#!/usr/bin/env python3
"""Validate the studio: python3 tools/validate.py [--strict]
- every scene/shot/character/manifest file against schema/*.schema.json (a small JSON-Schema subset, standard library only)
- scene.shots matches the shot folders; shot.scene/id match their path; unit statuses are known; a 'done' talking unit has a take
- every r2: reference names an object listed in a manifest (warning; error with --strict)
- public-text rules: no word from the editorial list (kept as hashes), no secrets, every file under 400 KB
CI runs this on every push. Exit 1 on any error. — Tab agent, 31 Oct 2026"""
import json, os, re, sys, hashlib, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent; STRICT = '--strict' in sys.argv
SCH = {p.stem.split('.')[0]: json.loads(p.read_text()) for p in (ROOT / 'schema').glob('*.schema.json')}
BANNED = set(["2961a6d1c8dcd624", "4b8ab7189b9addb1", "823d95a9a728f14d", "8753d1703f15ada9", "97b7e2db799e2b79", "a61808fe40feb8b3", "b5e91c059fd73705", "d79d3458a58877cd", "dd1b3c312cf7d816", "e5ac58aa0bcf6c64", "e828475612652415", "f02b95ed0b00ce45", "f514ae60147922b9"])
SECRET = re.compile(r'(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[bap]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY|"(?:STUDIO_KEY|INGEST|token|api_key|apiKey|secret)"\s*:\s*"[^"]{16,}"|Bearer [A-Za-z0-9._-]{24,})')
errors, warns = [], []
def err(m): errors.append(m)
TYPES = {'object': dict, 'array': list, 'string': str, 'integer': int, 'number': (int, float), 'boolean': bool}
def check(v, s, path):
    if 'enum' in s and v not in s['enum']: err(f'{path}: {v!r} not in {s["enum"]}'); return
    t = s.get('type')
    if t and not isinstance(v, TYPES[t]): err(f'{path}: want {t}'); return
    if 'pattern' in s and isinstance(v, str) and not re.match(s['pattern'], v): err(f'{path}: {v!r} does not match {s["pattern"]}')
    if isinstance(v, dict):
        for r in s.get('required', []):
            if r not in v: err(f'{path}: missing {r}')
        for k, sub in s.get('properties', {}).items():
            if k in v: check(v[k], sub, f'{path}.{k}')
        if isinstance(s.get('additionalProperties'), dict):
            for k, x in v.items():
                if k not in s.get('properties', {}): check(x, s['additionalProperties'], f'{path}.{k}')
    if isinstance(v, list) and 'items' in s:
        for i, x in enumerate(v): check(x, s['items'], f'{path}[{i}]')
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: err(f'{p}: not JSON ({e})'); return None
objects = {}
for mp in list((ROOT / 'studio').glob('scenes/*/manifest.json')) + [ROOT / 'studio' / 'manifest-shared.json']:
    if mp.exists():
        m = load(mp)
        if m: check(m, SCH['manifest'], str(mp.relative_to(ROOT))); objects.update(m.get('objects', {}))
for cp in (ROOT / 'studio' / 'characters').glob('*/character.json'):
    c = load(cp)
    if c:
        check(c, SCH['character'], str(cp.relative_to(ROOT)))
        if c.get('id') != cp.parent.name: err(f'{cp}: id {c.get("id")} != folder')
for sp in sorted((ROOT / 'studio' / 'scenes').glob('*/scene.json')):
    sc = load(sp)
    if not sc: continue
    rel = str(sp.relative_to(ROOT)); check(sc, SCH['scene'], rel)
    if sc.get('id') != sp.parent.name: err(f'{rel}: id != folder')
    have = sorted(d.name for d in (sp.parent / 'shots').iterdir()) if (sp.parent / 'shots').exists() else []
    if sorted(sc.get('shots', [])) != have: err(f'{rel}: shots list {sc.get("shots")} != folders {have}')
    for shid in sc.get('shots', []):
        pp = sp.parent / 'shots' / shid / 'shot.json'; sh = load(pp) if pp.exists() else None
        if not sh: err(f'{pp}: missing'); continue
        r2 = str(pp.relative_to(ROOT)); check(sh, SCH['shot'], r2)
        if sh.get('scene') != sc.get('id') or sh.get('id') != shid: err(f'{r2}: scene/id do not match the path')
        r = sh.get('render', {}); us = list((r.get('per_language') or {}).items()) or ([('shared', r['shared'])] if 'shared' in r else [])
        if not us: err(f'{r2}: no render units')
        for name, u in us:
            check(u, SCH['unit'], f'{r2}.render.{name}')
            if sh.get('type') == 'talking' and u.get('status') == 'done' and not u.get('take'): err(f'{r2}: {name} done without a take')
for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.parts: continue
    rel = str(p.relative_to(ROOT))
    if p.stat().st_size > 400 * 1024: err(f'{rel}: over 400 KB (big media goes to R2)')
    if p.suffix not in ('.json', '.md', '.py', '.yml', '.yaml', '.txt', '.jsonl', ''): continue
    t = p.read_text(encoding='utf-8', errors='replace')
    if SECRET.search(t): err(f'{rel}: looks like a secret')
    for ref in re.findall(r'r2:(studio/[A-Za-z0-9._\-/]+)', t):
        if ref not in objects and not ref.endswith('/'): (errors if STRICT else warns).append(f'{rel}: r2:{ref} not in any manifest')
    if rel.startswith('tools/validate.py'): continue
    words = re.findall(r"[a-záéíóúŵŷâêîôûäëïöü']+", t.lower())
    for i, w in enumerate(words):
        for cand in (w, w + ' ' + (words[i + 1] if i + 1 < len(words) else '')):
            if hashlib.sha256(cand.encode()).hexdigest()[:16] in BANNED: err(f'{rel}: editorial word list hit near word {i} ("{cand[:2]}…")')
for w in warns[:50]: print('warn', w)
if len(warns) > 50: print(f'warn … {len(warns) - 50} more')
for e in errors: print('ERROR', e)
print(json.dumps({'errors': len(errors), 'warnings': len(warns)}))
sys.exit(1 if errors else 0)

#!/usr/bin/env python3
"""cedwyn-studios shared library: packages, the work queue, the media store (R2) and the render manifest.
Standard library + requests only. Every tool imports this. — Tab agent, 31 Oct 2026"""
import json, os, sys, time, hashlib, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
STUDIO = ROOT / 'studio'
LANGS = ('cy', 'en', 'es')
DONE = {'done', 'superseded'}
STORE_URL = os.environ.get('CEDWYN_STUDIO_URL', 'https://cedwyn-studios-media.righteous.workers.dev')

def jload(p):
    return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
def jsave(p, obj):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
def now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()
def canon_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# ---------- packages ----------
def scene_path(sid): return STUDIO / 'scenes' / sid / 'scene.json'
def shot_path(sid, shid): return STUDIO / 'scenes' / sid / 'shots' / shid / 'shot.json'
def load_scene(sid): return jload(scene_path(sid))
def load_shot(sid, shid): return jload(shot_path(sid, shid))
def save_shot(sh): jsave(shot_path(sh['scene'], sh['id']), sh)
def scene_order():
    q = jload(STUDIO / 'queue' / 'queue.json'); order = list(q['order'])
    for d in sorted((STUDIO / 'scenes').iterdir()):
        if d.name not in order and (d / 'scene.json').exists(): order.append(d.name)
    return order, set(q.get('skip_status', []))
def units(sh):
    """(unit_name, unit) pairs: one per language for talking shots, one 'shared' unit otherwise"""
    r = sh.get('render', {})
    if 'per_language' in r: return [(lg, r['per_language'][lg]) for lg in LANGS if lg in r['per_language']]
    if 'shared' in r: return [('shared', r['shared'])]
    return []
def shot_status(sh):
    st = {u['status'] for _, u in units(sh)}
    if st and st <= {'done'}: return 'done'
    if st and st <= DONE: return 'superseded' if 'superseded' in st else 'done'
    if 'blocked' in st: return 'blocked'
    if st & {'rendered', 'prepared', 'done'}: return 'in_progress'
    return 'todo'
def step_for(sh, name, u):
    """the next concrete step for this unit, or None when it is done"""
    if u.get('status') in DONE: return None
    if u.get('status') == 'rendered': return 'qa'
    t = sh['type']
    if t == 'talking':
        if not (sh.get('still') or {}).get('image'): return 'still'
        if not u.get('audio'): return 'line'
        return 'take'
    if t == 'still-move':
        return 'move' if (sh.get('still') or {}).get('image') else 'still'
    if t == 'i2v':
        return 'i2v' if (sh.get('still') or {}).get('image') else 'still'
    return 'card'
def next_unit(lang=None, scene=None):
    """scene by scene (queue order); inside a scene, shared units first, then one language at a time in the scene's
    language_order (default cy, en, es), shots in order. Blocked units are skipped (blocked_by explains why)."""
    order, skip = scene_order()
    for sid in order:
        if scene and sid != scene: continue
        sc = load_scene(sid)
        if sc.get('status') in skip: continue
        shots = [load_shot(sid, x) for x in sc['shots']]
        for want in ['shared'] + list(sc.get('language_order') or LANGS):
            if lang and want not in (lang, 'shared'): continue
            for sh in shots:
                for name, u in units(sh):
                    if name != want or u.get('status') == 'blocked': continue
                    st = step_for(sh, name, u)
                    if st: return {'scene': sid, 'shot': sh['id'], 'unit': name, 'step': st, 'type': sh['type'], 'status': u.get('status')}
    return None

# ---------- manifest ----------
def manifest_path(sid): return STUDIO / 'scenes' / sid / 'manifest.json' if sid != '_shared' else STUDIO / 'manifest-shared.json'
def load_manifest(sid):
    p = manifest_path(sid)
    return jload(p) if p.exists() else {'schema': 'cedwyn-studios/manifest@1', 'scene': sid, 'store': 'r2:cedwyn-studios', 'objects': {}, 'renders': []}
def record_object(sid, key, sha, size, ctype, origin=None):
    m = load_manifest(sid); m['objects'][key] = {'sha256': sha, 'bytes': size, 'content_type': ctype, 'origin': origin, 'at': now()}
    jsave(manifest_path(sid), m); return m
def record_render(sid, row):
    m = load_manifest(sid); m['renders'].append(row); jsave(manifest_path(sid), m); return m
def find_render(sid, input_sha):
    for row in reversed(load_manifest(sid)['renders']):
        if row.get('input_sha256') == input_sha and row.get('output_key'): return row
    return None
def obj_sha(key):
    sid = key.split('/')[2] if key.startswith('studio/scenes/') else '_shared'
    o = load_manifest(sid)['objects'].get(key) or load_manifest('_shared')['objects'].get(key)
    return (o or {}).get('sha256')

# ---------- spend ledger (in git, so every computer sees the same day total) ----------
LEDGER = STUDIO / 'ledger' / 'spend.jsonl'
def day_spent(day=None):
    day = day or datetime.datetime.utcnow().strftime('%Y-%m-%d'); tot = 0.0
    files = [LEDGER] + [pathlib.Path(p) for p in os.environ.get('CEDWYN_EXTRA_SPEND', '').split(':') if p]
    for f in files:
        if not f.exists(): continue
        for l in f.read_text().splitlines():
            try: r = json.loads(l)
            except Exception: continue
            t = r.get('at')
            if isinstance(t, (int, float)): t = datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d')
            if str(t)[:10] == day: tot += float(r.get('usd') or 0)
    return round(tot, 3)
def add_spend(row):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, 'a') as f: f.write(json.dumps(row, ensure_ascii=False) + '\n')

# ---------- media store ----------
def store_key():
    k = os.environ.get('CEDWYN_STUDIO_KEY')
    if k: return k
    for p in (pathlib.Path.home() / '.config' / 'cedwyn-studios' / 'key.json', pathlib.Path('/home/user/tab/work/cedwyn-studios-private/secrets/studio_key.json')):
        if p.exists(): return json.loads(p.read_text())['STUDIO_KEY']
    sys.exit('no media key: set CEDWYN_STUDIO_KEY (ask the studio owner) — see STUDIO.md "Media store"')
def r2key(ref):
    return ref[3:] if ref and ref.startswith('r2:') else ref
class Store:
    def __init__(self):
        import requests; self.rq = requests; self.h = {'x-studio-key': store_key()}
    def put(self, local, key, ctype='application/octet-stream'):
        sha = sha256_file(local); size = os.path.getsize(local)
        with open(local, 'rb') as f:
            r = self.rq.put(f'{STORE_URL}/o/{key}', data=f, headers={**self.h, 'x-sha256': sha, 'content-type': ctype, 'content-length': str(size)}, timeout=900)
        r.raise_for_status(); return sha, size
    def head(self, key):
        r = self.rq.head(f'{STORE_URL}/o/{key}', headers=self.h, timeout=60)
        return None if r.status_code != 200 else {'bytes': int(r.headers.get('content-length', 0)), 'sha256': r.headers.get('x-sha256')}
    def get(self, key, dst, want_sha=None):
        with self.rq.get(f'{STORE_URL}/o/{key}', headers=self.h, timeout=900, stream=True) as r:
            r.raise_for_status()
            with open(dst, 'wb') as f:
                for c in r.iter_content(1 << 20): f.write(c)
        if want_sha and sha256_file(dst) != want_sha: raise SystemExit(f'sha256 mismatch on {key}')
        return dst
    def sign(self, key, ttl=3600):
        r = self.rq.post(f'{STORE_URL}/sign', json={'key': key, 'ttl': ttl}, headers=self.h, timeout=60); r.raise_for_status(); return r.json()['url']

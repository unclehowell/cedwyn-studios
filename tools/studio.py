#!/usr/bin/env python3
"""cedwyn-studios shared library: packages, the work queue, the media store and the render manifest.
Media store (31 Oct 2026): GitHub Releases first (tools/media_releases.py; public read, no key), the R2 Worker only as an
optional mirror, and the staging bridge for computers without a GitHub token (the media-releases workflow copies it on).
Standard library + requests only. Every tool imports this. — Tab agent, 31 Oct 2026 (store change — Sion's Tab agent)"""
import json, os, sys, time, hashlib, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
STUDIO = ROOT / 'studio'
LANGS = ('cy', 'en', 'es')
DONE = {'done', 'superseded'}
STORE_URL = os.environ.get('CEDWYN_STUDIO_URL', 'https://cedwyn-studios-media.righteous.workers.dev')
sys.path.insert(0, str(ROOT / 'tools'))
import media_releases as MR, ipfs_cid

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
    return jload(p) if p.exists() else {'schema': 'cedwyn-studios/manifest@1', 'scene': sid, 'store': 'github-releases', 'mirror': 'r2:cedwyn-studios', 'objects': {}, 'renders': []}
def record_object(sid, key, sha, size, ctype, origin=None, extra=None):
    m = load_manifest(sid); m['objects'][key] = {'sha256': sha, 'bytes': size, 'content_type': ctype, 'origin': origin, 'at': now(), **(extra or {})}
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
def store_key(required=True):
    """the R2 mirror's key (optional since 31 Oct 2026: reads come from GitHub Releases without one)"""
    k = os.environ.get('CEDWYN_STUDIO_KEY')
    if k: return k
    for p in (pathlib.Path.home() / '.config' / 'cedwyn-studios' / 'key.json', pathlib.Path('/home/user/tab/work/cedwyn-studios-private/secrets/studio_key.json')):
        if p.exists(): return json.loads(p.read_text())['STUDIO_KEY']
    if required: sys.exit('no mirror key and no GitHub token: set GH_TOKEN (contents:write on the repo) or CEDWYN_STUDIO_KEY — see STUDIO.md "Media store"')
    return None
def r2key(ref):
    return ref[3:] if ref and ref.startswith('r2:') else ref
class Store:
    """put: GitHub Releases first when a GitHub token is present (CEDWYN_R2_MIRROR=1 also writes the R2 mirror); without a
    token the file is staged on the R2 mirror and recorded release_state 'pending' — the media-releases workflow copies it
    to its release when the manifest is pushed. get/sign: the public release asset first, the mirror as fallback.
    After put, self.last holds the manifest fields (release, asset, github, cid, release_state, mirrors) for record_object."""
    def __init__(self):
        import requests; self.rq = requests; self.last = {}
        k = store_key(required=False); self.h = {'x-studio-key': k} if k else None
    def _mirror_put(self, local, key, ctype, sha, size):
        with open(local, 'rb') as f:
            r = self.rq.put(f'{STORE_URL}/o/{key}', data=f, headers={**self.h, 'x-sha256': sha, 'content-type': ctype, 'content-length': str(size)}, timeout=900)
        r.raise_for_status()
    def put(self, local, key, ctype='application/octet-stream'):
        sha = sha256_file(local); size = os.path.getsize(local)
        extra = {'release': MR.tag_for(key), 'asset': MR.asset_for(key), 'github': MR.url_for(key), 'cid': ipfs_cid.cid_of_file(local)}
        if MR.have_token():
            extra.update(MR.publish(local, key, ctype, sha))
            if self.h and os.environ.get('CEDWYN_R2_MIRROR') == '1': self._mirror_put(local, key, ctype, sha, size); extra['mirrors'] = ['r2:cedwyn-studios']
        else:
            if not self.h: store_key(required=True)
            self._mirror_put(local, key, ctype, sha, size); extra.update(release_state='pending', mirrors=['r2:cedwyn-studios'])
        self.last = extra; return sha, size
    def head(self, key):
        r = self.rq.head(MR.url_for(key), allow_redirects=True, timeout=60)
        if r.status_code == 200: return {'bytes': int(r.headers.get('content-length', 0)), 'sha256': obj_sha(key), 'from': 'github'}
        if not self.h: return None
        r = self.rq.head(f'{STORE_URL}/o/{key}', headers=self.h, timeout=60)
        return None if r.status_code != 200 else {'bytes': int(r.headers.get('content-length', 0)), 'sha256': r.headers.get('x-sha256'), 'from': 'r2'}
    def get(self, key, dst, want_sha=None):
        srcs = [(MR.url_for(key), {})] + ([(f'{STORE_URL}/o/{key}', self.h)] if self.h else [])
        for url, h in srcs:
            try:
                with self.rq.get(url, headers=h, timeout=900, stream=True) as r:
                    r.raise_for_status()
                    with open(dst, 'wb') as f:
                        for c in r.iter_content(1 << 20): f.write(c)
            except Exception:
                continue
            if want_sha and sha256_file(dst) != want_sha: continue
            return dst
        raise SystemExit(f'could not fetch {key} (release asset or mirror), or its sha256 did not match')
    def sign(self, key, ttl=3600):
        """a URL a render vendor can fetch: the public release asset when it is there, else a time-limited mirror link"""
        r = self.rq.head(MR.url_for(key), allow_redirects=True, timeout=60)
        if r.status_code == 200: return MR.url_for(key)
        if not self.h: store_key(required=True)
        r = self.rq.post(f'{STORE_URL}/sign', json={'key': key, 'ttl': ttl}, headers=self.h, timeout=60); r.raise_for_status(); return r.json()['url']

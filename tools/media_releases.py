#!/usr/bin/env python3
"""GitHub Releases media store for cedwyn-studios (the PRIMARY store since 31 Oct 2026; R2 is an optional mirror).
One release per scene holds that scene's media as release assets: tag media-F###; characters, sets, chronology and
voice-lab live in media-shared. An asset's name is its studio key below the scene/studio folder with '/' -> '__'
(studio/scenes/F002/shots/S02/takes/en/x.mp4 -> media-F002 / shots__S02__takes__en__x.mp4), so every key maps to one
public URL: https://github.com/<repo>/releases/download/<tag>/<asset>. Media never goes into git (400 KB rule).
Standard library only. Token: GH_TOKEN or GITHUB_TOKEN with contents:write (the Actions token in CI; a person's own
token or `gh auth token` on other computers). Never print it.
  python3 tools/media_releases.py publish <file> <key> [content-type]   upload one file (skips if the same bytes are there)
  python3 tools/media_releases.py copy [--only <prefix>] [--out index.json]  CI: copy every manifest object from the R2
        mirror to Releases, one file at a time (sha256 checked, CID computed, temp file deleted), and write the index
  python3 tools/media_releases.py apply <index.json>     merge an index into the manifests (then commit them)
  python3 tools/media_releases.py url <key>             print the public asset URL
— Sion's Tab agent, 31 Oct 2026"""
import hashlib, json, os, pathlib, re, subprocess, sys, tempfile, time, urllib.error, urllib.parse, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import ipfs_cid
REPO = os.environ.get('CEDWYN_STUDIOS_REPO', 'unclehowell/cedwyn-studios')
API = 'https://api.github.com'

def tag_for(key):
    p = key.split('/')
    return f'media-{p[2]}' if key.startswith('studio/scenes/') and len(p) > 3 else 'media-shared'
def asset_for(key):
    p = key.split('/'); rest = p[3:] if tag_for(key) != 'media-shared' else p[1:]
    return re.sub(r'[^A-Za-z0-9._-]', '.', '__'.join(rest))
def url_for(key):
    return f'https://github.com/{REPO}/releases/download/{tag_for(key)}/{asset_for(key)}'
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def _token():
    t = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not t:
        try: t = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception: t = ''
    return t or None
def have_token(): return bool(_token())
def _req(method, url, body=None, data=None, headers=None, timeout=120):
    h = {'Authorization': 'Bearer ' + (_token() or ''), 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', **(headers or {})}
    if body is not None: data = json.dumps(body).encode(); h['Content-Type'] = 'application/json'
    for attempt in range(5):
        try:
            if hasattr(data, 'seek'): data.seek(0)
            with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=h), timeout=timeout) as r:
                raw = r.read(); return r.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 504) and attempt < 4: time.sleep(5 * (attempt + 1)); continue
            return e.code, (e.read()[:500].decode('utf-8', 'replace'))
        except (urllib.error.URLError, TimeoutError):
            if attempt < 4: time.sleep(5 * (attempt + 1)); continue
            raise

_rel = {}
def release(tag):
    """the release for a tag (created, published, not marked latest, if missing) with its assets {name: asset}"""
    if tag in _rel: return _rel[tag]
    st, r = _req('GET', f'{API}/repos/{REPO}/releases/tags/{tag}')
    if st == 404:
        st, r = _req('POST', f'{API}/repos/{REPO}/releases', {'tag_name': tag, 'name': f'Studio media {tag[6:]}', 'make_latest': 'false',
            'body': f'Media store for {tag[6:]} (clips, stills, audio). Keys and sha256 are listed in the studio manifests; see STUDIO.md "Media store".'})
    if st not in (200, 201): sys.exit(f'release {tag}: HTTP {st} {r}')
    assets, page = {}, 1
    while True:
        st, a = _req('GET', f'{API}/repos/{REPO}/releases/{r["id"]}/assets?per_page=100&page={page}')
        if st != 200 or not a: break
        assets.update({x['name']: x for x in a}); page += 1
    _rel[tag] = {'id': r['id'], 'assets': assets}; return _rel[tag]

def publish(local, key, ctype='application/octet-stream', sha=None):
    """upload one file as the key's asset; same bytes already there -> skip. Returns the manifest fields."""
    sha = sha or sha256_file(local); tag, name = tag_for(key), asset_for(key); rel = release(tag); old = rel['assets'].get(name)
    if old and (old.get('digest') or '') == 'sha256:' + sha: state = 'verified'
    else:
        if old: _req('DELETE', f'{API}/repos/{REPO}/releases/assets/{old["id"]}')
        size = os.path.getsize(local)
        with open(local, 'rb') as f:
            st, a = _req('POST', f'https://uploads.github.com/repos/{REPO}/releases/{rel["id"]}/assets?name={urllib.parse.quote(name)}',
                         data=f, headers={'Content-Type': ctype, 'Content-Length': str(size)}, timeout=1800)
        if st != 201: sys.exit(f'upload {key}: HTTP {st} {a}')
        if a.get('digest') and a['digest'] != 'sha256:' + sha: sys.exit(f'upload {key}: GitHub digest {a["digest"]} != {sha}')
        rel['assets'][name] = a; state = 'verified' if a.get('digest') else 'uploaded'
    return {'release': tag, 'asset': name, 'github': url_for(key), 'release_state': state, 'cid': ipfs_cid.cid_of_file(local)}

def _manifests():
    return sorted((ROOT / 'studio').glob('scenes/*/manifest.json')) + [ROOT / 'studio' / 'manifest-shared.json']

def copy(only='', out='media-index.json'):
    """CI job: R2 mirror -> Releases, one object at a time. Needs CEDWYN_STUDIO_KEY (repo secret) for the mirror."""
    store = os.environ.get('CEDWYN_STUDIO_URL', 'https://cedwyn-studios-media.righteous.workers.dev'); k = os.environ['CEDWYN_STUDIO_KEY']
    ipfs = os.environ.get('IPFS_BIN'); ipfs = ipfs if ipfs and os.path.exists(ipfs) else None
    idx = json.loads(pathlib.Path(out).read_text()) if pathlib.Path(out).exists() else {}
    todo = []
    for mp in _manifests():
        for key, o in json.loads(mp.read_text())['objects'].items():
            if key.startswith(only) and '?' not in key: todo.append((key, o))
    print(f'{len(todo)} objects'); n_ok = n_skip = 0; total = 0
    for i, (key, o) in enumerate(todo, 1):
        tag, name = tag_for(key), asset_for(key); rel = release(tag); old = rel['assets'].get(name)
        if old and old.get('digest') == 'sha256:' + o['sha256'] and key in idx and idx[key].get('cid'):
            n_skip += 1; total += o['bytes']; continue
        fd, tmp = tempfile.mkstemp(prefix='media_'); os.close(fd)
        try:
            rq = urllib.request.Request(f'{store}/o/' + urllib.parse.quote(key), headers={'x-studio-key': k})
            with urllib.request.urlopen(rq, timeout=900) as r, open(tmp, 'wb') as f:
                for c in iter(lambda: r.read(1 << 20), b''): f.write(c)
            sha = sha256_file(tmp)
            if sha != o['sha256']: print(f'MISMATCH {key}: mirror {sha} != manifest {o["sha256"]}'); idx[key] = {'error': 'sha256 mismatch'}; continue
            row = publish(tmp, key, o.get('content_type') or 'application/octet-stream', sha)
            if ipfs:
                kubo = subprocess.run([ipfs, 'add', '-Q', '--only-hash', '--cid-version=1', tmp], capture_output=True, text=True).stdout.strip()
                if kubo == row['cid']: row['cid_check'] = 'kubo-match'
                elif kubo.startswith('baf'): row['cid_check'] = 'kubo-used (python gave ' + row['cid'] + ')'; row['cid'] = kubo
            idx[key] = {**row, 'sha256': sha, 'bytes': o['bytes']}; n_ok += 1; total += o['bytes']
            print(f'[{i}/{len(todo)}] {tag}/{name} {o["bytes"]} {row["release_state"]} {row["cid"][:16]}… {row.get("cid_check", "")}')
        finally:
            os.unlink(tmp)
        pathlib.Path(out).write_text(json.dumps(idx, indent=1, sort_keys=True) + '\n')
    pathlib.Path(out).write_text(json.dumps(idx, indent=1, sort_keys=True) + '\n')
    bad = [k for k, v in idx.items() if v.get('error') or str(v.get('cid_check', '')).startswith('kubo-differs')]
    print(json.dumps({'copied': n_ok, 'already_there': n_skip, 'bytes': total, 'problems': bad[:20]}))
    return 1 if bad else 0

def apply(index_path):
    idx = json.loads(pathlib.Path(index_path).read_text()); changed = []
    for mp in _manifests():
        m = json.loads(mp.read_text()); hit = False
        for key, o in m['objects'].items():
            r = idx.get(key)
            if r and not r.get('error') and r.get('sha256') == o['sha256']:
                for f in ('release', 'asset', 'github', 'release_state', 'cid', 'cid_check'):
                    if r.get(f) and o.get(f) != r[f]: o[f] = r[f]; hit = True
                if o.get('mirrors') != ['r2:cedwyn-studios']: o['mirrors'] = ['r2:cedwyn-studios']; hit = True
        if m.get('store') != 'github-releases':
            m['store'] = 'github-releases'; m['mirror'] = 'r2:cedwyn-studios'; hit = True
        if hit: mp.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n'); changed.append(str(mp.relative_to(ROOT)))
    print(json.dumps({'manifests_changed': changed}))

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == 'publish': print(json.dumps(publish(a[1], a[2], a[3] if len(a) > 3 else 'application/octet-stream'), indent=1))
    elif a[0] == 'copy':
        only = a[a.index('--only') + 1] if '--only' in a else ''; out = a[a.index('--out') + 1] if '--out' in a else 'media-index.json'
        sys.exit(copy(only, out))
    elif a[0] == 'apply': apply(a[1])
    elif a[0] == 'url': print(url_for(a[1]))
    else: sys.exit(__doc__)

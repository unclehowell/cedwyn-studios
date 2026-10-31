#!/usr/bin/env python3
"""Commit studio changes from a Tab box (no git push credentials needed): uses the box's GitHub helper
(work/site-flywheels/tools/gh.py, the connected GitHub account) with at most 4 files per commit, each under 400 KB,
no force-push, and validate.py first. Other computers: use plain git (same rules).
Usage: TAB_TASK_ID=<task> python3 tools/tab_commit.py "<message>" <path> [<path> ...]   (paths relative to the repo root)
The message gets the agent signature appended if missing. — Tab agent, 31 Oct 2026"""
import sys, os, subprocess, json, time, base64, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent; REPO = os.environ.get('CEDWYN_STUDIOS_REPO', 'unclehowell/cedwyn-studios'); BR = os.environ.get('CEDWYN_STUDIOS_BRANCH', 'main')
sys.path.insert(0, '/home/user/tab/work/site-flywheels/tools'); import gh as G
SIG = os.environ.get('CEDWYN_COMMIT_SIG', "— Tab agent")
msg, paths = sys.argv[1], sys.argv[2:]
if not msg.rstrip().endswith(SIG): msg = msg.rstrip() + ' ' + SIG
v = subprocess.run([sys.executable, str(ROOT / 'tools' / 'validate.py')], capture_output=True, text=True)
if v.returncode: sys.exit('validate.py failed:\n' + v.stdout[-2000:])
for i in range(0, len(paths), 4):
    batch = paths[i:i + 4]
    for attempt in range(4):
        st, ref = G.gh('GET', f'/repos/{REPO}/git/ref/heads/{BR}'); head = ref['object']['sha']
        st, hc = G.gh('GET', f'/repos/{REPO}/git/commits/{head}'); items = []
        for p in batch:
            fp = ROOT / p
            if fp.exists():
                assert fp.stat().st_size < 400 * 1024, p + ' is over 400 KB'
                items.append({'path': p, 'mode': '100644', 'type': 'blob', 'content': fp.read_text(encoding='utf-8')})
            else: items.append({'path': p, 'mode': '100644', 'type': 'blob', 'sha': None})
        st, t = G.gh('POST', f'/repos/{REPO}/git/trees', {'base_tree': hc['tree']['sha'], 'tree': items})
        m = msg if len(paths) <= 4 else f'{msg} ({i // 4 + 1}/{-(-len(paths) // 4)})'
        st, c = G.gh('POST', f'/repos/{REPO}/git/commits', {'message': m, 'tree': t['sha'], 'parents': [head]})
        st, u = G.gh('PATCH', f'/repos/{REPO}/git/refs/heads/{BR}', {'sha': c['sha'], 'force': False})
        if st == 200: print(json.dumps({'commit': c['sha'][:7], 'files': batch})); break
        time.sleep(5)
    else: sys.exit('could not fast-forward ' + BR)

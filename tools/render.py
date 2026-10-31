#!/usr/bin/env python3
"""Render one unit of one shot. Resumable and idempotent: a unit whose inputs hash to an output already in the manifest
(and present in the store) is marked done and skipped, never paid for twice.
Usage:
  python3 tools/render.py next [--lang en] [--scene F002] [--dry] [--cap 9.6] [--day-limit 10]
  python3 tools/render.py F002/S03 --lang en [--dry] [--cap ..] [--day-limit ..]
  python3 tools/render.py adopt F002/S03 --lang en --file take.mp4 [--usd 0.84] [--request-id ID] [--prompt-file p.txt]
  python3 tools/render.py adopt F002/S03 --step still --file still.jpg [--prompt "..."]
  python3 tools/render.py qa F002/S03 --lang en --verdict PASS|FAIL --notes "what you saw"
Steps it runs itself: take (OmniHuman 2.0, paid), line (ElevenLabs eleven_v4, paid, small), move (ffmpeg still-move, free).
Steps it hands back: still, i2v, card (generate with the models in docs/MODELS.md, then `adopt`).
Paid keys: on a Tab box the vendor door (/home/user/tab/.vendor-capability.json); elsewhere FAL_KEY / ELEVENLABS_API_KEY.
After any change: commit the touched studio/ files (git, or tools/tab_commit.py on a Tab box). — Tab agent, 31 Oct 2026"""
import json, os, sys, time, subprocess, tempfile, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import studio as S
A = sys.argv[1:]
def opt(n, d=None, t=str): return t(A[A.index(n) + 1]) if n in A else d
DRY = '--dry' in A; CAP = opt('--cap', 9.6, float); DAY = opt('--day-limit', 10.0, float)
VC_P = pathlib.Path('/home/user/tab/.vendor-capability.json')
def vendor():
    import requests
    if VC_P.exists():
        vc = json.loads(VC_P.read_text())
        return requests, vc['base_url'], {'Authorization': 'Bearer ' + vc['token'], 'x-tab-task': os.environ.get('TAB_TASK_ID', ''), 'content-type': 'application/json'}, 'door'
    return requests, None, {}, 'direct'
def touched(*paths): print(json.dumps({'touched': [str(pathlib.Path(p).relative_to(S.ROOT)) for p in paths]}))
def ff(*a, t=900): subprocess.run(['timeout', '-k', '5', str(t), 'ffmpeg', '-v', 'error', '-y', *a], check=True)

def guard(est):
    ds = S.day_spent()
    if ds + est > DAY: sys.exit(f'STOP: day spend {ds} + {est} > {DAY} (studio/ledger/spend.jsonl)')
    if est > CAP: sys.exit(f'STOP: this render {est} > cap {CAP}')

def omnihuman(image_url, audio_url, prompt):
    rq, B, H, mode = vendor(); MODEL = 'bytedance/omnihuman/v2'
    if mode == 'door':
        sub = f'{B}/fal-queue/{MODEL}'; base = f'{B}/fal-queue/bytedance/omnihuman/requests/'
    else:
        key = os.environ.get('FAL_KEY') or sys.exit('no FAL_KEY and no Tab vendor door on this computer')
        H = {'Authorization': 'Key ' + key, 'content-type': 'application/json'}; sub = f'https://queue.fal.run/{MODEL}'; base = 'https://queue.fal.run/bytedance/omnihuman/requests/'
    r = rq.post(sub, headers=H, json={'image_url': image_url, 'audio_url': audio_url, 'prompt': prompt}, timeout=120); r.raise_for_status(); rid = r.json()['request_id']
    print('submitted', rid, flush=True); t0 = time.time(); st = None
    while time.time() - t0 < 1500:
        time.sleep(15)
        try: st = rq.get(base + rid + '/status', headers=H, timeout=60).json().get('status')
        except Exception as e: print('status err', e); continue
        if st in ('COMPLETED', 'FAILED', 'ERROR'): break
    if st != 'COMPLETED': sys.exit(f'render {rid} ended {st}: not billed if it failed; check before retrying')
    return rid, rq.get(base + rid, headers=H, timeout=120).json()['video']['url']

def tts(voice, text, lang_code):
    rq, B, H, mode = vendor()
    body = {'text': text, 'model_id': voice.get('model_id', 'eleven_v4'), 'language_code': lang_code, 'voice_settings': voice.get('settings')}
    if mode == 'door': u = f"{B}/elevenlabs/v1/text-to-speech/{voice['voice_id']}?output_format=mp3_44100_64"
    else:
        u = f"https://api.elevenlabs.io/v1/text-to-speech/{voice['voice_id']}?output_format=mp3_44100_64"
        H = {'xi-api-key': os.environ.get('ELEVENLABS_API_KEY') or sys.exit('no ELEVENLABS_API_KEY'), 'content-type': 'application/json'}
    r = rq.post(u, headers=H, json=body, timeout=180); r.raise_for_status(); return r.content

def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True, timeout=60).stdout)

def put_output(st, sid, local, key, ctype, origin):
    sha, size = st.put(local, key, ctype); S.record_object(sid, key, sha, size, ctype, origin); return sha, size

def do_take(sh, lang):
    sid = sh['scene']; u = sh['render']['per_language'][lang]
    still = S.r2key(sh['still']['image']); audio = S.r2key(u['audio']); prompt = u['prompt']
    if not prompt or prompt.startswith('TODO'): sys.exit('write the prompt first (docs/QUALITY-BAR-v2.md rule 5)')
    ins = {'model': 'bytedance/omnihuman/v2', 'prompt': prompt, 'still': S.obj_sha(still), 'audio': S.obj_sha(audio)}
    if not ins['still'] or not ins['audio']: sys.exit(f'inputs not in the manifest: {still} / {audio}')
    h = S.canon_hash(ins); st = S.Store(); prev = S.find_render(sid, h)
    if prev and st.head(prev['output_key']):
        u.update(status='rendered' if u.get('status') != 'done' else 'done', take='r2:' + prev['output_key']); S.save_shot(sh)
        print('skip: output for these inputs exists', prev['output_key']); touched(S.shot_path(sid, sh['id'])); return
    est = round(-(-float(u.get('shot_s') or sh.get('seconds') or 8) // 1) * 0.105, 3); guard(est)
    if DRY: print('DRY take', sid, sh['id'], lang, 'est', est, 'input', h[:12]); return
    rid, url = omnihuman(st.sign(still), st.sign(audio), prompt)
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'take.mp4'); subprocess.run(['curl', '-sL', '--max-time', '300', '-o', out, url], check=True)
        secs = dur(out); usd = round(max(1, round(secs)) * 0.105, 3); sha = S.sha256_file(out)
        key = f"studio/scenes/{sid}/shots/{sh['id']}/takes/{lang}/{sha[:12]}.mp4"; put_output(st, sid, out, key, 'video/mp4', 'omnihuman ' + rid)
    S.record_render(sid, {'shot': sh['id'], 'unit': lang, 'step': 'take', 'model': ins['model'], 'input_sha256': h, 'inputs': ins, 'output_key': key, 'output_sha256': sha, 'seconds': secs, 'usd': usd, 'request_id': rid, 'at': S.now()})
    S.add_spend({'item': f'{sid} {sh["id"]} {lang} omnihuman', 'usd': usd, 'at': S.now(), 'request_id': rid})
    u.update(status='rendered', take='r2:' + key, request_id=rid, qa='todo'); S.save_shot(sh)
    print('rendered', key, secs, 's', usd, 'USD'); touched(S.shot_path(sid, sh['id']), S.manifest_path(sid), S.LEDGER)

def do_line(sh, lang):
    sid = sh['scene']; u = sh['render']['per_language'][lang]; who = sh.get('speaker')
    ch = S.jload(S.STUDIO / 'characters' / who / 'character.json'); v = ch.get('voice') or {}
    if not v.get('voice_id') or str(v.get('voice_id')).startswith('TODO') or str(u.get('voice', '')).startswith('TODO'):
        sys.exit(f'choose the voice for {who} in {lang} first (unit.voice); a new era means a new voice')
    text = u.get('text') or sys.exit('no line text for ' + lang)
    if DRY: print('DRY line', sid, sh['id'], lang, who, len(text), 'chars'); return
    guard(0.05)
    with tempfile.TemporaryDirectory() as td:
        mp3 = os.path.join(td, 'line.mp3'); open(mp3, 'wb').write(tts(v, text, lang)); sp = dur(mp3)
        shot_s = max(float(sh.get('seconds') or 0), round(sp + 1.2, 2)); adj = os.path.join(td, 'line.adj.wav')
        ff('-i', mp3, '-af', 'adelay=400:all=1,apad', '-t', f'{shot_s}', '-ar', '44100', adj)
        st = S.Store(); base = f"studio/scenes/{sid}/shots/{sh['id']}/lines/{lang}"
        put_output(st, sid, mp3, base + '.mp3', 'audio/mpeg', 'elevenlabs ' + v['voice_id']); put_output(st, sid, adj, base + '.adj.wav', 'audio/wav', 'lead 0.4 s, padded')
    S.add_spend({'item': f'{sid} {sh["id"]} {lang} line', 'usd': 0.02, 'at': S.now(), 'note': 'estimate'})
    u.update(status='prepared', line='r2:' + base + '.mp3', audio='r2:' + base + '.adj.wav', speech_s=round(sp, 3), shot_s=shot_s, transcribe_match='TODO: transcribe back (>= 0.8)')
    S.save_shot(sh); print('voiced', base, sp, 's'); touched(S.shot_path(sid, sh['id']), S.manifest_path(sid), S.LEDGER)

def do_move(sh):
    sid = sh['scene']; u = sh['render']['shared']; still = S.r2key(sh['still']['image']); secs = float(sh.get('seconds') or 8)
    ins = {'model': 'ffmpeg still-move v1', 'still': S.obj_sha(still), 'seconds': secs, 'move': u.get('move', 'push-in 1.00-1.08')}
    h = S.canon_hash(ins); st = S.Store(); prev = S.find_render(sid, h)
    if prev and st.head(prev['output_key']):
        u.update(status='rendered', clip='r2:' + prev['output_key']); S.save_shot(sh); print('skip: exists', prev['output_key']); return
    if DRY: print('DRY move', sid, sh['id'], secs); return
    with tempfile.TemporaryDirectory() as td:
        img = st.get(still, os.path.join(td, 'still' + os.path.splitext(still)[1]), ins['still']); out = os.path.join(td, 'move.mp4'); n = int(round(secs * 24))
        ff('-loop', '1', '-i', img, '-vf', f"scale=2560:1440:force_original_aspect_ratio=increase:flags=lanczos,crop=2560:1440,zoompan=z='1+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1280x720:fps=24,format=yuv420p",
           '-frames:v', str(n), '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', out)
        sha = S.sha256_file(out); key = f"studio/scenes/{sid}/shots/{sh['id']}/move/{sha[:12]}.mp4"; put_output(st, sid, out, key, 'video/mp4', 'ffmpeg still-move')
    S.record_render(sid, {'shot': sh['id'], 'unit': 'shared', 'step': 'move', 'model': ins['model'], 'input_sha256': h, 'inputs': ins, 'output_key': key, 'output_sha256': sha, 'usd': 0, 'at': S.now()})
    u.update(status='rendered', clip='r2:' + key); S.save_shot(sh); print('moved', key); touched(S.shot_path(sid, sh['id']), S.manifest_path(sid))

def adopt(sh, lang, step):
    sid = sh['scene']; f = opt('--file') or sys.exit('--file needed'); st = S.Store(); ext = os.path.splitext(f)[1].lower()
    sha = S.sha256_file(f); ct = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.mp4': 'video/mp4', '.wav': 'audio/wav', '.mp3': 'audio/mpeg'}.get(ext, 'application/octet-stream')
    if step == 'still':
        key = f"studio/scenes/{sid}/stills/{sh['id']}-{sha[:12]}{ext}"; put_output(st, sid, f, key, ct, 'adopted still')
        sh['still']['image'] = 'r2:' + key
        if opt('--prompt'): sh['still']['prompt'] = opt('--prompt')
    elif sh['type'] == 'talking':
        u = sh['render']['per_language'][lang]; key = f"studio/scenes/{sid}/shots/{sh['id']}/takes/{lang}/{sha[:12]}{ext}"; put_output(st, sid, f, key, ct, 'adopted take')
        prompt = open(opt('--prompt-file')).read().strip() if opt('--prompt-file') else u.get('prompt')
        ins = {'model': 'bytedance/omnihuman/v2', 'prompt': prompt, 'still': S.obj_sha(S.r2key(sh['still'].get('image') or '')), 'audio': S.obj_sha(S.r2key(u.get('audio') or ''))}
        S.record_render(sid, {'shot': sh['id'], 'unit': lang, 'step': 'take', 'model': ins['model'], 'input_sha256': S.canon_hash(ins), 'inputs': ins, 'output_key': key, 'output_sha256': sha, 'usd': opt('--usd', 0, float), 'request_id': opt('--request-id'), 'adopted': True, 'at': S.now()})
        u.update(status='rendered', take='r2:' + key, qa='todo')
        if opt('--request-id'): u['request_id'] = opt('--request-id')
    else:
        u = sh['render']['shared']; key = f"studio/scenes/{sid}/shots/{sh['id']}/{step or 'clip'}/{sha[:12]}{ext}"; put_output(st, sid, f, key, ct, 'adopted')
        u.update(status='rendered', clip='r2:' + key)
    S.save_shot(sh); print('adopted', key); touched(S.shot_path(sid, sh['id']), S.manifest_path(sid))

def qa(sh, lang):
    v = (opt('--verdict') or '').upper(); assert v in ('PASS', 'FAIL'), '--verdict PASS|FAIL'
    u = sh['render']['per_language'][lang] if lang in sh['render'].get('per_language', {}) else sh['render']['shared']
    u['qa'] = f"{v} {S.now()} {opt('--notes', '')}".strip(); u['status'] = 'done' if v == 'PASS' else 'todo'
    if v == 'FAIL': u.pop('take', None); u.pop('clip', None)
    sh['status'] = S.shot_status(sh); sh['qa'] = {'status': 'pass' if sh['status'] == 'done' else 'todo'}
    S.save_shot(sh); print('qa', sh['scene'], sh['id'], lang, v); touched(S.shot_path(sh['scene'], sh['id']))

def run_unit(sid, shid, lang):
    sh = S.load_shot(sid, shid); units = dict(S.units(sh)); name = lang if lang in units else 'shared'
    step = S.step_for(sh, name, units[name])
    if step is None: print('done already', sid, shid, name); return
    print(json.dumps({'scene': sid, 'shot': shid, 'unit': name, 'step': step}))
    if step == 'take': do_take(sh, name)
    elif step == 'line': do_line(sh, name)
    elif step == 'move': do_move(sh)
    elif step == 'qa': print('look at the take, then: tools/render.py qa', f'{sid}/{shid}', '--lang', name, '--verdict PASS|FAIL --notes "..."')
    else: print(f'step {step}: generate it with the model in docs/MODELS.md from shot.still.prompt / shot.direction, then: tools/render.py adopt {sid}/{shid} --step {step} --file <file>')

if not A: print(__doc__); sys.exit(0)
if A[0] == 'next':
    n = S.next_unit(opt('--lang'), opt('--scene'))
    if not n: print('nothing to do'); sys.exit(0)
    run_unit(n['scene'], n['shot'], n['unit'])
elif A[0] in ('adopt', 'qa'):
    sid, shid = A[1].split('/'); sh = S.load_shot(sid, shid)
    (adopt(sh, opt('--lang'), opt('--step')) if A[0] == 'adopt' else qa(sh, opt('--lang', 'shared')))
else:
    sid, shid = A[0].split('/'); run_unit(sid, shid, opt('--lang', 'shared'))

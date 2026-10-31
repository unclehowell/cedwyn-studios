#!/usr/bin/env python3
"""Assemble one scene in one language from its packages (Quality bar v2: 24 fps, lanczos 1280x720, two-pass VP9 filling
23.5 MB, Opus 128k, loudnorm I=-16 LRA=7 TP=-1.5, subtitles cy/en/es with this language first).
Usage: python3 tools/assemble.py F002 en [--plan] [--out /tmp/F002.en.webm] [--upload]
--plan prints the cut list and stops (no media). --upload stores the cut under studio/scenes/<id>/cuts/<lang>/ in the media
store (GitHub Releases first, release media-<id>; the R2 mirror only without a GitHub token, see studio.Store) and records it,
with its release asset URL and IPFS CID, in the scene manifest. Publishing to the site stays with RUNNER.md step 6. Ported from the Door 2 assembler.
Fonts: CEDWYN_FONT_TITLE / CEDWYN_FONT_TEXT (defaults: the box fonts, else DejaVu). — Tab agent, 31 Oct 2026"""
import json, os, sys, shutil, subprocess, tempfile, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import studio as S
A = sys.argv[1:]; sid, lang = A[0], A[1]; PLAN = '--plan' in A
out = A[A.index('--out') + 1] if '--out' in A else f'/tmp/{sid}.{lang}.webm'
VF = 'scale=1280:720:force_original_aspect_ratio=increase:flags=lanczos,crop=1280:720,fps=24,format=yuv420p,setsar=1'
def pick_font(env, *c):
    for p in [os.environ.get(env)] + list(c):
        if p and os.path.exists(p): return p
    return '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FT = pick_font('CEDWYN_FONT_TITLE', '/home/user/.fonts/PlayfairDisplay.ttf'); FX = pick_font('CEDWYN_FONT_TEXT', '/home/user/.local/share/fonts/SourceSerif4.ttf')
def ff(*a, t=900): subprocess.run(['timeout', '-k', '5', str(t), 'ffmpeg', '-v', 'error', '-y', *a], check=True)
sc = S.load_scene(sid); shots = [S.load_shot(sid, x) for x in sc['shots']]
cut = []; problems = []
for sh in shots:
    w = sh.get('published_window_v6') or []; win_s = round(w[1] - w[0], 3) if len(w) == 2 else None
    if sh['type'] == 'talking':
        u = sh['render']['per_language'].get(lang, {})
        d = float(u.get('shot_s') or sh.get('seconds') or 0)
        if u.get('status') != 'done' or not u.get('take'): problems.append(f"{sh['id']} {lang} take not done ({u.get('status')})")
        cut.append({'shot': sh['id'], 'kind': 'take', 'key': S.r2key(u.get('take')), 'seconds': d, 'audio': S.r2key(u.get('audio')) if lang != 'cy' or u.get('audio') else None,
                    'take_audio': lang == 'cy' and not u.get('audio'), 'lead': 0.4, 'speech_s': u.get('speech_s'),
                    'subs': {lg: (sh['render']['per_language'].get(lg, {}).get('text') or '') for lg in S.LANGS}})
    else:
        u = sh['render'].get('shared', {}); d = win_s or float(sh.get('seconds') or 0)
        if u.get('status') != 'done': problems.append(f"{sh['id']} shared not done ({u.get('status')})")
        if u.get('assemble_from'): cut.append({'shot': sh['id'], 'kind': 'published_window', 'window': w, 'seconds': d})
        else: cut.append({'shot': sh['id'], 'kind': 'source' if u.get('source') else 'clip', 'key': S.r2key(u.get('source') or u.get('clip')), 'seconds': d,
                          'source_seconds': u.get('source_seconds'), 'caption': (u.get('per_language_caption') or {}).get(lang)})
total = round(sum(c['seconds'] for c in cut), 3)
if PLAN or problems:
    print(json.dumps({'scene': sid, 'lang': lang, 'seconds': total, 'cut': cut, 'not_ready': problems}, ensure_ascii=False, indent=1))
    sys.exit(0 if PLAN else 2)
st = S.Store(); T = pathlib.Path(tempfile.mkdtemp(prefix=f'asm_{sid}_{lang}_'))
try:
    pub = None; segs = []; placed = []; cues = []; t = 0.0
    for i, c in enumerate(cut):
        seg = T / f'seg{i:02d}.mp4'; d = c['seconds']
        if c['kind'] == 'published_window':
            if pub is None:
                pub = T / 'published.webm'; src = 'https://raw.githubusercontent.com/' + sc['published']['repo'] + '/main/' + sc['published']['clip']
                subprocess.run(['curl', '-sL', '--max-time', '300', '-o', str(pub), src], check=True)
            ff('-ss', f"{c['window'][0]}", '-i', str(pub), '-t', f'{d}', '-an', '-vf', VF, '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', str(seg))
        else:
            src = st.get(c['key'], str(T / f'in{i:02d}.mp4'), S.obj_sha(c['key']))
            if c['kind'] == 'take':
                ff('-stream_loop', '-1', '-i', src, '-t', f'{d}', '-an', '-vf', VF, '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', str(seg))
                if c['take_audio']:
                    ff('-i', src, '-t', f'{d}', '-vn', '-ac', '2', '-ar', '48000', str(T / f'a{i:02d}.wav')); placed.append((t, T / f'a{i:02d}.wav'))
                elif c['audio']:
                    placed.append((t, st.get(c['audio'], str(T / f'a{i:02d}.wav'), S.obj_sha(c['audio']))))
                end = t + min(d, c['lead'] + float(c.get('speech_s') or d - 0.7) + 0.3)
                for lg, txt in c['subs'].items():
                    if txt: cues.append((lg, t + c['lead'], end, txt))
            else:
                k = (d / float(c['source_seconds'])) if c.get('source_seconds') else 1.0; vf = f'setpts={k:.4f}*PTS,{VF}'
                if c.get('caption'):
                    (T / f'cap{i}.txt').write_text(c['caption'])
                    vf += f",drawtext=fontfile={FX}:textfile={T}/cap{i}.txt:fontsize=19:fontcolor=0xDDDDDD:x=72:y=622:shadowcolor=black@0.6:shadowx=1:shadowy=1:alpha='if(lt(t,0.6),0,min(1,(t-0.6)/0.8))'"
                ff('-i', src, '-t', f'{d}', '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', str(seg))
        segs.append(seg); t += d
    (T / 'list.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
    ff('-f', 'concat', '-safe', '0', '-i', str(T / 'list.txt'), '-c', 'copy', str(T / 'video.mp4'))
    inputs = []; filt = []
    for i, (s0, wav) in enumerate(placed):
        inputs += ['-i', str(wav)]; filt.append(f'[{i}]adelay={int(s0 * 1000)}:all=1,apad[d{i}]')
    k = len(placed); extra = 0
    starts = {}; acc = 0.0
    for c in cut: starts[c['shot']] = acc; acc += c['seconds']
    for amb in sc.get('ambience', []):
        f = st.get(S.r2key(amb['key']), str(T / f'amb{extra}.mp3'), S.obj_sha(S.r2key(amb['key'])))
        if amb['mode'] == 'bed':
            inputs += ['-stream_loop', '-1', '-i', f]
            filt.append(f"[{k + extra}]atrim=0:{total},loudnorm=I={amb.get('loudnorm_i', -29)}:TP=-8:LRA=7,afade=t=in:d=1.5,afade=t=out:st={total - 2}:d=2[m{extra}]")
        else:
            inputs += ['-i', f]
            filt.append(f"[{k + extra}]volume={amb.get('volume', 0.35)},afade=t=in:d=1,afade=t=out:st={amb.get('fade_out_at', 10)}:d={amb.get('fade_out_s', 3)},adelay={int(starts.get(amb['shot'], 0) * 1000)}:all=1,apad[m{extra}]")
        extra += 1
    if k + extra == 0: sys.exit('no audio at all')
    filt.append(''.join(f'[d{i}]' for i in range(k)) + ''.join(f'[m{j}]' for j in range(extra)) + f'amix=inputs={k + extra}:normalize=0:duration=longest,atrim=0:{total}[aout]')
    ff(*inputs, '-filter_complex', ';'.join(filt), '-map', '[aout]', '-ar', '48000', '-ac', '2', str(T / 'mix.wav'))
    # two-pass loudnorm (Quality bar v2 rule 4): measure, then apply linearly to I=-16, LRA 7, TP -1.5
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(T / 'mix.wav'), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True, timeout=600).stderr
    m = json.loads(r[r.rfind('{'):r.rfind('}') + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    ff('-i', str(T / 'mix.wav'), '-af', ln + ',aresample=48000', '-ar', '48000', '-ac', '2', str(T / 'audio.wav'))
    def ts(x): return f'{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}'
    for lg in S.LANGS:
        with open(T / f'{lg}.vtt', 'w') as f:
            f.write('WEBVTT\n\n')
            for j, (l2, a, b, txt) in enumerate([c for c in cues if c[0] == lg]): f.write(f'{j + 1}\n{ts(a)} --> {ts(b)}\n{txt}\n\n')
    LN = {'cy': 'wel', 'en': 'eng', 'es': 'spa'}; order = [lang] + [x for x in S.LANGS if x != lang]
    sub_in = []; maps = []; meta = []
    for i, lg in enumerate(order):
        sub_in += ['-i', str(T / f'{lg}.vtt')]; maps += ['-map', f'{i + 2}:0']
        meta += [f'-metadata:s:s:{i}', f'language={LN[lg]}', f'-disposition:s:{i}', 'default' if i == 0 else '0']
    vk = max(800, min(2400, int((23.5e6 * 8 / total - 128000) / 1000)))
    VP9 = ['-c:v', 'libvpx-vp9', '-b:v', f'{vk}k', '-minrate', f'{vk // 2}k', '-maxrate', f'{vk * 2}k', '-bufsize', f'{vk * 4}k', '-row-mt', '1', '-tile-columns', '1', '-auto-alt-ref', '1', '-lag-in-frames', '25', '-deadline', 'good']
    ff('-i', str(T / 'video.mp4'), *VP9, '-cpu-used', '4', '-pass', '1', '-passlogfile', str(T / 'p2'), '-an', '-f', 'null', '/dev/null', t=1800)
    ff('-i', str(T / 'video.mp4'), '-i', str(T / 'audio.wav'), *sub_in, '-map', '0:v', '-map', '1:a', *maps, *VP9, '-arnr-maxframes', '7', '-arnr-strength', '3', '-cpu-used', '2',
       '-pass', '2', '-passlogfile', str(T / 'p2'), '-c:a', 'libopus', '-b:a', '128k', '-metadata:s:a:0', f'language={LN[lang]}', '-c:s', 'webvtt', *meta, out, t=2400)
    for lg in S.LANGS: shutil.copy(T / f'{lg}.vtt', out.rsplit('.', 1)[0] + f'.subs.{lg}.vtt')
    sz = os.path.getsize(out); res = {'out': out, 'seconds': total, 'MB': round(sz / 1e6, 2), 'under_25MB': sz < 25 * 1024 * 1024}
    if '--upload' in A:
        sha = S.sha256_file(out); key = f'studio/scenes/{sid}/cuts/{lang}/{sha[:12]}.webm'; st.put(out, key, 'video/webm'); S.record_object(sid, key, sha, sz, 'video/webm', 'assemble.py', st.last)
        res.update(key=key, github=st.last.get('github'), release_state=st.last.get('release_state'), cid=st.last.get('cid'))
    print(json.dumps(res))
finally:
    shutil.rmtree(T, ignore_errors=True)

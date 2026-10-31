#!/usr/bin/env python3
"""Pre-publish QA gate, Quality bar v2 (31 Oct 2026, task e0ba6a92). A clip that fails is NOT published.
Usage:
  python3 tools/qa_gate.py check <clip.webm> --talking "6.3-15.3,15.3-22.3" [--lang en] [--max-mb 25]
      -> machine checks + 3 frames per talking window extracted to /tmp/qa_gate/<clip>/ (look at EVERY one with attach_image)
         writes qa/<clip>.json with auto PASS/FAIL and look PENDING
  python3 tools/qa_gate.py sign <clip.webm> --verdict PASS|FAIL --notes "what you saw per shot"
      -> records your own look (faces/hands/mouth/eyeline/period/heraldry); PASS only if every frame is clean
  python3 tools/qa_gate.py ok <clip.webm>   -> exit 0 only if auto PASS and look PASS (the publish step must call this)
Machine checks: 1280x720, 24 fps (no 25/30 fps conversion of 24 fps sources), VP9, size < max-mb,
integrated loudness -17..-15 LUFS, true peak <= -1.0 dBTP, loudness range <= 10 LU, no interior silence > 1.5 s.
Studio copy (cedwyn-studios, 31 Oct 2026): records go to qa/ at the repo root; loudness is read with Tab's audio-proof tool when present, else with ffmpeg (loudnorm + silencedetect), so any computer with ffmpeg can run it.
"""
import json, os, sys, subprocess, pathlib, shutil, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
QD = ROOT / 'qa'; QD.mkdir(exist_ok=True)
def run(a, t=300):
    return subprocess.run(['timeout', '-k', '5', str(t)] + a, capture_output=True, text=True)
def probe(p):
    j = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size', '-of', 'json', p]).stdout)
    v = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    return v, float(j['format']['duration']), int(j['format']['size'])
def audio_facts(clip):
    ap = pathlib.Path('/home/user/tab/audio-proof.mjs')
    if ap.exists():
        try: return json.loads(run(['node', str(ap), 'inspect', clip]).stdout)
        except Exception: pass
    import re
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', clip, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], t=600).stderr
    j = json.loads(r[r.rfind('{'):r.rfind('}') + 1])
    s = run(['ffmpeg', '-hide_banner', '-nostats', '-i', clip, '-af', 'silencedetect=n=-35dB:d=0.4', '-f', 'null', '-'], t=600).stderr
    dur = float(json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', clip]).stdout)['format']['duration'])
    sil = []; st = None
    for line in s.splitlines():
        m = re.search(r'silence_start: ([\d.]+)', line)
        if m: st = float(m.group(1))
        m = re.search(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)', line)
        if m and st is not None:
            if st > 0.05 and float(m.group(1)) < dur - 0.05: sil.append({'start_s': st, 'duration_s': float(m.group(2))})
            st = None
    return {'loudness': {'integrated_lufs': float(j['input_i']), 'true_peak_dbtp': float(j['input_tp']), 'loudness_range_lu': float(j['input_lra'])}, 'interior_silences': sil}
def opt(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
cmd, clip = sys.argv[1], sys.argv[2]
rec = QD / (pathlib.Path(clip).name + '.json')
if cmd == 'check':
    v, dur, size = probe(clip); fails = []
    if (v['width'], v['height']) != (1280, 720): fails.append(f"size {v['width']}x{v['height']} (want 1280x720)")
    if v['r_frame_rate'] not in ('24/1', '24000/1000'): fails.append(f"fps {v['r_frame_rate']} (want 24/1)")
    if v['codec_name'] != 'vp9': fails.append(f"codec {v['codec_name']}")
    mx = float(opt('--max-mb', 25))
    if size > mx * 1e6: fails.append(f"{size/1e6:.1f} MB > {mx} MB")
    a = audio_facts(clip)
    L = a.get('loudness') or {}
    if not (-17.0 <= L.get('integrated_lufs', -99) <= -15.0): fails.append(f"loudness {L.get('integrated_lufs')} LUFS (want -16 +/-1)")
    if L.get('true_peak_dbtp', 0) > -1.0: fails.append(f"true peak {L.get('true_peak_dbtp')} dBTP (want <= -1.0)")
    if L.get('loudness_range_lu', 99) > 10: fails.append(f"loudness range {L.get('loudness_range_lu')} LU (want <= 10; dialogue vs ambience too uneven)")
    long = [s for s in a.get('interior_silences', []) if s['duration_s'] > 1.5]
    if long: fails.append('interior silence > 1.5 s at ' + ', '.join(f"{s['start_s']:.1f}s ({s['duration_s']:.1f}s)" for s in long))
    fd = pathlib.Path('/tmp/qa_gate') / pathlib.Path(clip).stem; shutil.rmtree(fd, ignore_errors=True); fd.mkdir(parents=True)
    frames = []
    for w in [x for x in (opt('--talking', '') or '').split(',') if x]:
        s, e = map(float, w.split('-'))
        for t in (s + 0.3, (s + e) / 2, e - 0.3):
            out = fd / f't{t:07.2f}.jpg'; run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t}', '-i', clip, '-frames:v', '1', '-q:v', '3', str(out)], 60); frames.append(str(out))
    r = {'clip': clip, 'checked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'duration_s': round(dur, 2), 'mb': round(size / 1e6, 2),
         'video': v, 'loudness': L, 'auto': 'FAIL' if fails else 'PASS', 'fails': fails, 'frames': frames,
         'look': 'PENDING', 'look_rule': 'attach_image every frame; FAIL on: warped hands/fingers, face drift from the cast sheet, eyes on the lens, mouth not moving on speech or moving on silence, smeared teeth, period errors (chimneys, glass windows, modern clothes/objects), any heraldry, text artefacts'}
    rec.write_text(json.dumps(r, indent=1)); print(json.dumps({k: r[k] for k in ('auto', 'fails', 'mb', 'duration_s')}, indent=1)); print(len(frames), 'frames to look at in', fd)
    sys.exit(0 if not fails else 2)
if cmd == 'sign':
    r = json.loads(rec.read_text()); r['look'] = opt('--verdict'); r['look_notes'] = opt('--notes', ''); r['look_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    assert r['look'] in ('PASS', 'FAIL'); rec.write_text(json.dumps(r, indent=1)); print('signed', r['look'])
if cmd == 'ok':
    r = json.loads(rec.read_text()) if rec.exists() else {}
    ok = r.get('auto') == 'PASS' and r.get('look') == 'PASS'
    print('QA GATE', 'OPEN' if ok else 'BLOCKED', r.get('fails'), r.get('look')); sys.exit(0 if ok else 3)

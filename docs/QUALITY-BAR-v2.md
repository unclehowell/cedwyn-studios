> Ported 31 Oct 2026 from the movie runner. tools/assemble.py and tools/qa_gate.py implement it. Studio wording: the talking-shot prompt template uses "and speaks, <one emotion word>, \"<line>\"".

## QUALITY BAR v2 — every scene run follows this (31 Oct 2026, health check task e0ba6a92; owner WhatsApp 12:06 GMT 31 Oct: "I want it to produce better quality videos")
Measured on the live Door 2 (clips/F002.v6*.webm) and Door 1 (F001.v2) on 31 Oct; numbers are from ffprobe, ffmpeg PSNR/SSIM and audio-proof on this box.
1. 24 fps end to end. OmniHuman 2.0 and Kling 2.5 deliver 24 fps (1274x722 / 1280x716); every cut so far was conformed to 25 fps, which duplicates one frame a second (judder, worst on mouths). Timeline, intermediates and the final file stay at 24 fps; scale with flags=lanczos.
2. Never re-cut a published file. Shared (non-talking) shots come from their ORIGINAL renders (Door 2 map: F002native/shared_sources.json), never from clips/*.webm. Measured: re-cutting the published webm costs 2.6 dB PSNR on a face shot (37.4 vs 40.1 dB at the same size).
3. Two-pass VP9 that fills the size budget: target bitrate = (23.5 MB x 8 / seconds) - 128k, minrate/2, maxrate x2, auto-alt-ref, lag 25, pass 2 at cpu-used 2 (recipe in F002native/assemble.py). Measured at equal size on Door 2 shot 2: 40.1 dB vs 38.6 dB for the old one-pass crf 34 cpu-used 4. The 25 MB cap is the cedwyn-movie fetch-media check; PROPOSED (root/owner): raise it to 45 MB for the paid R2 cuts only (about 2.4 Mbps), the largest remaining picture lever.
4. Audio mastered for phones: two-pass loudnorm I=-16, LRA=7, TP=-1.5 on the final mix; ambience bed about 13 LU under dialogue; Opus 128k. Measured: Door 2 cy/en loudness range 20 / 18.7 LU (dialogue and ambience far apart), true peak -0.56 dBTP; the en cut has a 1.9 s dead gap at 124 s.
5. OmniHuman prompt structure (GENERATION_CRAFT 'Video prompt craft' + 'Anti-glaze'): the still's setting and ONE light source; then "<He/She> keeps head and eyes turned three-quarters toward <listener> off-screen for the whole shot and speaks, <one emotion word>, "<the exact line in the shot's language>""; then "Natural blinks, small head movements; never faces the camera. Keep the still's light and colours. Natural skin texture, no CGI gloss, no text." Never "then turns to him": in the 31 Oct A/B that phrase swung the eyes onto the lens. Stills: 16:9 at least 1920 wide, the speaker's face at least 350 px tall, body three-quarters to the listener, period props checked (no chimneys, glazed windows, electric-looking lights, modern loaves or haircuts before their time), one light consistent with the scene's time of day.
6. Retakes only for a shot that fails the look in the gate below; one retake per shot per run, then log it to work/problems/QUEUE.md.

### PRE-PUBLISH QA GATE (blocking) — tools/qa_gate.py
- `python3 tools/qa_gate.py check <each language video> --talking "<start-end of every talking shot>"` (machine checks: 1280x720, 24 fps, VP9, < 25 MB, -16 +/-1 LUFS, true peak <= -1 dBTP, loudness range <= 10 LU, no interior silence > 1.5 s; it extracts 3 frames per talking shot).
- LOOK at every extracted frame (`await attach_image(path)`): face matches the cast sheet, eyes off the lens, mouth open on vowels and closed in pauses, teeth/hands not smeared or extra, period props right, no heraldry, no text artefacts. Then `qa_gate.py sign <video> --verdict PASS|FAIL --notes "<what you saw per shot>"`.
- `qa_gate.py ok <video>` must exit 0 for EVERY language video before upload_media / the manifest commit. A failing shot is re-taken (rule 6) or the door waits; never publish over it. Record the qa/<video>.json verdicts in the report.
- Baseline: the live Door 2 en video fails the gate today (25 fps, LRA 18.7 LU, TP -0.62, 1.9 s gap); Door 2 and Door 1 are grandfathered until JOB 1 replaces them.



## STANDING RULE — EVERY SCENE GENERATED FROM SCRATCH PER LANGUAGE (cy, en, es) | owner 30 Oct 2026 21:29 GMT, recorded by task cb666e05
Owner, verbatim: "when I change audible languages in documeht I expect the entire video to be generated from scratch for all 3 languages per each scene. Remember that. Don't just produce one video in one language. Because I want the lip sync to match the audio when users change audio and I don't want a half measure"
From now on every scene (new doors and every redo) is made three times, once per language:
1. cy, en and es each get their OWN full render of EVERY talking shot, performed in that language (native voice line for that language).
2. Each talking shot is ByteDance OmniHuman 2.0 (`bytedance/omnihuman/v2`) lip-synced to THAT language's own audio. Never a mouth re-sync of another language's render.
3. Each language gets its OWN assembled video file carrying only its own audio. The manifest lists `"video": {"cy": …, "en": …, "es": …}` on EVERY door entry (`clip` = the cy file as fallback); the player switches video with the audio language.

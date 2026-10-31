> Ported 31 Oct 2026.

# STANDING RULE — EVERY SCENE GENERATED FROM SCRATCH PER LANGUAGE (cy, en, es) | owner 30 Oct 2026 21:29 GMT, recorded by task cb666e05
Owner, verbatim: "when I change audible languages in documeht I expect the entire video to be generated from scratch for all 3 languages per each scene. Remember that. Don't just produce one video in one language. Because I want the lip sync to match the audio when users change audio and I don't want a half measure"
From now on every scene (new doors and every redo) is made three times, once per language:
1. cy, en and es each get their OWN full render of EVERY talking shot, performed in that language (native voice line for that language).
2. Each talking shot is ByteDance OmniHuman 2.0 (`bytedance/omnihuman/v2`) lip-synced to THAT language's own audio. Never a mouth re-sync of another language's render.
3. Each language gets its OWN assembled video file carrying only its own audio. The manifest lists `"video": {"cy": …, "en": …, "es": …}` on EVERY door entry (`clip` = the cy file as fallback); the player switches video with the audio language.
SUPERSEDED / HALF MEASURES (never again for a new cut): the 30 Oct 02:39Z approach (Kling video-to-video re-lip-sync of the Welsh shot for en/es, as in F002.v6.en/.es), and any single video with swapped audio tracks (one lip-synced video + separate cy/en/es audio). Existing cuts made that way stay only as older versions.
Cost: about 3 × OmniHuman per scene (≈ 3 × talking seconds × $0.105). Render budget still applies: no paid render unless the rolling 24 h spend is under about $7; if over, prepare everything (lines, voices, stills, plan) and queue it, then stop before the paid render.
A cut is not "done" until all three language videos exist, each verified (transcribe-back, 3 frames per talking shot: mouth open on vowels, closed on silence).
— the owner's Tab agent

---

# Multi-language video — NO DUBBING from 30 Oct 2026 05:00Z (supersedes the Kling LipSync verdict below)

Owner 04:58 GMT 30 Oct: "Forget dubbing and make 3 language specific seperate videos but keep the current as older versions." GO 05:05: "Do it even if it takes days. Just update hubspot" (HubSpot (task id kept off the public repo)).

## Rule
- Each language (cy, en, es) is its own separately performed video: its own lines spoken by a native voice for that language, and its own OmniHuman 2.0 (`bytedance/omnihuman/v2`, $0.105/s) render of every shot where a character speaks on camera. No mouth re-sync of another language's performance (Kling LipSync, sync. lipsync-2, LatentSync etc. are no longer used for the film).
- Shots where nobody speaks on camera (i2v landscapes, document inserts, date cards, end card) are rendered once and shared by all three videos; only the audio bed changes (ambience shared, dialogue per language).
- Voices: cy = the designed Welsh voices (eleven_v4 language_code cy; Gemini TTS fallback). en = the same characters in Welsh-accented English (the characters are Welsh). es = native Spanish voices (Rioplatense, designed per character; never a Welsh voice reading Spanish). The voice account was at its custom-voice limit on 29 Oct: free or reuse a slot before designing (not checked today).
- Each language file carries only its own audio. Manifest: `video: {cy, en, es}` on the v0.0.1 entry; `clip` = cy.
- The dubbed cuts stay playable as older versions (#v0.0.1-0.0.N chips on /documentary/): Door 2 #v0.0.1-0.0.5 = F002.v6 (Welsh) + F002.v6.en/.es (Kling dubs); Door 1 #v0.0.1-0.0.2 = F001.v2 (Welsh lip-sync, en/es dub tracks). v0.0.1 is reserved for the native release (`next_version` status "coming").

## Per door: what needs its own render (detail and costs in RERENDER-QUEUE.md JOB 1)
| door | talking shots (own render per language) | shared shots | cy | en | es | door total |
|---|---|---|---|---|---|---|
| 2 (F002 v1.0.2) | 2, 3, 6, 7, 8, 10, 11, 13, 14, 16, 17 (11 shots, 91 s) | 1, 4, 5, 9, 12, 15, 18 i2v + end card | reuse Welsh OmniHuman renders ($0) | ≈ $9.5 | ≈ $9.9 | ≈ $20–23 incl. voices + ~15% retakes |
| 1 (F001 v0.3.0, cut v2) | cut shots 2, 5, 6, 8, 13, 14 (6 close-ups, ≈ 66 s; Welsh renders cost $6.94) | title still, wide i2v, document inserts, stills | reuse ($0) | ≈ $6.4 | ≈ $6.9–7.2 | ≈ $14–16 |
All figures are list-price estimates (bible/MODELS.md), NOT CHECKED against receipts. If the cy shots must also be re-performed: + ≈ $9.6 (Door 2), + ≈ $6.9 (Door 1).
Every new door from Door 3 on is made this way from the start (three performances, shared non-speaking shots): ≈ 3 × talking seconds × $0.105.

## Verification per shot per language
audio-proof on the line; transcribe back ≥ 0.8; 3 frames per shot against the line (open on vowels, closed on silence); the face matches the character's reference portrait.

---

# Multi-language lip-sync — research, plan, rule (30 Oct 2026, worker c52025d8)

Owner ask, WhatsApp 02:39 GMT 30 Oct, verbatim: "Surely you can make 3 variations of the webm in the 3 different languages so lipsync always matches the spoken language. I'm sure there's been innovations in ai for doing this recently. Research a bit first. Plan a big. Then attempt it."

## What exists (video-to-video: keep the shot, redraw only the mouth to new audio)
All reachable through our fal vendor proxy (VENDOR_CAPABILITY.md, fal registered). Prices are the model pages' own, read 30 Oct 2026.

| Tool | fal id | Price | Clip limits | Notes / source |
|---|---|---|---|---|
| Kling LipSync (audio-to-video) | fal-ai/kling-video/lipsync/audio-to-video | $0.014 per 5 s increment (page text; one snippet reads per second, to confirm on our receipt) | video 2–10 s, 720p/1080p, ≤100 MB; audio 2–60 s, ≤5 MB | language-agnostic (phoneme-free audio model). https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video |
| sync. lipsync-2 | fal-ai/sync-lipsync/v2 | $3.00 / min ($0.05/s) | long clips | zero-shot, keeps speaker style; strongest published quality. https://fal.ai/models/fal-ai/sync-lipsync/v2 |
| sync. lipsync-2-pro | fal-ai/sync-lipsync/v2/pro | $5.00 / min ($0.083/s) | long clips | finer teeth/beard detail. https://fal.ai/models/fal-ai/sync-lipsync/v2/pro |
| LatentSync | fal-ai/latentsync | $0.20 per video up to 40 s, then $0.005/s | | diffusion lip-sync, open model. https://fal.ai/models/fal-ai/latentsync |
| MuseTalk | fal-ai/musetalk | per compute second | | real-time, lower fidelity. https://fal.ai/models/fal-ai/musetalk |
| sync lipsync 1.9 | fal-ai/sync-lipsync | $0.70 / min | | older generation |
| HeyGen / Rask-style "video translate" | not on our proxy | subscription | | they also re-translate and clone the voice; we already have our own cy/en/es lines and voices, so we only need the mouth step |
| OmniHuman 2.0 per language | bytedance/omnihuman/v2 | ≈ $0.105/s | ≤ ~30 s audio | full re-render from the still: best match to our cy shots but 3× the cost; fallback only |
| Wav2Lip / Piper | — | — | — | REJECTED by the owner 27 Oct. Never. |

All of these drive the mouth from the audio waveform, not from text, so Welsh is not a special case for them; the quality risk is the dub's timing, not the language.

## Verdict
- PRIMARY: Kling LipSync — cheapest by far, 720p native, fits our ≤10 s talking shots (longer shots split at a pause into ≤10 s pieces and re-joined).
- FALLBACK: sync. lipsync-2 ($0.05/s) when a Kling result smears the mouth or drifts; lipsync-2-pro for close-ups that need it. OmniHuman per language only if both fail on a shot.

## Plan and cost per scene (≈ 95 s of talking per ~2 min scene)
- cy video: OmniHuman as now (≈ $10 per scene incl. stills/i2v).
- en + es videos: Kling on every talking shot per language ≈ 2 × 95 s → about $0.27–$2.70 per scene depending on how Kling is billed (to be confirmed on the first receipts); with lipsync-2 instead ≈ $9.50.
- Order: Door 2 now (being re-voiced anyway) → Door 1 inside its all-motion redo → every future door by default.
- Verification per shot per language: audio-proof on the track, then 3 frames per shot checked against the line (open mouth on vowels, closed on silence).

## Manifest shape (for the player)
Each `filled` entry keeps `clip` (the Welsh video, back-compat) and gains
`"video": {"cy": "clips/F00N.webm", "en": "clips/F00N.en.webm", "es": "clips/F00N.es.webm"}`.
Each language file carries ONLY its own audio track. A missing language key means: play `clip` with the separate `audio[lang]` track (old behaviour).

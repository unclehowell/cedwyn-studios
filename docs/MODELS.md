> Ported 31 Oct 2026. The "free route" text below is history only: rejected by the owner on 27 Oct 2026. Talking shots use OmniHuman 2.0.

> **QUALITY BAR v2 (31 Oct 2026, task e0ba6a92) — OmniHuman 2.0 facts and settings.** `bytedance/omnihuman/v2` input schema (fal OpenAPI, read 31 Oct): `image_url`, `audio_url` (wav/mp3 ≤ 15 MB, 4–300 s), optional `prompt` (zh/en/ja/ko/es-MX/id) — no resolution, seed or fps fields. Output from a 1920x1088 still: 1274x722 H.264 24 fps, ~4.3 Mbps, AAC; 8 s of audio took 166 s and was billed 8 s x $0.105 = $0.84 (request 01a191e0…, spend.jsonl). So picture quality is set by (a) the still, (b) the prompt, (c) what we do after: keep 24 fps, lanczos to 1280x720, never re-cut a published file, two-pass VP9 (RUNNER.md 'QUALITY BAR v2'). Prompt shape that held the look and lip-sync in the 31 Oct A/B: setting + one light, gaze locked "three-quarters toward <listener> off-screen for the whole shot", the exact line in quotes with one emotion word, "Natural skin texture, no CGI gloss, no text". A higher-resolution talking shot needs `fal-ai/bytedance/omnihuman/v1.5` with `resolution: 1080p` ($0.16/s, ≤ 60 s audio at 720p, not tested here) or an upscale pass; neither is worth it while the delivery file is capped at 25 MB. Kling 2.5 turbo i2v also delivers 24 fps (1280x716).

> **CURRENT RULE — the owner 27 Oct 13:35 GMT, verbatim: "Never do that method again. Its so bad. Just use ByteDance Omnihuman 2.0 moderately so the scene gets done to perfection and take as long as it takes so we keep it minimal cost".**
> This SUPERSEDES the 12:50 "keep it free" block below (restored 28 Oct 2026 04:50 UTC by the CEDWYN MOVIE RUN worker). Talking shots (only where a character speaks on camera) = fal `bytedance/omnihuman/v2` (OmniHuman 2.0, $0.105 per output second, 16:9 1280x720 still + the Welsh line; recipe in bible/MODELS.md section 1). Ambient shots = stills with slow ffmpeg moves; new stills may be generated cheaply (gpt-image-2.5, era/scene looks as EDITS of the bible reference). Voices: ElevenLabs eleven_v4 cy (bible/VOICES.json). Spend only inside the render budget left in live-state; if it is $0, prepare everything and wait (log the wait to work/problems/QUEUE.md). Retakes only when a shot is visibly wrong.
> The free Piper + Wav2Lip talking-portrait route is **REJECTED by the owner 27 Oct 13:35 — never use it again**; its models were deleted 28 Oct. The "free" text below is kept only as history.


> **the owner 27 Oct 12:50: keep it free.** WhatsApp 12:50 GMT 27 Oct 2026, replying to the budget question: "Keep it free whatever that takes".
> RULE: ZERO SPEND, FREE TOOLS ONLY, for every scene from now on (F002 v2 included). No OmniHuman, no Kling/Seedance/Veo, no paid image models, no ElevenLabs/Gemini TTS, no paid transcription. The 6-hourly cadence stays.
> Proven free route (27 Oct 13:11 UTC, proof /home/user/tab/files/movie-free-proof.webm): Piper TTS with `free/models/cy_GB-bu_tts-medium.onnx` (speakers benyw-de-pro = female South, gwryw-de-1 = male South) → `free/lipsync.py` (Wav2Lip GAN ONNX on CPU, on the actor's existing portrait) → ffmpeg push-ins, cards, VP9. About 30 s of CPU per 10 s of talking shot. Details: bible/MODELS.md §0.
> Honest limits: the mouth moves but the head and eyes stay still, and the mouth area is softer than the face. Ambient shots are stills with slow moves (no AI motion). New scenes or era looks come from portraits/sets already on disk or openly licensed archive photos (credited), never new generation. Files already paid for (e.g. F002v2/audio) may be reused at $0.
# CEDWYN — model probe and production recipe (v1, 25 Oct 2026)

Helper run a110fe21 for the pre-production worker. Every call went through Tab's vendor door (`https://control.tab.bot/v/<vendor>/...`, with `x-tab-task`).
Prices are the vendors' published list prices read on 25 Oct 2026; the request ids for every fal job are in `test/fal_requests.jsonl`.


## 0. FREE ROUTE (27 Oct 2026, measured on this box) — the only route now

| step | tool (free, local) | size | measured | quality |
|---|---|---|---|---|
| Welsh TTS | `piper` 1.8 (already installed) + `free/models/cy_GB-bu_tts-medium.onnx` (Bangor Univ. bu-tts, CC-BY, 7 speakers: benyw-de-pro, benyw-gogledd-pro, gwryw-gogledd-pro, gwryw-gogledd-2, gwryw-de-1, gwryw-gogledd-1, benyw-gogledd-1) | 77 MB | 12.5 s of speech in 3.3 s CPU | clear native Welsh pronunciation; studio-neutral read, less character than the designed voices; accent strength not checked by ear. `de` = South, `gogledd` = North |
| Lip-sync | `free/lipsync.py`: Wav2Lip GAN as ONNX (`free/models/wav2lip_gan_96.onnx`, from the FaceFusion asset release) on onnxruntime 1.29 CPU, mel computed in numpy, face box given by hand once per portrait, feathered mouth mask + unsharp | 145 MB (+ opencv-python-headless) | 359 frames (14.3 s) in 25 s at 1024²; ~17 s per 10 s | mouth opens/closes in time with the Welsh; head/eyes static (no blinks); mouth region softer (96 px model). Reads as a talking portrait, not a filmed actor |
| Motion | ffmpeg `scale=…:eval=frame` + `crop` push-in, pans, crossfades, drawtext cards | 0 | VP9 crf 32 encode ~10 s per 10 s at 720p | fine; do NOT use zoompan on a video input (dropped 1.7 s of frames in the first proof) |
| Subtitles | own VTT from the TTS cue timings; `subtitle_check.py` | 0 | — | en 1 soft WPM flag, es 0 |

Proof: `/home/user/tab/files/movie-free-proof.webm` (14.4 s, 1280×720 VP9 + Opus cym + WebVTT eng/spa, 427 KB; −18.0 LUFS, TP −1.2 dBTP, interior pauses 0.47–0.71 s only between sentences) and `movie-free-proof-subs.mp4` (English burned in, for phones). Build files in `free/proof/`.
Not free / not used now: OmniHuman (head motion, expressions), Kling/Seedance i2v (ambient motion), new image generation (new sets, era edits, children), designed ElevenLabs voices.
Nearest free substitutes: talking portrait (above); slow moves on stills; existing bible portraits/sets and openly licensed archive photos (credit them); Piper bu_tts speakers. Considered, not installed: SadTalker / LivePortrait (need PyTorch, >1.5 GB with weights, too heavy for this disk/RAM); GFPGAN mouth restore (340 MB ONNX, ~1–2 s per frame on CPU — too slow for 2-minute scenes); MMS-TTS cym (PyTorch).

**Sections 1–7 below are the PAID recipe of 25 Oct, kept for reference only. Do not use them (27 Oct free rule).**

## 1. Talking video: OmniHuman

| model id (fal queue) | status | request shape | result |
|---|---|---|---|
| `bytedance/omnihuman/v2` (**OmniHuman 2.0**, listed "Bytedance Omnihuman V2", active) | **PASS** | `{image_url, audio_url, prompt?}`. Audio: wav/mp3, ≤15 MB, **4–300 s**. Image: jpeg/png/webp etc., ≤30 MB, aspect 0.4–2.5. Prompt languages: zh, en, ja, ko, es(MX), id | 7.8 s of audio → 8.0 s, **960×960** H.264 24 fps with AAC, the audio echoed back in sync. Queue+render **~7.5 min** wall (461 s). **$0.105 per output second** (fal page), so this test ≈ **$0.84** |
| `fal-ai/bytedance/omnihuman/v1.5` | listed, schema read, not rendered | adds `resolution` 720p/1080p (≤60 s audio at 720p), `turbo_mode`, `mask_url` (choose who speaks) | $0.16/s |
| `fal-ai/bytedance/omnihuman` (v1) | listed, not tested | | |
| `fal-ai/omnihuman` | **FAIL**: `Application "omnihuman" not found` | | |

Findings:
- **A generated (non-real) face works.** The test used the edited 1974 Mary portrait. Identity held through every frame I checked (the mole, the eyes, the cardigan). The prompt was obeyed: she glances down at the letters once.
- **Inputs must be real https URLs.** A `data:` URI for the audio failed with fal's own words: `"Failed to download the file. Please check if the URL is accessible and try again." (file_download_error)`.
  Workaround that needs no publishing: pass the file through a fal utility that accepts data URIs and returns a fal-hosted URL. I used `fal-ai/ffmpeg-api/loudnorm` (`{audio_url: data:..., integrated_loudness: -16}` → `audio.url` on v3b.fal.media, 5 s, about $0). It also loudness-normalises the line. For images, reuse the fal.media URL returned by the image job that made the still (fetch it again from the job's `response_url`).
- Output is square 960×960 when the input is square. **Make OmniHuman stills 16:9** (1280×720 or 1920×1072) so the output is widescreen. The test cropped 960×540 from the square and upscaled it.
- OmniHuman lip-syncs **one** language per render. The cy and es tracks of a talking shot are either (a) dubbed over the English lip movement, or (b) re-rendered per language at 3× the cost. See the recipe.
- Not probed with money (the v2 pass made them unnecessary): `fal-ai/kling-video/ai-avatar/v2/pro`, `fal-ai/infinitalk`, `fal-ai/sync-lipsync/v3`, `veed/fabric-1.0`, `fal-ai/heygen/avatar4/image-to-video` are all listed on fal as talking-head alternatives. For non-talking motion (landscapes, sets, hands on documents), GENERATION_CRAFT's measured medians are Kling 2.5 turbo i2v ~126 s, Veo 3 ~140 s and Seedance 2.5 i2v ~279 s.

## 2. Images

| model id | status | latency | cost (list) |
|---|---|---|---|
| `openai/gpt-image-2.5/sunburst/text-to-image` (`quality: high`, `output_format: jpeg`, `output_compression: 88`) | **PASS** for 10 portraits (1024²) and 12 sets (1920×1072 → 1280×720) | 34–60 s when the queue is free. fal's queue for this model stalled 5–15 min when 8+ jobs were in flight; one job sat IN_QUEUE >15 min | 1024² high $0.053; 1920×1072 high $0.039 |
| `openai/gpt-image-2.5/sunburst/edit` (`image_urls: [data URI]` accepted) | **PASS**: same face held in new costume/scene (B_JOHN → 1890s farmer is excellent). **Weakness:** it under-ages. A_MARY "aged 60" came back looking about 48 (`cast/A_MARY_1974_gptedit.jpg`) | ~48 s | ~$0.05 |
| `fal-ai/nano-banana-pro/edit` (`image_urls`, `aspect_ratio`, `resolution: 1K`) | **PASS, better for ageing**: kept identity and aged convincingly to about 55–60. Used as the canonical `cast/A_MARY_1974.jpg` | 28–95 s | ~$0.15 |
| `fal-ai/nano-banana-pro` (text-to-image 16:9) | **PASS**: s07 courtroom in 28 s. A crest appeared on a judge's chair; one `nano-banana-pro/edit` ("make every chair back plain, no emblems") removed it cleanly | 28 s | ~$0.15 |
| Seedream v5 | not tested (fal's OpenAPI for `fal-ai/bytedance/seedream/v5/pro/edit` returned no schema; not needed) | | |

Consistency proof for buildings: `sets/s11.jpg` (the farmhouse in about 1980) is a **gpt-image edit of `sets/s01.jpg`**. It is the same building and viewpoint, aged, with housing behind. A text-only s11 gave a different house and was discarded. **Rule: every era of a set is an edit of its establishing reference, never a fresh text prompt.**

## 3. Speech (TTS) and checks

Welsh test line: "Bore da. Dyma Dŷ Mawr, Llandochau. Mae'r fferm wedi bod yma ers canrifoedd, ac mae'r papurau'n dweud y cyfan."
Every file was transcribed back with OpenAI `gpt-4o-transcribe` (model door) and scored as a word match against the script (1.0 = identical).

| engine / model | Welsh match (lang=cy / auto) | verdict |
|---|---|---|
| ElevenLabs `eleven_multilingual_v2` | 0.00 / 0.00 (heard as German-ish gibberish: "Burdaz, Dima Dima, Landeschau…") | **FAIL for Welsh** (cy is not in its 29 languages) |
| ElevenLabs `eleven_v3`, no language_code | 0.82 / 0.87 | ok |
| ElevenLabs `eleven_v3`, `language_code: cy` | 0.72 / 0.79 ("Bore da" → "Fodd bynnag") | weaker |
| **ElevenLabs `eleven_v4`, `language_code: cy`** | **0.92 / 1.00** | **PASS, chosen** (v4 lists 94 languages incl. cy) |
| Google AI `gemini-3.8-flash-tts` (voice Kore, styled "fluent Welsh, South Wales accent") | 0.95 / 0.95 | PASS, the Welsh fallback (a different timbre) |
| Google AI `gemini-2.5-pro-preview-tts` | 429 "You exceeded your current quota" | unavailable |

- ElevenLabs door facts: `GET /v1/voices` and `/v2/voices` are **refused by control** (`path_refused`: account-wide lists closed since 22 Oct). `GET /v1/voices/<id>`, TTS, `/v1/models`, voice design and creation work. `GET /v1/shared-voices` timed out at the door (30 s).
- **Groq Whisper is refused**: `"Organization has been restricted because of overdue payment(s)…"`. Use OpenAI `gpt-4o-transcribe` (text) and `whisper-1` (`verbose_json` + word timestamps, for subtitles) through the model door `https://control.tab.bot/capabilities/model/openai/v1/audio/transcriptions`.
- **Voices.** None of the stock ElevenLabs voices is Welsh-accented, so I **designed 10 voices** (`/v1/text-to-voice/design`, `eleven_ttv_v3`, 3 previews each). I kept the preview with the best transcribe-back and saved it with `POST /v1/text-to-voice` as "Cedwyn <ID>". Each actor uses one voice for all three languages through `eleven_v4`. All 30 samples transcribe back at 0.74–1.0, and the lower scores are only on spellings of Tŷ Mawr and Llandough. Ids, settings and scores are in `VOICES.json`.
- Spanish: the samples are neutral Latin American Spanish. J_ELENA's voice was designed rioplatense. The `es` translations are machine-written and need review.

## 4. Test clip (done)

`test/test-clip.webm`: 1280×720 VP9 (crf 32), 8.42 s, **1.40 MB**. It carries **three Opus audio tracks** (eng default, cym, spa, titled English / Cymraeg / Español) and one embedded WebVTT (eng). Sidecars: `test-clip.vtt` (= en), `test-clip.en.vtt`, `test-clip.cy.vtt`, `test-clip.es.vtt`. Source lines: `test/mary_line_{en,cy,es}.mp3`.
- ffprobe: vp9 1280×720 + 3× opus + webvtt; duration 8.424 s.
- audio-proof: −18.5 LUFS, true peak −0.17 dBTP; one interior pause at 3.74–4.27 s, the same as in the source line and in OmniHuman's echoed audio (lip sync is aligned); 0.8 s tail of silence (padding and fade).
- I checked frames at 0.8 s, 4.0 s and 7.2 s against `cast/A_MARY.jpg` and `cast/A_MARY_1974.jpg`: the same woman (mole, eyes, cheekbones), aged.
- The lips match English only. The cy/es tracks show the dub-over approach.
- Encode: `timeout -k 5 600 ffmpeg … -c:v libvpx-vp9 -crf 32 -b:v 0 -row-mt 1 -cpu-used 2 -deadline good -c:a libopus -b:a 64k -ac 1 -c:s webvtt` with `-metadata:s:a:N language=eng|cym|spa`. 14 s to encode 8 s on this box. Expect about 4–5 min per 2-minute clip at these settings, about 20 MB per 2 min at crf 32 (raise crf to 34–36 if a clip nears GitHub's 25 MB).

## 5. Files made

- `cast/<ID>.jpg`: 10 reference portraits, 1024², 110–200 KB, saved as JPEG (not PNG) to save disk. Era variants: `A_MARY_1974.jpg` (nano-banana-pro edit, canonical), `A_MARY_1974_gptedit.jpg` (gpt edit, under-aged), `B_JOHN_1890s.jpg` (gpt edit).
- `sets/s01–s13.jpg`: 1280×720, 180–300 KB. All by GPT Image 2.5 except s07, which is nano-banana-pro with an emblem removed by edit. s11 is an edit of s01.
- `voices/<ID>_{cy,en,es}.mp3`: 30 samples, 64 kbps. `voices/tests/`: the engine comparisons and the 10 chosen design previews.
- `VOICES.json`: voice ids, model, settings, QC scores, how to call.
- `test/`: the clip, VTTs, source lines, `fal_requests.jsonl` (every fal request id).

## 6. Spend (estimate from list prices)

- Images: about 38 GPT-image/NBP jobs ≈ **$2.3**. This includes ~16 jobs from the first batch whose replies were lost when the vendor door timed out (they may have rendered and billed; I re-ran them).
- OmniHuman v2: 8 s ≈ **$0.84** (the 422'd data-URI attempt and the empty-body id probes failed validation, unbilled as far as fal's rules go).
- ElevenLabs: 10 voice designs + about 45 short TTS lines ≈ **$1–1.5** in credits.
- Gemini TTS, transcription, loudnorm: < $0.10.
- **Total ≈ $4.5–5** (under the $8 cap).

## 7. Per-scene recipe (what I'd run each day for a ~2-minute frame)

1. **Read** `movie/PROMPT.md`, the frame's script (en/cy/es) and its cast/set ids.
2. **Stills (16:9, 1920×1072 → 1280×720)**: 8–14 shots per scene. Always **edit from the bible references**, never text-only:
   - people: `nano-banana-pro/edit` with `image_urls=[cast/<ID>.jpg (+ set/<sNN>.jpg)]` for age changes, or `gpt-image-2.5/sunburst/edit` for costume/scene with the same age;
   - places: `gpt-image-2.5/sunburst/edit` from `sets/<sNN>.jpg` for each era;
   - documents: real scans from the evidence pages where they exist, otherwise a generated "paper on the table" still with no legible invented text (HyperFrames overlays the real quoted words).
   Check each still against its reference (attach and look). Cost ≈ $0.05–0.15 each, so ≈ **$1/scene**. Run them in parallel, but keep at most 4–6 in flight (fal's GPT-image queue stalls above that).
3. **Dialogue audio**: per line, `eleven_v4` + the actor's voice id + `language_code`, for en, cy and es. Transcribe back (≥0.8, else re-render once, else Gemini TTS for cy). Join per language with ffmpeg. ≈ $0.3–0.5/scene/3 languages. Use whisper-1 word timestamps for the VTT cues.
4. **Talking shots (OmniHuman v2)**: 2–4 shots per scene, 5–12 s each, **English lip-sync only** ≈ 20–30 s ≈ **$2–3/scene**, with ~7–8 min render each (run them in parallel). Host the audio via `fal-ai/ffmpeg-api/loudnorm` and the image via its own fal.media URL. Every other spoken line plays over stills, documents, reaction shots, over-the-shoulder shots and landscapes (the soap reads naturally that way, and the cy/es dubs don't fight the lips). Full 120 s lip-sync in all three languages would be 360 s × $0.105 ≈ $38/day, which is not recommended.
5. **Ambient motion** (optional, 1–2 shots): Kling 2.5 turbo i2v or Seedance i2v from a set still, 5 s, for landscapes and smoke. Otherwise HyperFrames Ken Burns on stills (free).
6. **Assembly in HyperFrames** (`npx hyperframes render`, the hf-series kit with `HFW=1` under disk pressure): 1280×720 timeline of OmniHuman clips + stills with slow push-ins + document overlays with the real quoted lines and their source line + the date/era card + a "A tab.bot production" end card. Render the picture once, **without burned-in subtitles**.
7. **Mux** with ffmpeg: VP9 crf 32–34, 3 Opus tracks (eng default, cym, spa) + 3 WebVTT tracks embedded, plus sidecar `.vtt` per language for the page's subtitle toggle. Keep the file under 25 MB (2 min ≈ 15–22 MB), else raise crf or split into a/b.
8. **QC**: ffprobe (streams, duration 90–150 s), `audio-proof.mjs inspect` (no interior silence > 1.5 s unless scripted, −16 to −20 LUFS), 3 frames compared against the bible portraits, and a transcribe-back of each language track.
9. **Timing per day** ≈ 25–40 min of machine time (stills 5–10 min in parallel, OmniHuman ~8 min in parallel, HyperFrames 5–10 min, encode ~5 min).
   **Cost ≈ $4–5 per 2-minute scene**, i.e. about **$2–2.5 per finished minute**. For a ~148-frame film that is about $600–750 over the run.
10. Delete raw renders after muxing. Disk is ~2.3 GB free.

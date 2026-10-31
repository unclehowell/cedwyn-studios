> Ported 31 Oct 2026. The machine-readable order is studio/queue/queue.json; tools/next.py walks it.

# RERENDER QUEUE

## JOB 0 (ABOVE EVERYTHING) — PER-LANGUAGE FROM-SCRATCH RULE (owner 30 Oct 2026 21:29 GMT; recorded by task cb666e05)
Every job below, and every new door, is produced three times: cy, en and es each get their own full render of every talking shot in that language, OmniHuman 2.0 lip-synced to that language's own audio, and their own assembled video; the manifest lists `video: {cy, en, es}` for every door. Kling video-to-video re-lip-sync (the 30 Oct 02:39Z approach) and one-video-with-swapped-audio cuts are half measures and are not made any more. Cost ≈ 3 × OmniHuman per scene. No paid render unless the rolling 24 h spend is under about $7; otherwise prepare and queue. Full text: RUNNER.md top and bible/LIPSYNC-MULTILANG.md top.

## JOB 1 (TOP) — NATIVE-LANGUAGE PERFORMANCES cy/en/es, Door 2 then Door 1 | GO from the owner 30 Oct 05:05; pace within the render budget; take as long as needed
Owner 04:58 GMT 30 Oct: "Forget dubbing and make 3 language specific seperate videos but keep the current as older versions." Owner 05:05: "Do it even if it takes days. Just update hubspot".
HubSpot task **(task id kept off the public repo)** "[CEDWYN MOVIE] Native-language performances (cy/en/es), Doors 1-2" (NOT_STARTED): every movie run appends a dated progress line to its body (what rendered, $ spent, what is next); progress goes to HubSpot, never to the owner. Mark it COMPLETED only when all three languages are live for both doors.
Rule: no dubbing and no mouth re-sync (Kling LipSync / sync.) from now on. Each language is its own performance: its own native voice lines and its own OmniHuman 2.0 render of every on-camera talking shot. Non-speaking shots are shared by all three videos.
Page/manifest state (done 30 Oct, task 55c81952): the dubbed cuts are older versions — Door 2 plays #v0.0.1-0.0.5 (F002.v6 + .en/.es Kling dubs), Door 1 plays #v0.0.1-0.0.2 (F001.v2); each entry has `next_version: {version: "0.0.1", status: "coming"}`, shown as a disabled "#v0.0.1 coming" chip.

## JOB 1 progress — Door 2 native performances (30 Oct 2026, 08:05–08:30Z, CEDWYN MOVIE RUN 05d200e8)
Prepared up to the paid render; NO OmniHuman render made this run (budget, see below).
- en: 11 lines voiced (ElevenLabs eleven_v4, language_code en). Transcribe-back 1.0 on all 11. Median pitch: mothers/wives 208–258 Hz, men 109–158 Hz.
  Voices: c. 200 BC mother A_MARY, elder B_JOHN; c. AD 200 wife F_GWEN, farmer C_FRED (H_CLERK reads in received pronunciation, the wrong accent
  for an English-speaking Welsh farmer; G_DAI measured a 200–275 Hz median, a gender risk; C_FRED is male at ~123 Hz and was designed as a man long in South Wales).
- es: 11 lines. c. 200 BC mother J_ELENA (ElevenLabs, the account's only native Rioplatense voice); elder, AD 200 wife and farmer by OpenAI gpt-4o-mini-tts
  (onyx / coral / ash) with Rioplatense instructions, because the ElevenLabs account is full and Gemini TTS on Vertex answered 403. Transcribe-back 0.90–1.0;
  five lines sped up 1.08–1.12× to fit. Accents not checked by ear.
- Files: assets/F002/native/{en,es}/sNN.mp3 (the voiced line) and sNN.adj.wav (OmniHuman input: 0.4 s lead, padded to the shot length).
  Shot lengths, stills, prompts and voices per shot: assets/F002/native/plan.json. Scripts: assets/F002/native/render.py, assemble.py.
- Estimates at $0.105/s: en ≈ $9.0 (85.9 s of output), es ≈ $9.9 (94.6 s). cy = reuse clips/F002.v6.webm (Welsh OmniHuman renders), $0.
- Pipeline test: assemble.py en --standin (the Welsh renders in place of the English ones) built a 133.8 s 720p VP9 file of 22.2 MB, under 25 MB. Not published.
- Shot 1 in the en/es cuts: the v6 date card names Welsh as the spoken language, so assemble.py redraws it from the raw image-to-video shot with a caption in that language (en: "Spoken in English; they spoke Brittonic, the ancestor of Welsh"). The AD 200 card (shot 12) is bilingual and is shared as is.
- Budget: the box's render meter showed $0 of $10 because it does not count these direct renders; the film's own spend logs already held $26.34
  for 30 Oct (UTC), spent 00:00–03:20Z on the Door 2/Door 1 lip-sync work before the $10/day pacing rule. So renders wait for 31 Oct.
  render.py enforces the daily limit from those logs (--day-limit 10, --cap per run).
- Next: 31 Oct: `TAB_TASK_ID=<task> python3 render.py en --cap 9.6` (11 renders, one at a time, ~7 min each), check 3 frames per shot, then
  `python3 assemble.py en` → F002.v7.en.webm. 1 Nov: es the same way (the cap may leave 1–2 shots for the next day). Then the manifest switch in RERENDER-QUEUE JOB 1.

- 31 Oct 2026 12:23Z (health check e0ba6a92): the 31 Oct `render.py en --cap 9.6` never ran (no movie worker since 30 Oct 08:30Z: every occurrence skipped on disk < 2 GB and a rolling all-vendor spend figure). en shot 2 is now RENDERED under Quality bar v2 (oh_en/s02.mp4, take 2 of 2; take 1's eyes drifted to the lens; QA gate PASS; $1.68 for both takes, logged in F002native/spend.jsonl). plan.json now carries prompt_v2 per shot and language and render.py uses it; assemble.py is 24 fps + two-pass VP9 + -16 LUFS/LRA 7. Next: `render.py en --cap 9.6` renders the other 10 en shots (≈ $8.0), then assemble.py en, then tools/qa_gate.py on the result. Before es: re-edit still iL1 (the row of candle-like lights behind the mother reads as string lights). HubSpot (task id kept off the public repo) not updated by this check (next movie run appends the line).

### Door 2 (F002, script v1.0.2; shot list work/cedwyn-movie/F002v6/F002.v1.0.1.json + the v1.0.2 recast) — FIRST
| shot | s | kind | per language? |
|---|---|---|---|
| 1 | 6.32 | Kling i2v, dawn homestead + caption | shared |
| 2 | 9.0 | talking: A_MARY (roundhouse mother) | own render per language |
| 3 | 7.0 | talking: B_JOHN (Iron Age elder) | own render per language |
| 4, 5 | 5.8 each | Kling i2v | shared |
| 6 | 5.0 | talking: A_MARY | own render |
| 7 | 7.0 | talking: B_JOHN | own render |
| 8 | 8.0 | talking: A_MARY | own render |
| 9 | 5.8 | Kling i2v | shared |
| 10 | 8.0 | talking: B_JOHN | own render |
| 11 | 8.0 | talking: A_MARY | own render |
| 12 | 6.32 | Kling i2v (AD 200 date card) | shared |
| 13 | 11.0 | talking: AD 200 farmer (recast, H_CLERK voice in v1.0.2) | own render |
| 14 | 11.0 | talking: AD 200 wife (recast, F_GWEN voice) | own render |
| 15 | 5.8 | Kling i2v | shared |
| 16 | 11.0 | talking: AD 200 wife | own render |
| 17 | 6.0 | talking: AD 200 farmer | own render |
| 18 | 7.04 | Kling i2v | shared |
| 19 | 5 | end card | shared (text per language) |
Talking: 11 shots, 91 s. Shared: 7 i2v shots (42.9 s) + end card.
- cy: REUSE the existing Welsh OmniHuman renders in clips/F002.v6.webm (already a native Welsh performance; voices designed Welsh). $0.
- en: 11 new lines in eleven_v4 with the characters' Welsh-accented English voices → 11 OmniHuman 2.0 renders from the same 16:9 stills. ≈ 90 s × $0.105 ≈ **$9.5**.
- es: 11 new lines in Rioplatense Spanish with native Spanish voices (designed, not the Welsh voices) → 11 renders. ≈ 94 s × $0.105 ≈ **$9.9**.
- Voices/TTS ≈ $0.4. Retake allowance ~15% ≈ $3.
- **Door 2 total ≈ $20–23.** Output: clips/F002.v7.webm (cy, = v6 Welsh), clips/F002.v7.en.webm, clips/F002.v7.es.webm, each carrying only its own audio.

### Door 1 (F001, script v0.3.0, cut v2) — SECOND
- Talking close-ups needing their own render per language: cut shots 2, 5, 6, 8, 13, 14 (S2v5/oh/f1s*.v2.mp4; the Welsh renders cost $6.94 on 30 Oct ≈ 66 s; spend.jsonl).
- Shared, no render: shot 1 title still, the wide i2v shot, document inserts and stills. Lines heard over shared shots only need the new language's audio track.
- cy: REUSE the 30 Oct Welsh OmniHuman close-ups (native Welsh). $0.
- en: ≈ 61 s × $0.105 ≈ **$6.4** (English lines run ~8% shorter by subtitle cue time). es: ≈ 66 s × $0.105 ≈ **$6.9–7.2**.
- Voices ≈ $0.3; retakes ≈ $2. **Door 1 total ≈ $14–16.**
- The separate Door 1 all-motion redo (stills → i2v, ≈ $6–8, see below) can be done in the same pass; then the shared shots are new for all three languages at once.

### Both doors ≈ $34–39 at list prices (bible/MODELS.md: OmniHuman 2.0 $0.105 per output second). NOT CHECKED against receipts.
Not checked / risks: (1) the voice account was at its custom-voice limit on 29 Oct (the Spanish elder used B_JOHN's voice); native Spanish voices may need a slot freed or the Gemini TTS fallback. (2) es/en line lengths estimated from subtitle cue spans (F002.v6 cy 93.6 s, en 90.0 s, es 94.3 s; F001 cy 136.2, en 124.9, es 136.3). (3) The cy reuse assumes the owner counts the existing Welsh OmniHuman renders as the Welsh performance; if not, add ≈ $9.6 (Door 2) and ≈ $6.9 (Door 1).

### When a door's three native videos are live
Manifest: move the current top-level cut into `cuts` as its sub-version (Door 2: 0.0.1-0.0.5 with its `video`; Door 1: 0.0.1-0.0.2), set the new entry `version: "0.0.1"` with `clip` = the cy video and `video: {cy, en, es}`, remove `next_version`, run tools/download_variants.py N --upload. The page then shows #v0.0.1 free (default) followed by the older chips. Append a dated line to HubSpot (task id kept off the public repo).

### Budget
Spend only what the 24 h render budget allows; when it is $0, prepare everything (lines, voices, audio) and wait — log the wait as an internal note in work/problems/QUEUE.md (P-056), never to the owner.

---

> **CURRENT RULES (29 Oct 2026).** Owner, WhatsApp 16:04 GMT 29 Oct: the film is a scene-by-scene recount and recreation of what most likely happened, in strict chronological order, with no fourth wall (full text and meaning: BIBLE.md "IN-PERIOD RULE"). This replaces the narrator-on-camera rule from scene 3 onward. Still in force: OmniHuman 2.0 (`bytedance/omnihuman/v2`, $0.105 per output second) used moderately, only for a character speaking on camera to another character, quality first, minimal spend; NEVER the free Piper/Wav2Lip route (rejected 27 Oct 13:35); Welsh spoken before about 1970 with en/es subtitles (Rioplatense Spanish); Welsh accents; no likeness of real family members; banned public words; never name the producer; no heraldry; no villa shown; the hill is inland.

# RERENDER-QUEUE (rewritten 29 Oct 2026, in-period plan v2.0.0)

## Published scenes (keep as they are)
| frame | title | status |
|---|---|---|
| F001 | Place-names before the deeds | KEEP (owner: "the first 2 scenes are ok") |
| F002 | The hill before the records (c. 200 BC + c. AD 200; former F003 merged in) | PUBLISHED v1.0.0 29 Oct 23:5x, fully animated, no fourth wall |
| F003 | (merged into door 2 on 29 Oct at the producer's word; no longer a door) | RETIRED |

F003 is the first in-period scene (29 Oct 2026). Nothing to REDO. Any clip found later for a frame 3+ made under the old narrator scripts is REDO.

## Next scenes, in order (dates and places from FRAMES.json `moment`; full list SCENE-LIST.md)
| frame | date | place | title | script |
|---|---|---|---|---|
| 4 | c. 650 | Monastic burial ground on Llandough hill, above the Ely | Graves above the Ely | v0.4.0 written |
| 5 | c. AD 1000 (10th–11th century) | Churchyard of the monastery at Llandough | The Irbic cross | v0.4.0 written |
| 6 | c. 1786 | Fields of the Herbert of White Friars estate, Llandough-juxta-Penarth | The surveyor's chain | v0.4.0 written |
| 7 | c. 1790 | Tŷ Mawr farmyard, Llandough | Two plans of Tŷ Mawr | v0.4.0 written |
| 8 | 1824 | Bute estate office, Cardiff | Plan 19: Cedfin or Tŷ Mawr | v0.4.0 written |
| 9 | 23 December 1864 | Kitchen of Great House Farm (Tŷ Mawr), Llandough | Amy Williams dies | v0.4.0 written |
| 10 | 9 April 1872 | Vestry of St Dochdwy's Church, Llandough | A new church, a rate book | v0.4.0 written |
| 11 | October 1876 | Vestry of St Dochdwy's church, Llandough | The Poor Rate of 1876 | v0.4.0 written |
| 12 | 1877 (month not recorded) | Bute estate office, Cardiff | A Notice for Great House | v0.4.0 written |
| 13 | 4 April 1881 (census of 3 April) | Farmhouse kitchen, Great House Farm, Llandough | Census Night at the Farm | v0.4.0 written |
| 14 | August 1889 (between 11 and 16 August) | Penarth police court | Apples Over the Hedge | v0.4.0 written (29 Oct, HubSpot (task id kept off the public repo)) |
| 15 | 16 August 1889 | Llandough village street, by the post office | The Paper Comes to Llandough | to write |
| 16 | 7 June 1892 | The village inn taproom, Llandough | Geese in the Echo | to write |
| 17 | Late July 1894 | Farmyard, Great House Farm, Llandough | Swine Fever at Great House | to write |
| 18 | 15 May 1897 | Llandough hill, looking over the Ely and the marshes toward Penarth | Wireless at Lavernock | to write |
| 19 | 15 May 1897 | The village inn taproom, Llandough | Mr. Williams of the Engineering Department | to write |
| 20 | July 1904 | Bute estate office, Cardiff | Occupier Since 1855 | to write |
| 21 | 23 February 1905 | A solicitors' office acting for the Bute estate, Cardiff | Bute Conveys to the Corporation | to write |
| 22 | 1 April 1907 (Easter Monday) | Great House Farm yard, Llandough | Easter Monday Shoot at Great House | to write |

Scripts F003–F013 were rewritten in-period (v0.4.0, 29 Oct; not rendered; Welsh/Spanish machine-written for native review). The narrator versions are kept in backup-2026-10-29-inperiod/scripts for reference only. Keep scripts 10 frames ahead: next to write is F015 (next to render: F004).

## Order
1. F003 onward, one scene per run, in FRAMES.json order, from its v0.4.0+ script: date-and-place card, stills with slow moves carrying ambience and captions, 3–5 OmniHuman talking shots of characters speaking to each other in the moment. Never a narrator, never a voice over a still, never the archive reading room (s08).
2. Spend only inside the render budget left; if it is $0, prepare everything and wait (log the wait to work/problems/QUEUE.md).

— the owner's Tab agent


## 29 Oct 2026 23:55Z — door renumbering (worker 64b98b2d)
Scene 3 merged into Scene 2. frames.json 2.1.0 has 147 items: each item keeps its script id (F004, F005 …) but its door number n moved up one (F004 = door 3, F005 = door 4 …). When rendering the next door, use the item's n for the manifest entry and its id for the script file. Next to render: F004 (door 3, c. 650).

## REDO F002 v1.0.1 — distinct AD 200 cast (the owner 23:51 29 Oct)
Re-cast the Romano-British farmer + wife as NEW people (not A_MARY / B_JOHN; different faces, ages, hair; Romano-British dress: tunic and cloak with brooch, no heraldry), new 3/4-profile stills, OmniHuman 2.0 for rL1, rL2, rL4, rL5 using F003v1/audio Welsh lines, Kling 2.5 turbo for aST2; re-cut S2v5 timeline (same start times) and re-upload as clips/F002.v5.1.webm. About $5. Licence: only our AI reconstructions may be animated.


## 30 Oct 2026 02:40Z — owner steer (worker c52025d8)
- REDO F002 → v1.0.2 (door 2): shots 16/17 had swapped faces vs voices (woman's line lip-synced on the man and vice versa, all three tracks); AD 200 couple re-voiced (H_CLERK farmer, F_GWEN wife — new voices, not the Iron Age pair's) and 4 talking shots re-lip-synced. IN PROGRESS by this worker.
- REDO F001 (door 1): every still / photo slide becomes motion video (i2v for scenery, OmniHuman for speech, documents filmed as physical objects). NEXT after door 2; waiting for budget if the 24 h render budget is spent.
- PARKED F004 (door 3, c. 650 'Graves above the Ely'): rendered 30 Oct 02:20Z (clips/F004.webm, audio/F004.*.webm, subs/F004.*.vtt, stills/F004.jpg are on cedwyn-movie main) but NOT opened: it has 6 stills with slow moves, which the new no-stills rule forbids, and its voices (G_DAI monk, F_GWEN woman) clash with door 2's new AD 200 voices. To finish: i2v the 6 stills in F004v1/stills (st1b, st2, st3b, st6b, st8 + end card) with Kling, re-voice the monk/woman with voices not used in door 2 (and re-lip-sync the 5 OmniHuman shots), re-mux, then add the manifest entry. Script v0.4.1, stills, portraits, mix recipe in work/cedwyn-movie/F004v1/.

- 03:30Z DONE F002 v1.0.2 (door 2): faces/voices fixed, AD 200 couple re-voiced, cy/en/es lip-synced videos (clips/F002.v6{,.en,.es}.webm). Downloads re-run.
- WAITING FOR BUDGET — F001 (door 1) all-motion redo + en/es lip-sync videos: the 24 h render budget ($10) is spent (door 3 render $5.17 + door 2 fix $4.68). Plan: i2v (Kling 2.5 turbo) for every still/slide shot, archive scans as filmed physical documents, OmniHuman for speech, then Kling LipSync for en/es. Estimated ≈ $6–8.
- WAITING FOR BUDGET — F004 (door 3) finish (see PARKED above) ≈ $3–5.
- 30 Oct 14:05Z root: 2ea6e095 occurrence skipped — render budget for this UTC day spent ($26.34 today vs $10 cap) and disk 1.8 GB (<2 GB rule). Next paid render after 31 Oct 00:00Z budget reset; P-056 holds the 31 Oct 02:02Z render.py en --cap 9.6 + assemble.py en.

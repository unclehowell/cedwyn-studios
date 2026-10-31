> Ported from the cedwyn-movie flywheel bible on 31 Oct 2026. The studio packages under studio/ are the working copy; this file is the reference text. File paths such as `cast/A_MARY.jpg` now live in R2 under `studio/characters/<ID>/look/`, sets under `studio/sets/`.

# CEDWYN — consistency bible (v1.0.0, 25 Oct 2026)

*A tab.bot production.* Everything a daily scene run needs so that the last frame shows the same people, voices, buildings and landscapes as the first.
Files: `bible/cast/`, `bible/sets/`, `bible/voices/`, `bible/VOICES.json`, `bible/test/` (the test clip).

## 1. The repertory company

A small company of ten actors plays the people of Llandough in every age — the Williams line, the village voices, the officials. One fixed reference portrait per actor;
an age or costume change is always an **edit of that portrait**, never a new face. Real family members are played by these actors with **no attempt at likeness** until the
family supplies photographs and approves. The present-day researcher is never named: he is "the Grandson". No heraldry anywhere (crests, arms, shields, emblems on chairs or seals).

| id | role | plays | reference | voice (ElevenLabs, eleven_v4, cy/en/es) |
|---|---|---|---|---|
| A_MARY | the Williams woman | the 20th-century Williams woman and the earlier Williams women (Amy Williams 1860s); the roundhouse mother in the prologue (invented portrait `cast/A_MARY_ironage.jpg`, never a real photograph) | `cast/A_MARY.jpg` | `uZ2F64pQ4awvfM38w9V9` |
| B_JOHN | the Williams man | the John Williamses (1841–1949); Iron-Age elder (`cast/B_JOHN_ironage.jpg`), villa steward, monk in the prologue | `cast/B_JOHN.jpg` | `ft0WkOZmCF3NFIbyp280` |
| C_FRED | the in-law | the 20th-century in-law | `cast/C_FRED.jpg` | `XZLLk8LKa4NX4HsuCPiS` |
| D_BILLY | the son / the Grandson | the son, as boy and man; in the 2020s "the Grandson" (never named) | `cast/D_BILLY.jpg` | `bi1ppGIASFluT4PbdRza` |
| E_AGENT | the Man from the Estate | offices only: Bute estate agent, company agents, solicitors, overseers, Land Registry and council officers | `cast/E_AGENT.jpg` | `2Jm4mkkEDFemeO085c56` |
| F_GWEN | the village voice (fictional) | Gwen, who reads the papers aloud in every era | `cast/F_GWEN.jpg` | `UmQyXL5FYPCIbuUQZKqK` |
| G_DAI | the landlord (fictional) | Dai, innkeeper/carter, Gwen's sparring partner | `cast/G_DAI.jpg` | `bjneJtpl97NGdlhAINbN` |
| H_CLERK | the Court | clerks, magistrates and judges; lines quote judgments verbatim | `cast/H_CLERK.jpg` | `nzPzKJE9RrymxViKMFhm` |
| I_NIA | the Archivist (fictional) | Nia, who reads each document with the Grandson | `cast/I_NIA.jpg` | `XEKRPEMYQPpow8lb1XZN` |
| J_ELENA | the Patagonian (fictional) | Elena, guide at Puerto Madryn (Argentina frames) | `cast/J_ELENA.jpg` | `VJAA1A5gQklMXZjm0smO` |

Era edits made so far: `A_MARY_1974.jpg` (aged ~60, nano-banana-pro edit — canonical for 1960s–80s), `B_JOHN_1890s.jpg` (gpt-image edit). Make each new era once,
check it against the reference, save it as `cast/<ID>_<era>.jpg`, and reuse it for every later scene of that era.

## 2. Voices

One designed voice per actor, used for all three languages so the timbre never changes (`VOICES.json`): model **eleven_v4** with `language_code` cy / en / es,
settings stability 0.5, similarity 0.8, style 0, speaker boost on. Welsh fallback for a line that fails transcribe-back: Gemini 3.8 Flash TTS (voice Kore), accepting a timbre change.
Every line is transcribed back (OpenAI gpt-4o-transcribe) and must match the script at ≥ 0.8; years are spelled out in words.

## 3. Sets and eras

| id | set | reference |
|---|---|---|
| s01 | Great House Farm / Tŷ Mawr farmhouse exterior and yard (c.1850–1974) | `sets/s01.jpg` |
| s02 | the farmhouse kitchen (inglenook, flagstones, dresser) | `sets/s02.jpg` |
| s03 | St Dochdwy's church and churchyard, Llandough | `sets/s03.jpg` |
| s04 | Llandough village street and green | `sets/s04.jpg` |
| s05 | the village inn (taproom) | `sets/s05.jpg` |
| s06 | a Cardiff office (Bute estate office / solicitors / company office, by era) | `sets/s06.jpg` |
| s07 | a courtroom (magistrates, county court, High Court, Court of Appeal, by era) | `sets/s07.jpg` |
| s08 | the archive reading room (modern records office) and the Grandson's desk | `sets/s08.jpg` |
| s09 | Llandough hill landscape over the Ely, Leckwith woods and Cardiff Bay | `sets/s09.jpg` |
| s10 | prologue: the hill in prehistory/Roman/early-medieval times (roundhouse, villa, monastery) | `sets/s10.jpg` |
| s11 | the farmhouse 1974–88: aged, threatened, development around | `sets/s11.jpg` |
| s12 | the site after demolition (1988–2026): housing estate, verge, green | `sets/s12.jpg` |
| s13 | Chubut arid steppe, Patagonia (Argentina): dry tussock grass, gravel, low scrub, ochre and dun; no flowers, no lush green (27 Oct rule) | `sets/s13.jpg` |

Rule: **every era of a set is an edit of its establishing reference** (s11, the farmhouse c. 1980, is an edit of s01 — same building, same viewpoint, aged, housing behind).
Next improvement: condition s01/s02/s11 on the real archive photographs of Tŷ Mawr held in the Cedwyn media register (measured survey 1974, press photographs 1974–88) so the
farmhouse matches the real building; until then the farmhouse is an evocation, not a likeness.

Eras: prologue (s10, the hill before the records) → 1824–1915 Bute years (s01 c.1900, s02, s03, s04, s05, s06 19th c.) → 1916–1968 (s01/s02 mid-century, s06 20th c.) →
1969–1988 (s11 threatened farmhouse, s07 courts, s06 company offices) → 1988 onwards (s12 the site after demolition) → 2026 (s08 archive, s12, s04) → Argentina (s13).

## 4. Palette and lens

Muted Glamorgan greens, slate grey, lime-wash white, oak brown, warm tungsten interiors; gold (#d4b25a) only for titles and date cards. 35 mm lens look, natural light,
slight film grain, shallow depth of field for talking close-ups, slow push-ins on stills, no handheld shake. Date/era card at the start of each scene; "A tab.bot production" end card.
Documents appear as props on the table; the real quoted words are overlaid by HyperFrames with their evidence id — never invented legible text in a generated image.

## 5. Per-scene recipe (proved in pre-production)

1. Read `PROMPT.md` first, then the frame's script (en/cy/es), cast and set ids, and the frame's HubSpot task (latest version).
2. Stills, 16:9 (1920×1072 → 1280×720), 8–14 per scene, always edits of the bible references (people: nano-banana-pro/edit for age, gpt-image-2.5/edit for costume/scene; places: gpt-image-2.5/edit of `sets/sNN.jpg`). Look at each one against its reference. ≈ $1/scene. Keep ≤ 4–6 jobs in flight.
3. Dialogue audio: every line × 3 languages with the actor's voice (eleven_v4), transcribe-back QC, joined per language. ≈ $0.3–0.5/scene.
4. Talking shots: **OmniHuman 2.0** (`bytedance/omnihuman/v2` on fal; image + audio → talking video; $0.105 per output second; ~7–8 min per render; generated faces accepted) for 2–4 close-ups of 5–12 s, English lip-sync; cy/es are dubbed over them. Inputs must be https URLs (host audio through `fal-ai/ffmpeg-api/loudnorm`). Make the still 16:9 so the output is widescreen.
5. Ambient motion (optional): Kling 2.5 turbo or Seedance image-to-video for 5 s landscapes; otherwise slow push-ins in HyperFrames.
6. Assembly: HyperFrames (`npx hyperframes render`, the hf-series kit, `HFW=1` under memory/disk pressure) at 1280×720 — clips, stills, document overlays with their evidence ids, date card, end card. No burned-in subtitles.
7. Mux: VP9 crf 32–34 (raise to 36 near the limit), three Opus tracks (cym, eng default, spa) and the WebVTT tracks embedded; sidecar `subs/Fnnn.<lang>.vtt` from the real TTS timings; `audio/Fnnn.<lang>.webm` per language for the page; `stills/Fnnn.jpg` poster. Under 25 MB, else split into `Fnnn-a` / `Fnnn-b`.
8. QC: ffprobe (90–150 s), `audio-proof.mjs inspect` (−16 to −20 LUFS, no unscripted silence > 1.5 s), three frames compared with the portraits, transcribe-back per language, banned-word grep on all subtitles, every event id of the frame cited.
9. Cost ≈ $4–5 per scene (≈ $600–750 for 148 frames); machine time ≈ 25–40 min per scene.

## Chronology rule (the owner, 11:45 GMT 26 Oct 2026) — read before every script and render

- Tŷ Mawr is first named in the record we have found in the 1824 David Stewart survey of the Bute Glamorgan estates (EV-0211). In the family's account, Tŷ Mawr was acquired in 1667.
- Never present "the 1547 lease" or "the 1552 Bute deed" as Tŷ Mawr records. Bute estate and other third-party documents are never shown as records of Tŷ Mawr before 1824: on screen they are Bute (or third-party) papers whose application to Tŷ Mawr is under forensic examination, and the Bute freeholds are under forensic examination for validity.
- Outside narratives (websites, catalogue summaries, secondary books) are tested on screen, not repeated. Our film asserts and defends our evidence and our interpretation.
- Names have been played on (Cydwin, Cydfin, Cedfin, Ked Fen, Tŷ Mawr, Great House, Great House Farm; Llandough-juxta-Penarth CF64 vs Llandough near Cowbridge CF71): the register is the e-book "Enwau" on cedwyn.bucklerfamily.estate/ebooks/.
- F006 ("A thousand-year lease") is re-titled and must be rewritten to this rule before it is rendered; F005's hand-over line and F006's continuity are updated.

## Image exclusion rule: Kissed Frogs (27 Oct 2026, owner instruction 02:34 GMT)
Images labelled "Kissed Frogs" in the Wayback Vault (not of the farm; source thought to be an FOI disclosure; not checked), and every image the Vault
has withdrawn as not of the farm (wayback/images/facebook/unrelated.json, the whole FB album 623829877754485), must never be used as a source
for farm imagery, digital editions (nft-art), quote cards, film stills/sets (cedwyn-movie) or any other generated media. Check every candidate
source path against /home/user/tab/work/kissed-frogs/excluded_images.json before using it (27 Oct 03:00: the whole album was purged
from every public view at the owner's word; the private record is work/kissed-frogs/withdrawn_fb_album_do_not_publish.json). Only images the owner has confirmed as the farm, or catalogued records (maps, plans,
documents) of the farm, are valid sources. — the owner's Tab agent


## Geography rule: Llandough hill is inland (27 Oct 2026, owner instruction 06:48 GMT)
Llandough hill is inland — never describe the farm/hill as by the sea or on the coast; it overlooks the Ely, the marshes and the estuary.
Applies to every language (en/cy/es) in scripts, subtitles, narration and image/shot prompts: no "by the sea", "on the coast", "seaside", "shore",
"the sea throws" (cy "môr", "arfordir", "glan y môr"; es "mar", "costa", "orilla"). Use estuary / marsh / river / weather wording. In stills, the water
below the hill is the distant estuary and the Ely marshes, not open sea at the foot of the hill. Even 2,200 years ago (higher, wetter marshes) the
hill was never coastal. First applied: F002 v0.1.2 (elder's line "the sea" -> "the weather"). — the owner's Tab agent


## PERIOD ACCURACY rule — every frame (27 Oct 2026, owner instruction 06:59 GMT)
Owner, verbatim: "Don't use still photos with voice overs if you can, have them speak and be animated using ByteDance Omnihuman 2.0 . Don't show a roman villa in the scene 2200 years ago. That makes no sense. And dont have the character from 2200 years ago talk about title and deeds and occupancy or anything that will have concerned them. They'd be speaking welsh and just being very pramative humans then. Actually study them from that era to know"
1. **Research the era first.** Before writing or rendering a frame, write `research/<era>-<frame>.md` from primary/academic sources (excavation reports, Amgueddfa Cymru, Cadw, Coflein/HER, university projects, contemporary texts), citing each point and marking interpretation as such. F002 example: `research/iron-age-F002.md`.
2. **Nothing from a later age.** No buildings, objects, materials, animals, crops, clothes, tools, writing, money, religion or landscape features that did not exist in that year (e.g. no villa, coins, crosses or stone rectangular buildings in the Iron Age; no tarmac or pylons in 1850). Every era of a set is an era edit checked against the research, not just against the previous frame.
3. **People speak only of what their own time cared about.** No modern legal ideas (title, deeds, ownership, occupancy, boundaries, rent, courts) before they existed, no hindsight or prophecy about what the place will become, no narrator's knowledge in a character's mouth. Iron Age people talk of weather, harvest, animals, food, cloth, children, kin, the seasons, water. Later eras use the concerns and words the records of that era show.
4. **Language of the time.** Speech is in the language the people spoke; where that language is lost (Brittonic), use its closest living descendant (modern Welsh), lip-sync to it, and say so once on screen. Welsh is the primary track for Welsh-speaking eras.
5. **Talking characters are animated, not stills with voice-over.** Every on-screen speaker is an OmniHuman 2.0 talking shot wherever the budget allows; lines that cannot be afforded play off-screen over MOVING shots (image-to-video), never over a still. A still may appear only without a voice (title, document insert, a brief wordless establishing hold).
6. **Llandough hill is inland** (see Geography rule): the Ely, its marsh and the distant estuary below; never sea at the hill's foot.
7. **Real people:** no likeness of real family members except where the owner supplied a photo and approved it for that character; prologue/ancestral roles use the invented portraits.
Check before rendering: grep scripts, VTTs and image prompts (cy/en/es) for out-of-period words (villa, deed, title, owner, lease, rent, sea, coast...), and look at every still for later-period objects. — the owner's Tab agent


## the owner 27 Oct — accents, language, on-camera narrators (hard rules, 27 Oct 2026)

Owner steer at 11:50 and 11:52 GMT: *"At least have a think welsh accent from everyone until 1970, except the non welsh."* These rules are above every older section.

1. **Thick Welsh accent.** Every Welsh character and both narrators (Nia, the Grandson) speak with a **thick** South Wales accent in any scene set before about 1970, and the narrators keep it in the 2020s. Non-Welsh characters keep their own accents: Estate, BP and Land Registry officials, outside bailiffs, English officials, Elena (Argentine).
2. **Welsh first before ~1970.** Welsh characters speak Welsh (`cy`) on camera, lip-synced to the Welsh line, with en/es **subtitles** led by an `[in Welsh]` marker. No dubbed English or Spanish track for period lines. The 2020s narrators speak English. Each script line carries `spoken` and `accent`, and each frame carries `spoken_language` (FRAMES.json v1.2.0).
3. **Narrators on camera.** Nia and the Grandson appear as OmniHuman 2.0 talking shots, lip-synced. **Never a voice-over on a still.** A shot with a voiced line is OmniHuman (one face per render) or a moving i2v shot with the line off-screen, never a still.
4. **The Grandson's face.** D_BILLY in 2020s frames is the Grandson with the invented cast face (`bible/cast/D_BILLY.jpg`). He never gets a real person's likeness. William Buckler's real photo (approved 25 Oct) appears only in William's own-era frames.
5. **Voices (cast list).** Library voices are free to add; each recast passes an accent check by an audio-capable model on one line **before** any OmniHuman spend. If a library pick reads mild, design a new "very thick South Wales" voice (costs credits; next budget window) and record its id in `bible/VOICES.json`.

| actor | voice_id | voice | status |
|---|---|---|---|
| A_MARY | `73fZMjboCm1aBVyxTbBp` | Hannah (Welsh female, library) | recast from uZ2F64pQ4awvfM38w9V9 (gentle lilt) |
| B_JOHN | `ft0WkOZmCF3NFIbyp280` | existing design, strong South Wales | kept |
| C_FRED | `XZLLk8LKa4NX4HsuCPiS` | existing | kept for now; his origin is open. If the record shows he was Welsh-raised, recast to thick South Wales |
| D_BILLY | `EmvLmNNZPnr2cOTaYrUc` | Rhys Horler (Welsh male, library) | recast from bi1ppGIASFluT4PbdRza (modern Cardiff); the Grandson narrator |
| E_AGENT | `2Jm4mkkEDFemeO085c56` | existing, RP English | kept (non-Welsh) |
| F_GWEN | `UmQyXL5FYPCIbuUQZKqK` | existing design, strong Valleys | kept |
| G_DAI | `bjneJtpl97NGdlhAINbN` | existing design, broad South Wales | kept |
| H_CLERK | `nzPzKJE9RrymxViKMFhm` | existing, RP | kept (non-Welsh official) |
| I_NIA | `EoMKQ1XHxZPJ6KVTvPL3` | LOUISE (Welsh female, library) | recast from XEKRPEMYQPpow8lb1XZN (mixed North/South); the archivist narrator |
| J_ELENA | `VJAA1A5gQklMXZjm0smO` | existing, Argentine | kept (non-Welsh) |

   Spare Welsh library candidates: Chris `aKQdyEogZx5VoND0oujS`, Flameheart `698IrvLv5nahuUHY2tLv`, Zak `004KTmksPwLFhbYi3ENc`, `wUkGqD7qevNIshEdEC5s`, Daniel `sBU90Bu4NCleWDoNkGog`.
6. **Subtitles.** Each cue has at most 2 lines of 42 characters, at most 20 characters per second, and lasts 0.83–7 s. Welsh-spoken cues start with `[in Welsh]`. Check with `work/bizdev/skills/tools/subtitle_check.py` before upload.
7. **Hook.** A hook question asked on camera in the first 5 s. No catalogue IDs spoken in the first 30 s; they go on the document overlay after 0:30.
8. **No villa shown** (see `research/roman-F003.md`). Patagonia is arid steppe with no flowers. The geography rule (inland hill) stands.

— the owner's Tab agent

## CAST CHANGES WITH THE CENTURY (the owner, 29 Oct 2026 23:51)
When a scene jumps in time, the people on screen are different people (descendants or newcomers), never the same faces. Each period gets its own cast reference sheet in bible/cast/<period>_*.jpg; never edit one period's stills from another period's cast refs.

# STUDIO.md — the cedwyn-studios spec

Read this once and you can advance the film by one unit with no other context. Version 1.0.0, 31 Oct 2026.

## 1. Ideas

1. **A scene is data.** `studio/scenes/F###/` holds `scene.json`, one `shots/S##/shot.json` per shot, and `manifest.json`. Nothing about a scene lives only on one computer.
2. **A unit is the smallest piece of work.** A talking shot has one unit per language (`cy`, `en`, `es`): each language is its own performance, lip-synced to its own audio (the per-language rule in docs/QUALITY-BAR-v2.md). Every other shot has one `shared` unit.
3. **A render is a function.** Its output is fixed by its inputs: `input_sha256 = sha256(canonical JSON of {model, prompt, sha256 of the still, sha256 of the audio})`. If the manifest already maps that input hash to an output that is in the store, the render is skipped. Nothing is paid for twice, and any computer can resume where another stopped.
4. **Media is never in git.** Images, audio and video go to GitHub Releases (one release per scene; R2 only as a mirror); git holds the keys, hashes and CIDs. Files in git stay under 400 KB.
5. **One unit per run, then commit.** Small commits (at most 4 files), no force-push. If two agents race, the second re-reads and retries.

## 2. Files

### scene.json
| field | meaning |
|---|---|
| `id` | `F###`, the frame id from `studio/frame-map.json` |
| `title` | `{en, cy, es}` |
| `date`, `place`, `present` | the one dated moment the scene recreates and who was there (cast slot → role) |
| `set` | a set id from `studio/sets/sets.json` |
| `sources.catalogue_ids` | chronology and evidence catalogue ids (EV-, CH-, PX-, MR-) the scene rests on; `sources.urls` site pages |
| `moment` | the frame map's moment record: summary, anchor, captions, basis |
| `languages`, `spoken_language`, `subtitles`, `accent` | language rules for this scene |
| `language_order` | optional: the order the runner works through languages (Door 2: en, es, cy) |
| `status` | `scripted` → `in_progress` → `published`; or `held`, `superseded` |
| `shots` | shot ids in play order |
| `ambience` | optional sound beds: `{key, mode: bed|at_shot, shot, volume, …}` |
| `published` | where the current public cut lives |

### shot.json
| field | meaning |
|---|---|
| `type` | `talking` (OmniHuman 2.0 lip-sync), `still-move` (slow ffmpeg move on a still, free), `i2v` (Kling image-to-video), `card` |
| `speaker` | the cast slot speaking (a folder in `studio/characters/`) |
| `lines` | `[{who, cy, en, es, cite}]` the exact words per language |
| `direction`, `captions` | what the shot shows; on-screen captions |
| `still` | `{prompt, image, refs, origin}`: the still's prompt and the `r2:` key of the approved still |
| `seconds`, `start`, `published_window_v6` | timing |
| `render.per_language.<lang>` (talking) | a unit: `status`, `text`, `voice`, `line` (voiced mp3), `audio` (the OmniHuman input wav: 0.4 s lead, padded to the shot), `speech_s`, `shot_s`, `prompt`, `take`, `qa`, `request_id` |
| `render.shared` (other types) | a unit: `status`, `source` / `clip`, timing fit, per-language caption |
| `status` | roll-up of the units: `todo`, `in_progress`, `done`, `superseded`, `blocked` |

**Unit status:** `todo` → `prepared` (line voiced, prompt written) → `rendered` (take stored, waiting for QA) → `done` (QA PASS). `blocked` carries `blocked_by`. `superseded` is history.

**The next step for a unit** (tools/studio.py `step_for`): no still → `still`; talking without audio → `line`; talking with audio → `take`; still-move → `move`; i2v → `i2v`; card → `card`; rendered → `qa`.

### character.json
`role`, `plays`, `likeness_rule` (invented faces only, never a real person's likeness; a new century means new people), `look.reference` and `look.era_edits` (`r2:` keys; an era change is an edit of the reference portrait), `voice` (vendor, `voice_id`, `model_id`, `settings`, `design_prompt`, per-language `language_code` and transcribe-back score, `accent_notes`).

### manifest.json
`objects`: `{key: {sha256, bytes, content_type, origin, at}}` for every stored file of the scene. `renders`: one row per render: `{shot, unit, step, model, input_sha256, inputs, output_key, output_sha256, seconds, usd, request_id, at}`. Characters, sets and the chronology are in `studio/manifest-shared.json`.

## 3. Media store

**GitHub Releases are the primary store** (since 31 Oct 2026). One release per scene holds that scene's media as release assets (tag `media-F###`); characters, sets, chronology and voice tests live in `media-shared`. An asset's name is its key below the scene folder (or below `studio/`) with `/` turned into `__`, so every key has one public URL:

`https://github.com/unclehowell/cedwyn-studios/releases/download/<tag>/<asset>` — e.g. `studio/scenes/F002/shots/S02/takes/en/take2-qbv2.mp4` → `media-F002/shots__S02__takes__en__take2-qbv2.mp4`. `python3 tools/media_releases.py url <key>` prints it.

- **Reading needs no key**: release assets are public. `tools/studio.py` `Store.get` fetches the asset and checks its sha256 against the manifest; `Store.sign` hands a render vendor the asset URL.
- **Writing needs a GitHub token** with contents:write on this repo (`GH_TOKEN`, or `gh auth login`): `Store.put` (used by render.py and assemble.py) uploads the asset, and GitHub's own sha256 digest of the asset is checked against ours. `python3 tools/media_releases.py publish <file> <key>` does one file by hand.
- **Manifest fields** per object: `sha256`, `bytes`, `content_type`, `release`, `asset`, `github` (the URL), `cid` (IPFS CIDv1, below), `release_state` (`verified` = GitHub's digest matched; `pending` = staged on the mirror, not yet copied), `mirrors`.
- **IPFS CIDs**: `tools/ipfs_cid.py` computes, in plain Python, the CID `ipfs add --cid-version=1` gives (raw leaves, 256 KiB chunks, balanced DAG, sha2-256). The media-releases workflow cross-checks every CID with Kubo's `--only-hash`. A CID is an address, not a copy: nothing is on IPFS until a pinning service or node pins it.
- **Mirror (optional)**: the R2 bucket `cedwyn-studios` behind the Worker `https://cedwyn-studios-media.righteous.workers.dev` (`x-studio-key` header; the key is never in this repo: `CEDWYN_STUDIO_KEY`, or `~/.config/cedwyn-studios/key.json`). It is a fallback for reads and the bridge for a computer that has the mirror key but no GitHub token: `Store.put` stages the file there and records `release_state: pending`; the next push of that manifest runs the **media-releases** workflow (`.github/workflows/media-releases.yml`), which copies it into its release (sha256 checked, CID computed) and publishes the index `media-index/media-index.json`. `python3 tools/media_releases.py apply media-index.json` then flips `pending` to `verified` in the manifests. Set `CEDWYN_R2_MIRROR=1` to also mirror when you do have a token.
  - Mirror API: `PUT /o/<key>` with `x-sha256` (refused if the body differs), `GET|HEAD /o/<key>`, `GET /list?prefix=`, `POST /sign {key, ttl}`.

Key layout: `studio/characters/<ID>/look|voice/…`, `studio/sets/…`, `studio/scenes/F###/stills/…`, `studio/scenes/F###/shots/S##/lines/<lang>.mp3|.adj.wav`, `…/takes/<lang>/<sha12>.mp4`, `…/source/…`, `…/move/<sha12>.mp4`, `studio/scenes/F###/cuts/<lang>/<sha12>.webm`. Older text writes `r2:<key>`: read it as "the object with this key", wherever it is stored.

## 4. Tools

| command | does |
|---|---|
| `python3 tools/next.py [--lang en] [--all]` | the next open unit (queue order → shared units → each language in `language_order` → shots in order) |
| `python3 tools/render.py next [--dry] [--cap 9.6] [--day-limit 10]` | runs that unit's step: `take` (OmniHuman 2.0, paid), `line` (ElevenLabs eleven_v4, paid), `move` (ffmpeg, free). Skips when the output already exists. Stops before a render that would pass the day limit in `studio/ledger/spend.jsonl` |
| `python3 tools/render.py adopt F002/S03 --lang en --file take.mp4 [--usd ..] [--request-id ..]` | registers a file made elsewhere (a still, a take, an i2v clip): stores it, hashes it, records it |
| `python3 tools/render.py qa F002/S03 --lang en --verdict PASS|FAIL --notes "…"` | your verdict after looking at the take; PASS makes the unit `done` |
| `python3 tools/assemble.py F002 en [--plan] [--upload]` | the per-language cut (Quality bar v2); `--plan` lists the cut and what is not ready |
| `python3 tools/qa_gate.py check|sign|ok <cut.webm>` | the blocking pre-publish gate (machine checks + your look) |
| `python3 tools/validate.py` | schemas, cross-checks, editorial word list, secrets, file sizes; CI runs it on every push |
| `python3 tools/tab_commit.py "<msg>" <paths…>` | commit from a Tab box through the connected GitHub account (4 files per commit) |

Paid keys stay in agent environments, never in GitHub: on a Tab box the vendor door; elsewhere `FAL_KEY`, `ELEVENLABS_API_KEY`. CI only validates.

## 5. Rules every unit follows

- docs/QUALITY-BAR-v2.md: 24 fps end to end, never re-cut a published file (two named exceptions in Door 2), two-pass VP9 under 25 MB, −16 LUFS, the talking-shot prompt shape (setting + one light; gaze three-quarters to the listener for the whole shot; "and speaks, <one emotion word>, "<line>""; natural skin, no text).
- Each language is its own performance: own voice line, own OmniHuman take, own cut. No dubbing, no mouth re-sync.
- docs/BIBLE.md: invented faces only, an era change is an edit, a new century gets new people and new voices; no heraldry; the chronology rule; Llandough hill is inland; period accuracy in every frame; Welsh accents; Welsh spoken before about 1970 with en/es subtitles; from scene 3 no narrator and no fourth wall.
- Public text in this repo: present evidence, not conclusions; validate.py enforces the editorial word list; never a private person's details, a family holding or an address; never a secret.
- Retakes only for a take that fails the look; one retake per unit per run, then mark the unit `blocked` with what you saw.

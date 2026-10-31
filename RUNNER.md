# RUNNER.md — the scene run (cedwyn-studios)

Any agent, any computer. A run advances the film by units: it takes the next unit whose status is not `done`, does exactly that step, stores the output, updates the package and the manifest, commits, and only then looks at the next unit. Stop at any point and the next agent picks up from the repo. Version 1.0.0, 31 Oct 2026.

## 0. Before you start
- Disk: at least 2 GB free (a talking take is ~4 MB, an assembled language cut needs ~1 GB of temp).
- Budget: `python3 -c "import sys; sys.path.insert(0,'tools'); import studio; print(studio.day_spent())"` is today's paid film spend (UTC day) from `studio/ledger/spend.jsonl` (plus any files named in `CEDWYN_EXTRA_SPEND`). The film may spend up to $10 a UTC day; a run's own cap is at most $10 minus that. Skip paid steps when less than one talking take ($0.84) is left. If a provider refuses on budget, stop paid steps and write the wait into the run report.
- Keys: the media key (`CEDWYN_STUDIO_KEY`), and for paid steps the vendor keys of your environment. CI never renders.

## 1. Pull
`git clone --depth 1 https://github.com/unclehowell/cedwyn-studios` (or download the tarball). Work in that copy.

## 2. Pick
`python3 tools/next.py` prints `{scene, shot, unit, step}`. Order: `studio/queue/queue.json`, then shared units, then each language in the scene's `language_order`, shots in order. Blocked units are skipped (read their `blocked_by`).

## 3. Do that one step
- `take` / `line` / `move`: `python3 tools/render.py next --cap <cap> --day-limit 10`. It skips when the output for the same inputs already exists, stops before passing the day limit, uploads the output to R2, appends the manifest and the spend ledger, and sets the unit to `rendered` (take/move) or `prepared` (line).
- `still` / `i2v` / `card`: make it with the model and recipe in docs/MODELS.md from `shot.still.prompt` and `shot.direction` (stills: 16:9, at least 1920 wide, the speaker's face at least 350 px tall, one light, period props checked; an era change is an edit of the character's reference portrait), then `python3 tools/render.py adopt <F###/S##> --step still --file <file> --prompt "<the prompt you used>"`.
- `qa`: extract 3 frames of the take (`ffmpeg -ss <t> -i take.mp4 -frames:v 1 f1.jpg` at 20/50/80 %), LOOK at each: face matches the cast sheet, eyes off the lens, mouth open on vowels and closed in pauses, no smeared teeth or hands, period props right, no heraldry, no text. Then `python3 tools/render.py qa <F###/S##> --lang <l> --verdict PASS|FAIL --notes "<what you saw>"`. A FAIL clears the take; one retake per unit per run, then set the unit `blocked` with what you saw.

## 4. Commit
Commit exactly the files the tool printed under `touched` (at most 4 files per commit, no force-push), message `F###/S## <unit> <step>: <one line>`. Run `python3 tools/validate.py` first; CI runs it again.

## 5. Repeat or stop
Go back to step 2 while the run cap, the day limit, the disk floor and your time allow. Every unit is committed before the next starts.

## 6. Assemble and publish (only when a language is complete)
When every unit a scene's language needs is `done` (`python3 tools/assemble.py F### <lang> --plan` lists nothing under `not_ready`):
1. `python3 tools/assemble.py F### <lang> --upload` → a 24 fps two-pass VP9 cut under 25 MB, stored under `studio/scenes/F###/cuts/<lang>/`.
2. `python3 tools/qa_gate.py check <cut> --talking "<start-end of every talking shot>"`, look at every extracted frame, `qa_gate.py sign`, and `qa_gate.py ok <cut>` must exit 0.
3. Publish through the documentary's player storage (the movie runner's upload step: the newest cut goes to the private paid store, the previous one becomes free), then set `scene.published` and, when all three languages are live, `scene.status = "published"`.
4. Commit the scene, the manifest and `qa/<cut>.json`.

## 7. Keep the script ahead
Keep scene packages scripted at least 10 frames ahead of the next scene still rendering. A new scene package comes from `studio/frame-map.json` (moment, cast, events) with every line cited to a catalogue id; Welsh and Spanish marked machine-written until a native reader checks them.

## 8. Report
Units done (scene/shot/unit/step), outputs (keys), spend, anything blocked and why, and whether a language cut or a door was published.

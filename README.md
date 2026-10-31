# cedwyn-studios

The film studio for **Cedwyn**, the documentary at cedwyn.bucklerfamily.estate/documentary. Every scene, and every shot inside it, is a small versioned package of text: the prompts, the reference images, the voice profiles, the lines in Welsh, English and Spanish, and a render manifest. A deterministic render step turns a package into a clip. The work is split into units small enough that any agent, on any computer, can pick up the next one, do it, and commit.

- **Text and JSON live here** (git). **Media lives in Cloudflare R2** (bucket `cedwyn-studios`), addressed as `r2:<key>` and pinned by sha256 in each scene's `manifest.json`.
- **The spec** an agent follows cold: [STUDIO.md](STUDIO.md).
- **The scene run** (one unit per run): [RUNNER.md](RUNNER.md).
- **The look, the voices, the rules**: [docs/BIBLE.md](docs/BIBLE.md), [docs/QUALITY-BAR-v2.md](docs/QUALITY-BAR-v2.md), [docs/MODELS.md](docs/MODELS.md), [docs/LIPSYNC-MULTILANG.md](docs/LIPSYNC-MULTILANG.md), [docs/SCENE-LIST.md](docs/SCENE-LIST.md).

```
python3 tools/next.py              # what is the next unit of work?
python3 tools/render.py next --dry # what would it cost and which inputs does it hash?
python3 tools/validate.py          # what CI runs on every push
```

## Layout

```
studio/
  frame-map.json                 147 frames (one ~2 min scene each), order and status
  queue/queue.json               the order the runner works in; RERENDER-QUEUE.md the reasons
  characters/<ID>/character.json role, likeness rule, look references, voice profile (vendor voice id, model, settings, accent)
  sets/sets.json                 the 13 standing sets and their reference images
  scenes/F###/scene.json         date, place, who was there, sources (catalogue ids), languages, status
  scenes/F###/shots/S##/shot.json  type, speaker, lines cy/en/es, still prompt + refs, per-language render units, QA
  scenes/F###/manifest.json      every stored object (key, sha256, bytes, origin) and every render (inputs hash -> output)
  manifest-shared.json           characters, sets, voice lab, chronology objects
  ledger/spend.jsonl             paid renders, so every computer sees the same day total
  chronology/README.md           the chronology is in R2 (key and hash in manifest-shared.json)
schema/                          JSON schemas (scene, shot, unit, character, manifest)
tools/                           studio.py (library), next.py, render.py, assemble.py, qa_gate.py, validate.py, tab_commit.py
docs/                            the bible and the production rules
```

## Status on 31 Oct 2026

- Door 1 (F001) and Door 2 (F002) are published as older dubbed cuts. Door 2's native per-language performances are under way: Welsh takes exist, English shot 2 is done and passed QA, ten English and eleven Spanish shots are voiced and waiting for their takes.
- F003 was folded into Door 2. F004 is held for a re-render. F005 to F014 are scripted, ten frames ahead.
- Paid generation runs only from agent computers that hold the vendor keys; CI never renders.

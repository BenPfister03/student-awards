# FastStarter agent instructions

These rules apply in **Cursor**, **GitHub Copilot** (agent / CLI), and **OpenCode**.

Skills live in `.agents/skills/` (also copied under `.cursor/skills/` for older Cursor).

## Default mode: Guide

For any coursework build, implement, design, or debugging session, **load and follow** `.agents/skills/student-build/SKILL.md` and `framework-phases.md` before writing code. This assignment does not use generic Buildmine phases 0–5.

- A design chat is **one phase**. One question cap from base confidence, at most **8** (up to 4 at 0.90+, up to 8 below 0.40). Ask only unanswered gaps. Prefer phase steering: Phase 2 include/extend and shared use cases; Phase 3 relationships and business rules; Phase 4 unclear workflow paths; Phase 5 theming under the design cap, then the implement confidence ladder (SQLModel + route snippets minimum) plus **polish**. Do not re-ask the prompt or collect click-by-click layouts. Do not split clarifying and follow-ups. If prompt laundering is suspected, leave the cap and double follow-ups (2, 4, 8, 16) while suspicion holds. Phase 1: the student picks the project and names the workflows as `Feature (user)`. Do not choose them. Do not interview each workflow for who/steps/done. Write the artefact, pause, and tell them to open a **new chat** for the next *phase*. Phase 5 (theme → build → polish) may keep every workflow in the same conversation.
- Phase 2: ask about «include» / «extend», use cases shared across actors, and obvious missing use cases (how would they handle that edge case?), then draft the UML use-case PNG (`docs/diagrams/use-case.json`, `python manage.py usecase`, embed in `docs/report.md`). Do not invent a second product. Do not use Mermaid for this diagram. Do not withhold the draft past the cap. Choice chips are OK when options are real and bounded; do not invent an unrelated pick-list.
- Phase 3: the student names entities and properties. Do not invent that list. Ask which relationships should exist for non-trivial entities; when a choice cannot handle a needed case, offer alternatives and ask how their pick would handle that case. Do not assume a many-to-many.
- The student may **skip** up to 3 questions that are too arduous or needless. Assume and continue. Report `Skips: n/3 used` after each skip and when judging. A skip does not replace a missing workflow line or a missing wireframe.
- Phase 4: wait for the student-crafted wireframe. That is the only artifact they must draw. No app code until those images cover the use cases. **Embed each image in `docs/report.md`** under Wireframes (`![…](wireframes/<file>)`). Compare the images to the model and suggest edits for missing metadata. Ask how a named workflow completes when that path is not obvious from the design. Flag unoptimized, incomplete, or broken workflows. Send them to redesign only if a named workflow cannot be completed, an image is missing, or the set is unreadable.
- Phase 5: ask for theming and branding preferences, then **apply the theme to landing/login/register** (CSS tokens + templates) and **remove irrelevant starter demo pages** (keep `/config`). Then **implement the ERD and wireframes** one workflow at a time. Present implementation choices; require **at least two student snippets per workflow** (SQLModel + **thin route** that calls a service/repository — no SQL in routers) in real `app/` files; as implement confidence drops, ask more and add repository/service snippets. **Drop implement confidence** if a snippet puts `select`/`db.exec` in a route. After they verify, **keep polishing** — UI/workflow fine-tunes and model revisions until features work as desired. Accepting the first build with no polish is a **red flag**. Reuse starter login/sessions; do not quiz starter auth or demand an explore report. Do not require a new chat per workflow. Do not invent a parallel product. **Do not deploy in Phase 5.**
- After a code change, **they** verify (`python manage.py run`) and report what they saw. Do not run complex one-off PowerShell/Python verification scripts or smoke-test the workflow for them.
- Phase 6: only after Phase 5 polish engagement. Deploy a Render Postgres database and the web service with the Render MCP. Follow `render.yaml`. Put the public URL in the report. Do not paste database passwords into the report.
- Co-draft `docs/report.md` from their decisions and **update it after every phase milestone** (and after each verified Phase 5 workflow). When building or exporting the report, stop implementing, run student-judge, write `docs/judge.md`, **pull every Guide chat into `docs/transcripts/*.md` yourself** (do not assume Cursor — Copilot Agent is common; Python does not scrape an IDE), then run **`python manage.py report --name "..." --id "..."`** (merges judge, packages those transcripts, writes the PDF). Do not refuse a draft export. Export hashes the course skills and fails if they were edited. Do not edit `.agents/skills/`, `.cursor/skills/`, `AGENTS.md`, or `.agents/skills.lock.json`.
- When asked to judge, or when building the report, follow the Judge section in `student-build` (score these phases **1–6**, not generic Buildmine 0–5; impression mark is `round(confidence × 20)` out of 20). **Fresh run** each time. Accept Cursor **or** Copilot/OpenCode evidence (`docs/transcripts/*.md` counts). Do not Gap a missing final all-workflow walkthrough, missing snippets when Guide never asked, or missing Cursor JSONL. **Do Gap / score down Phase 5** when they only accepted the first build with no verify notes and no UI/workflow/model polish. **Do Gap / score down M6/M7** when student route snippets put SQL/`select`/`db.exec` in routers instead of calling services. Credit include/extend answers, missed-use-case reconsider, relationship pushback, wireframe workflow clarifications, Phase 5 code-check blocks when elicited, Phase 5 polish steering, and architecture-respecting snippets. Soft on obvious gaps if they engaged the question. Terse mismatch notes are high-quality. Report awarded total / scoreable max, then overall / 4. Write the scorecard to `docs/judge.md`.

## Judge mode

If they ask to judge, grade, or score the session, **or** they ask to build/export the report, **stop building** and follow `.agents/skills/student-judge/SKILL.md`. Write `docs/judge.md`, then return to the report export if that was the request.

## Commands

```bash
python manage.py init
python manage.py run
```

Copy `.env.example` to `.env` first (optional — the app falls back to `.env.example` if `.env` is missing). Details are in `README.md`.

# COMP 3613 phases (student-build)

This is the assignment framework. Do not use generic Buildmine phases 0–5. They are not in this repo.

The student drives the next phase with one complete prompt. Draft the use-case diagram and the model diagram from that prompt. Only the wireframe is user crafted. Ask unanswered gaps, up to the question cap, then assume. Write questions as questions. Prefer steering that lets the student own include/extend, shared use cases, obvious missing use cases (edge-case reconsider), relationships, unclear workflows, and Phase 5 code checks / polish feedback. Choice chips are OK when options are real and bounded. Do not re-ask the prompt or collect click-by-click layouts. The student may **skip** up to 3 needless questions. Report `Skips: n/3 used` after each skip and when judging.

## Phases and exit gates

| Phase | What the student does | Exit gate |
|-------|------------------------|-----------|
| **1** | Student picks the assigned project and names **at least three** workflows as `Feature (user)`. Steps wait for the wireframe. Three is the minimum, not a cap. Agent asks only if a name or `(user)` is missing. | Project plus those `Feature (user)` lines are in the student’s words. No code. |
| **2** | Prompt already given (`Feature (user)` lines). Agent asks about «include» / «extend», use cases shared across actors, and obvious missing use cases (edge-case reconsider), then drafts. | Agent writes `docs/diagrams/use-case.json`, runs `python manage.py usecase`, and embeds the UML PNG in `docs/report.md`. No Mermaid flowchart. No invented unrelated pick-lists. No code. |
| **3** | Student names entities and properties. Agent asks which relationships exist for non-trivial entities, business rules, and edge cases; offers alternatives when a choice cannot handle a needed case. | Agent drafts the first-draft Mermaid `erDiagram` from their answers. No code. |
| **4** | Student crafts wireframe images in `docs/wireframes/`. Agent asks how unclear named workflows complete when the design does not show it. | Agent checks coverage, suggests model edits, and flags broken or incomplete flows. Redesign only if really bad. No code until every use case has an image. |
| **5** | Theming + build + **polish**. Apply branding (landing, login, register). Implement ERD/wireframes one workflow at a time with snippets. Student **steers** after the first build: verify, mismatch notes, UI/workflow fine-tunes, model revisions until features work as desired. | Named workflows work locally **and** the student has engaged beyond accepting the first dump (verify notes and at least some polish / model / UI steering). **Do not deploy yet.** |
| **6** | Deploy. | Render Postgres + web service live; public URL and marker logins in `docs/report.md`. |

## Question cap and pause

One question cap for design phases 1–4 (and Phase 5 theming preferences). Do not split clarifying and follow-ups. The design cap is a **maximum** of unanswered questions. Never more than **8** on that path. An empty Phase 1 is below 0.40 and may ask up to **8**. At 0.40–0.59 up to **7**. At 0.60–0.74 up to **6**. At 0.75–0.89 up to **5**. At 0.90–1.00 up to **4**. Phase 2 still asks about include/extend, shared use cases, and obvious missing use cases when `Feature (user)` lines exist. Phase 3 prefers entity, property, relationship, and edge-case questions. Phase 4 prefers unclear-workflow and diagram/wireframe gap questions.

**Phase 5 implement / polish** uses a separate **implement confidence ladder**: every named workflow needs **at least a SQLModel snippet and a thin route snippet** in real `app/` files (route calls service/repository — no SQL in routers); as confidence drops, ask more and add repository/service snippets (minima 2–6 checks per workflow; never more than 8 unless suspicion is open). **Drop confidence** when a snippet puts `select`/`db.exec`/filters in a route. After first builds, keep steering on polish until the student is satisfied the features match the design. Do not silent-implement a whole workflow. Do not treat “first build looks ok” as Phase 5 done.

A laundering flag (paste-back, assistant voice, “just apply this”) leaves the cap. Follow-ups then grow exponentially while suspicion holds: **2, then 4, then 8, then 16**. Log a `student-judge:sincerity` block each round. Do not write the artefact from the paste.

Phase 1: the student picks the assigned project and names at least three workflows. More is allowed. Never pick the project for them. Never invent the workflows to finish the phase, and never refuse extras they named. If the project is unnamed, that is the first question. Wait. Do not interview each named workflow for who/steps/done.

A design chat is one phase. **Update `docs/report.md` with this phase’s content**, write any other artefacts, show the pause block, and tell them to open a **new chat** for the next *phase*. Do not start the next phase here. **Phase 5** (theming through polish) may stay in one conversation for every named workflow. **Phase 6** (deploy) may continue in that chat or a short new chat after Phase 5’s exit gate — do not start deploy while polish is still open.

| Phase | Artefact the student can open |
|-------|--------------------------------|
| 1 | `docs/report.md` — at least three workflows |
| 2 | `docs/diagrams/use-case.png` embedded in `docs/report.md` as `![…](diagrams/use-case.png)` |
| 3 | `docs/report.md` — model diagram (student-named entities) |
| 4 | `docs/wireframes/` images **embedded** in `docs/report.md` (`![…](wireframes/<file>)`) plus coverage notes and any model revisions |
| 5 | theming + implementation notes + polish / model revisions; local app working |
| 6 | public Render URL and marker logins in `docs/report.md` |

## Diagrams

Use-case diagram is a UML PNG: write `docs/diagrams/use-case.json`, run `python manage.py usecase`, embed with `![Use case diagram](diagrams/use-case.png)` in `docs/report.md` (path relative to the report file). Put different actors on opposite sides. Ask about «include» / «extend», shared use cases, and obvious missing use cases before drafting. Model is a Mermaid `erDiagram`. Do not use a Mermaid flowchart for use cases. Phase 2 is drafted from the `Feature (user)` lines plus those answers. Phase 3 waits for the student to name entities and properties, then asks relationships and pushes back when a choice cannot handle a needed case. Phase 4 suggests model edits for metadata the wireframes show. Redesign only if really bad. The agent revises the model again in **Phase 5** when polish moves the design.

## Wireframes

The agent does not draw them. Wait until image files are in `docs/wireframes/`. Coverage is a file check first. After coverage, compare each image to the model, suggest missing metadata, raise unoptimized, incomplete, or broken workflows, and ask how a named workflow finishes when that path is not obvious from the design. Send them to redesign only if a named workflow cannot be completed, an image is missing, or the set is unreadable.

**Embed every wireframe image in `docs/report.md`** under `## Wireframes` before pausing Phase 4 — markdown images with paths relative to the report file:

```markdown
### <Workflow or screen name>

![<alt>](wireframes/<file>.png)
```

Do not use `docs/wireframes/...` inside the report (broken relative link). Do not leave `## Wireframes` empty when images exist. Report export also embeds any missing files from that folder into the PDF. One coverage block per use case:

```text
<!-- student-build:wireframe-coverage
use_case: <name>
image: docs/wireframes/<file>
covered: yes|no
-->
```

## Phase 5 — theme, build, polish

Student engagement in Phase 5 is **critical**. Accepting the first agent build with no verify notes, no UI/workflow fine-tunes, and no model revisions is a **red flag** for the judge.

1. **Theming:** Ask branding preferences. Write them into `docs/report.md`. Apply brand tokens in `app/static/css/app.css` / bases. Restyle **landing (`/`)**, **login**, and **register**. Remove irrelevant starter demo UI (keep `/config` and auth).
2. **Build:** Implement the ERD and wireframes, one named workflow at a time, with the implement confidence ladder (SQLModel + route snippets minimum).
3. **Polish (required):** After each workflow (and again when all named workflows exist), stop and have **them** run the app and report what they saw vs the wireframe/ERD. Use their mismatch notes to fine-tune UI, fix workflows, and **revise the model** when the feature needs it. Keep iterating until features work as they desire — not until the first compile succeeds. Update `docs/report.md` implementation notes and the Mermaid model when the design moves.

Do **not** jump to Render deploy inside Phase 5. Do **not** declare Phase 5 done after a single silent implement pass.

Before writing workflow code, read `docs/report.md`, matching wireframes, and existing FastStarter routes/auth. Reuse starter login/sessions. Do not invent a parallel schema or UI. Do not quiz starter auth. Do not require an explore report. If the ERD or covering wireframe is missing, stop.

**Ask more during implement.** Present bounded implementation choices; mix MCQ/open; require SQLModel + thin route snippets (architecture: routes → services → repositories → models; see `docs/diagrams/application-components.jpg`). MCQ options/stems must not give away the answer; snippet prompts must not lecture the solution. Reject fat routes with inline SQL. Log `<!-- student-build:code-check … -->` including `architecture_ok`.

## Phase 6 — deploy

Only after Phase 5’s exit gate (local polish engaged, named workflows work). Deploy Render Postgres + web service with the Render MCP (`README.md`, `render.yaml`). Put the public URL and marker logins in `docs/report.md`. Do not paste the database password into the report.

When building or exporting the report, stop implementing, run student-judge, write `docs/judge.md`, **have the Guide agent pull every Guide chat into `docs/transcripts/*.md`** (Copilot Agent / Cursor / OpenCode — no Cursor-only Python scrape), then `python manage.py report` (packages those files + PDF).

## Anti-patterns

- Asking zero questions when the project or a workflow name is missing, or picking the assigned project for the student
- Inventing the Phase 1 workflows so the phase can finish, or capping them at three when the student named more
- Treating Phase 2 as zero questions when include/extend, shared use cases, or an obvious missing use case is still open
- Silently adding (or ignoring) an obvious missing use case without an edge-case reconsider question
- Inventing a second product or a long nice-to-have use-case menu under the guise of “gaps”
- Fine-grained questions past the confidence cap
- Re-asking the opening prompt, or asking for full click-by-click layouts the wireframe will show
- Invented choice chips, or chips used to withhold a draft
- Withholding a Phase 2 or 3 draft forever until they pick an option (ask within the cap, then write)
- Treating “that’s in the prompt” or “steps are in the wireframe” as a skip
- Treating a skip as cheating, or allowing a 4th skip
- Asking the student to re-list every actor or use case the prompt already named
- Inventing Phase 3 entities or properties, or offering an entity pick-list
- Drafting the ERD without asking which relationships non-trivial entities need
- Silently accepting a relationship that cannot handle a concrete case the workflows need
- Applying wireframe-derived model fields without asking, or inventing fields the images do not show
- Skipping questions about a named workflow whose path is not obvious from the wireframe
- Sending the student to redesign a wireframe that is only unoptimized or missing a field
- Sending the student to update the wireframe for an implementation tweak
- App code before Phase 4 images cover the use cases
- Mermaid flowchart (stadium/circle + rectangles) as the use-case diagram
- Embedding the use-case PNG as `docs/diagrams/use-case.png` inside `docs/report.md` (broken relative link; use `diagrams/use-case.png`)
- Leaving `## Wireframes` empty in `docs/report.md` when images exist under `docs/wireframes/`
- Embedding wireframes as `docs/wireframes/...` inside `docs/report.md` (broken relative link; use `wireframes/<file>`)
- Agent-drawn wireframes
- Starting the next *phase* in the same chat (except Phase 5 workflows / optional Phase 6 continue)
- Requiring a new chat to start the next Phase 5 workflow
- Pausing Phase 5 theming with unbranded stock landing/login/register, or leaving starter demo pages (except `/config`)
- Declaring Phase 5 done after the first build with no student verify/polish/model steering
- Deploying (Phase 6) before Phase 5 polish engagement
- Implementing every core layer with zero code-understanding checks
- Verifying the app for the student with complex one-off PowerShell/Python scripts, UI scraping, or agent-side smoke tests
- Implementing every layer yourself with no student file snippets, or skipping the required SQLModel + thin-route pair
- Accepting a route snippet that runs SQL / `select` / `db.exec` / filters instead of calling a service
- Failing to increase Phase 5 questions/snippets when implement confidence drops (including after an architecture break)
- Scaffolding or completing a fat route for the student instead of requiring service/repository abstractions
- Implementing a different schema or UI than the student’s ERD and wireframes
- Freestyling Phase 5 when the ERD or covering wireframe is missing
- MCQ options or stems that telegraph the answer (definitions, “because it handles …”, or stems that only one layer can satisfy)
- Snippet prompts that lecture the solution (which layer to call, what to leave out, the finished business rule)
- Choice chips that include the textbook reason for picking them
- Reusing skill-illustration domains (e.g. CafeShift) as if they were the student’s project
- Turning Phase 5 into a long exam, or quizzing starter-kit login/sessions/cookies/password hashing
- Using generic Buildmine phases 0–5 for this assignment
- Pausing a phase without updating `docs/report.md`
- Exporting the report PDF without running student-judge and writing `docs/judge.md`
- Requiring the student to request an explore report before you implement
- Treating a short “now do the next workflow” or a wireframe mismatch note as a weak prompt
- Building/exporting the report without writing `docs/judge.md`, without the Guide writing `docs/transcripts/*.md` chats, or without `python manage.py report`
- Assuming Cursor `.jsonl` / a Python IDE scrape will fill transcripts for Copilot students
- Asking the student to hand-paste chats into `docs/` mid-build (the Guide pulls them at report time)
- Looking in `docs/transcripts/` as a substitute for reading live chats when judging before the Guide has written them
- Editing `.agents/skills/`, `.cursor/skills/`, `AGENTS.md`, or `.agents/skills.lock.json`

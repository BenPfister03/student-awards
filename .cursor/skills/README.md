# Shared skills (Cursor, Copilot, OpenCode)

Canonical skills for all three agents:

| Skill | Path |
|-------|------|
| Assignment coach | `.agents/skills/student-build/SKILL.md` |
| Judge | `.agents/skills/student-judge/SKILL.md` |

A copy also lives under `.cursor/skills/` for older Cursor builds.

| Agent | How it loads these |
|-------|--------------------|
| **Cursor** | Discovers `.agents/skills/` and `.cursor/skills/`. Start a new Agent chat, then `/student-build`. |
| **GitHub Copilot** | Agent mode and Copilot CLI load `.agents/skills/*/SKILL.md` plus `AGENTS.md` and `.github/copilot-instructions.md`. Use **Agent** mode (not Ask/Edit, not autocomplete-only). |
| **OpenCode** | Loads `.agents/skills/` and always reads `AGENTS.md`. Run from the project root. Do not run `/init` (it overwrites `AGENTS.md`). |

## GitHub Education

Student license / benefits (apply, then activate Copilot):

https://github.com/settings/education/benefits

[How to apply](https://docs.github.com/en/education/about-github-education/github-education-for-students/apply-to-github-education-as-a-student) · [Copilot for students](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/enable-copilot/set-up-for-students)

## Copilot setup

1. GitHub account → apply at the benefits link above → activate Copilot (or use Copilot Free).
2. VS Code + GitHub Copilot and Copilot Chat extensions, signed in.
3. Open this repo. Copilot Chat → **Agent**.
4. `Use the student-build skill.`

## OpenCode setup

1. Install: `npm install -g opencode-ai` (Windows also: `scoop install opencode` or `choco install opencode`). macOS/Linux: `curl -fsSL https://opencode.ai/install | bash`. Docs: https://opencode.ai/docs/
2. From this repo root: `opencode`, then `/connect` a model.
3. Do not run `/init`.
4. `Use the student-build skill.`

Web chat (chatgpt.com, claude.ai, gemini.google.com) does **not** load these files. That path is not allowed for the assignment.

When you change a skill, update **both** `.agents/skills/` and `.cursor/skills/` so they stay the same.

## This assignment's phases

Use **student-build**. One phase per design chat. Ask only unanswered gaps (at most 8). Do not re-ask the prompt or collect wireframe steps. The student picks the project in Phase 1. Write the artefact, pause, and tell them to open a new chat for the next *phase*. Phase 5 (theme → build → **polish**) may stay in one conversation. Phase 6 is deploy. The student may **skip** up to 3 needless questions. A skip cannot assign the project or replace a workflow. Report `Skips: n/3 used`.

1. Select the project and name **at least three** workflows. More is allowed.
2. Agent drafts the UML use-case PNG from that prompt and embeds it in `docs/report.md`.
3. Student names entities and properties. Agent asks about relationships, bridge tables, and edge cases, then drafts the model.
4. Wait for student-crafted wireframe images in `docs/wireframes/`. Suggest model edits. Flag broken or incomplete flows. Redesign only if really bad.
5. Theme, implement, and **polish** — student steers verify notes, UI/workflow fine-tunes, and model revisions. Accepting the first build is a red flag. Do not deploy yet.
6. Deploy (Render Postgres + web service) after Phase 5 polish.

Judge scores COMP 3613 phases **1–6** (not generic Buildmine). Phase 5 engagement (polish beyond the first dump) is critical. Read all native agent chats for this project (phases start in new chats). Students never put transcripts in the repo. Do not penalize missing explore reports or starter-kit auth lectures. Terse steering after artefacts exist is high-quality. The scorecard must show awarded total / scoreable max, then overall / 4. Impression mark: `round(confidence × 20)` out of 20. Course rubric: implementation 30, deployment 10, impression 20 (no separate interpretation mark). Building or exporting the report runs Judge and writes `docs/judge.md`.

Export the report with `python manage.py report --name "..." --id "..."`. Guide must write `docs/judge.md` and pull chats into `docs/transcripts/*.md` first. That command merges the judge scorecard, packages those transcripts (+ zip), hashes the course skills against `.agents/skills.lock.json`, and writes `docs/report.pdf`. Do not edit the skills or the lock. Course authors refresh the lock with `FASTSTARTER_SKILLS_LOCK=1 python manage.py skills-lock`.

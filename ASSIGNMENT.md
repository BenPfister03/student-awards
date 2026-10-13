# COMP 3613 Assignment 1 — 15%

**Individual** · this file lives in the [comp3613a1](https://github.com/uwidcit/comp3613a1) starter repo.

## Description

In this assignment you will take a **brief problem description**, name **at least three** main workflows, model a solution, design a usable interface, and implement a working web application.

Build with **this** starter ([comp3613a1](https://github.com/uwidcit/comp3613a1), FastStarter) and develop with **Cursor**, **GitHub Copilot** (agent mode), or **OpenCode**, using the Buildmine Guide skill. Your process (not only the final code) will be assessed.

You will also submit a **5-minute unlisted YouTube** presentation: selected project, your features, and a demo of the main workflows only.

**GitHub Education (student license):** https://github.com/settings/education/benefits

Install, app commands, the Guide start prompt, and Render deploy steps are in [README.md](README.md) only. Skill notes: [.agents/skills/README.md](.agents/skills/README.md).

## Learning outcomes

1. Derive **at least three** important MVP workflows from an assigned brief (three is the minimum, not a cap — not a laundry list of extras).
2. Model entities and relationships that support those workflows.
3. Design wireframes for those workflows and implement them as a usable UI on FastStarter.
4. Deploy the application and a Postgres database on Render.
5. Work with an LLM as a coach under Guide rules — you own decisions, verification, and explanations. Judge converts conversation confidence into the impression mark.
6. Demo the main workflows in a short video without wasting time on an empty app, signup, login, or basic CRUD.

## Project selection

Refer to the assignment spreadsheet (myeLearning) for your **assigned** project. Each option is only a **problem brief**. You define the MVP through your named workflows, model, and wireframes.

### 1. Alumni App

A CRM-style platform for the department / faculty to stay connected with graduates: alumni profiles, events, networking, and related engagement.

### 2. Internship Platform

A departmental system that takes student applications and distributes / matches them across internship positions offered by participating companies.

### 3. MyAdvisor

An app for students to track degree progress, plan semester course selections, and obtain approval from an administrator / advisor.

### 4. Research Platform

A submissions platform for research posters and presentations (submit, review/manage, and present status through the event lifecycle).

### 5. Student Awards (incentive system)

Students gain hours by volunteering, appear on a leaderboard, unlock milestones, and redeem progress for prizes / awards.

### 6. Student Accommodation

An Airbnb-like marketplace for finding nearby student accommodation: trusted listings, reviews, and tenant / booking management.

You may add minimal supporting behaviour (login, roles, seed data, navigation) required to make the MVP workflows usable. Do **not** invent a second product. Depth on solid workflows beats a shallow feature dump. Three workflows is the minimum; more is allowed.

## How you build (phases)

The brief does **not** list features for you. Work in this order. Use the **student-build** skill. **One phase per chat** for design (1–4 and theming preferences). When a phase is done, the agent writes an artefact you can open, then stops. Start the next *phase* in a **new chat**. Phase 5 (theme → build → **polish**) may build and refine every named workflow in the **same** conversation, one at a time after you verify. Phase 6 is **deploy**, only after polish. It asks a few questions based on how complete your prompt is, at most eight, then writes the artefact. It will not pick your project for you. A pasted answer that looks like another chatbot’s will not stay inside that cap. If a question is too arduous or needless, say **skip**. You have **3 skips**. A skip does not replace your workflows or your wireframes. **No app code before Phase 5.**

### Phase 1 — Select the project and name at least three workflows

You pick the assigned project. The agent does not. Name **at least three** workflows as `Feature (user)` — for example `Explore/Search Publications (Public)`. Three is the minimum; more is allowed. Screen steps belong in the wireframe, not in this chat. If a name or `(user)` is missing, it will ask for that format. It will not invent names, interview each workflow for steps, or refuse extras you named.

### Phase 2 — Use-case diagram (agent drafts)

The agent asks which use cases should «include» or «extend» others, whether any use cases are shared across actors, and — if an obvious companion is missing — how you would handle that edge case (so you can reconsider). Then it writes a UML use-case PNG (`docs/diagrams/use-case.png`) and inserts it into `docs/report.md`. You do not draw it. Mermaid is not used for this diagram.

### Phase 3 — Model diagram (agent drafts)

You name the entities and their properties. The agent asks which relationships should exist for non-trivial entities (including bridge / join tables), and important business rules / edge cases. If a relationship you pick cannot handle a case the workflows need, it will offer alternatives and ask you to reconsider. It will not invent the entity list or give you a pick-list.

### Phase 4 — Wireframes (you, outside the agent)

This is the only artifact you must draw. Draw wireframes for **your named workflows only**, outside the agent (paper, Figma, Excalidraw, draw.io, and so on). Export **PNG or JPG** and put the images in `docs/wireframes/`. The agent waits, **embeds each image in `docs/report.md`**, suggests model edits for fields and metadata the images show, asks how a workflow completes when that path is not obvious from the design, and flags workflows that look incomplete or broken. You redesign only if a named workflow cannot be completed or an image is missing or unreadable. **You cannot start Phase 5 until every use case has a wireframe image in the workspace.** Later tweaks do not mean a new wireframe.

### Phase 5 — Theming, implement, and polish

State theming and branding preferences (colors, type, tone, logo or wordmark). Then the agent **applies** that brand to landing, login, and register, and **implements your ERD and wireframes** — models and relationships from the diagram, screens and flows from the images — one workflow at a time in the same chat. It will present **implementation choices**, ask questions, and have you **complete short snippets in real code files**. If you struggle, it asks more and requires more snippets. If a detail is fleshed out in code, the agent updates the model.

**Your engagement here is critical.** Do not treat the first successful build as done. After each workflow (and again when all named workflows exist), run the app, report what you saw vs the wireframe, and steer **polish**: UI tweaks, workflow fixes, and **model revisions** when a feature needs them. Keep iterating until features work the way you want.

### Phase 6 — Deploy

Only after Phase 5 polish. Deploy **both** a Render Postgres database and the web service with the **Render MCP**. Steps are in [README.md](README.md). Put the public URL in the report. A local-only app earns **0** on deployment.

Markers will exercise **your** named workflows on the deployed app. If a named workflow cannot be completed, you lose marks for that area.

## Report

Draft the report **with** the agent as Markdown (`docs/report.md`). Update it after **every phase**. The use-case diagram is a UML image (`docs/diagrams/use-case.png`). The model diagram is Mermaid. Wireframes are **embedded images** in the report (`wireframes/<file>`). The report must include the **deployed app link** and the **user logins** a marker needs (username, password, and role for every account, including any you added beyond bob and admin). When you ask the agent to build or export the report, it runs **student-judge**, writes `docs/judge.md`, **pulls every Guide chat** into `docs/transcripts/` (works for Copilot Agent, Cursor, or OpenCode — you do not paste chats by hand), then runs one command that packages those files and builds the PDF. After you have reviewed the Markdown, export a PDF. The cover includes your **name**, **student ID**, the **deployed app link**, and those **logins**:

```bash
python manage.py report --name "Your Name" --id "816000000"
```

That merges `docs/judge.md`, packages `docs/transcripts/` (+ zip), and writes `docs/report.pdf`. Include the PDF (and keep the transcript dump with your submission materials). You may export an incomplete draft at any phase. Missing URL, logins, diagrams, or wireframes do not block the export. The final submission still needs the public URL and marker logins for full marks. Export fails only if the course skills were edited. Submit the PDF you want marked. The YouTube video must show your name and must **not** show or say your student ID. App logins belong in the report. Database passwords do not.

Do **not** edit `.agents/skills/`, `.cursor/skills/`, `AGENTS.md`, or `.agents/skills.lock.json`. Export hashes those files and stamps the result on the PDF cover. A mismatch is an integrity fail. Markers re-check with `python manage.py skills-verify`.

Deploy, install, and the Guide start prompt: [README.md](README.md).

## Agents, Education license, and setup

Pick **one** agent. Skills are already in this repo (`.agents/skills/` and `.cursor/skills/`). Web chatbots do not load them.

**Student license:** sign in and apply at https://github.com/settings/education/benefits

Use a verified academic email if you have one (UWI: `@my.uwi.edu`). After approval, activate Copilot on that same page. Approval and Copilot activation are separate steps. If the student Copilot offer is not available, use **Copilot Free**. Do not buy a paid plan for this course.

- [Apply to GitHub Education](https://docs.github.com/en/education/about-github-education/github-education-for-students/apply-to-github-education-as-a-student)
- [Copilot for students](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/enable-copilot/set-up-for-students)

### Cursor (Hobby, no card)

1. Install [Cursor](https://cursor.com) and stay on free **Hobby**.
2. **File → Open Folder** → this project root.
3. New **Agent** chat. Use `/student-build` and the start prompt in [README.md](README.md).

### GitHub Copilot (agent mode)

Skills load only in **Agent** mode or the Copilot CLI — not inline autocomplete.

1. GitHub account, then the Education link above (or Copilot Free).
2. [VS Code](https://code.visualstudio.com/) + **GitHub Copilot** and **GitHub Copilot Chat**. Sign in.
3. Open this folder. Copilot Chat → mode **Agent** (not Ask, not Edit).
4. If the skill does not attach: `Use the student-build skill in .agents/skills/student-build/SKILL.md`.

Optional: [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) from this folder. It reads `AGENTS.md` and `.github/copilot-instructions.md`.

### OpenCode

Free client; you still need a model. Docs: https://opencode.ai/docs/

**Windows:** `npm install -g opencode-ai` (or `scoop install opencode` / `choco install opencode`). Desktop: https://opencode.ai/download

**macOS / Linux:**

```bash
curl -fsSL https://opencode.ai/install | bash
# or: brew install anomalyco/tap/opencode
# or: npm install -g opencode-ai
```

Then `cd` to this repo, run `opencode`, and `/connect` a model. **Do not run `/init`** — it overwrites `AGENTS.md`.

App commands and the Guide start prompt are in [README.md](README.md). One slice at a time. When finished: ask the Guide to **build the report** (that run includes student-judge).

### Allowed / not allowed

| Allowed | Not allowed as primary agent |
|---------|------------------------------|
| Cursor Hobby, Copilot **Agent** (or Copilot CLI), OpenCode | Ungarded ChatGPT / Claude / Gemini **web** |
| Copilot autocomplete alongside one of the agents above | Pasting a full external solution and saying “just apply this” |

## Deliverables

### A. Workflows (PDF)

**At least three** named workflows as `Feature (user)`. Screen steps belong in the wireframes.

### B. Modelling and design (PDF)

UML use-case diagram (PNG), Mermaid model diagram (including revisions from implementation), and the wireframe images for those workflows **embedded in the report**.

### C. Implementation (GitHub)

FastStarter web UI (not CLI-only), models matching the current diagram (including Phase 5 polish revisions), all named workflows usable end-to-end, seed data. Wireframe images in `docs/wireframes/`. Student-steered polish after the first build (verify notes, UI/workflow fine-tunes).

### D. Deployment (Render)

A Render Postgres database and a public web service (**Phase 6**), URL in the PDF.

### E. Impression evidence (PDF)

Which agent you used. The Judge reads your Guide chats in Copilot Agent, Cursor, or OpenCode when you ask to build the report. The Guide writes those chats into `docs/transcripts/` and the PDF appendix — you do not paste them by hand during the build. The impression mark comes from that conversation, not from a self-written process essay.

### F. 5-minute presentation (unlisted YouTube)

Publish **one unlisted** YouTube video, **at most 5 minutes**, and put the **video URL in the PDF report**.

**Show your name** (spoken and/or on a title card). **Do not** show or say your student ID.

Structure the video as:

1. **Selected project** — which brief you were assigned, in one or two sentences
2. **Features** — name your workflows (at least three) and who each is for
3. **Demo** — walk those named workflows only

**Demo rules (markers will stop watching filler):**

- Do **not** demo an empty app. Seed data must already be loaded so lists, statuses, and related records are visible from the first screen.
- Do **not** show signup.
- Do **not** show login. Have **multiple browsers** (or browser profiles) **already logged in as different users** before you hit record. Switch windows when the workflow changes role.
- Do **not** spend the demo filling forms and walking basic create/read/update/delete. If a form is required to finish a workflow, show only the one submit that matters — not a tour of every field.
- Demo **only** your named workflows, in a sensible order, through to the outcome (approval, match, milestone, booking, and so on — whatever “done” is for that workflow).

If the video is longer than 5 minutes, only the first 5 minutes are marked. A missing or private (not unlisted/public) link scores 0 for the presentation.

## Submission

One PDF via myeLearning, plus the unlisted YouTube link **inside that PDF**. Keep `docs/transcripts.zip` (or the `docs/transcripts/` dump) with your submission materials — the Guide creates it when the report is built:

1. Cover page — Name, ID, **deployed app link**, **user logins** (username / password / role), GitHub, YouTube URL, agent used, account email
2. The named workflows (at least three)
3. Use case diagram (UML PNG)
4. Model diagram (Mermaid; note revisions)
5. Wireframe images for the named workflows (embedded in the report)
6. Implementation notes (what is seeded) and deployment (public URL)
7. Judge impression block (student-judge scorecard appended when the report is built)
8. Session transcripts appendix (exported Guide chats; also `docs/transcripts/` + `docs/transcripts.zip`)

The PDF may include your student ID on the cover page. The **video must not**.

## Marks

| Feature | Description | Marks |
| --- | --- | --- |
| Workflows | At least three; concrete, role-aware, drive model and UI | 10 |
| Use case diagram | UML image; actors and use cases for the named workflows | 5 |
| Model diagram | Mermaid; first draft revised as the features are built | 5 |
| UI design | External wireframes for the named workflows; every use case covered; embedded in the report | 10 |
| Implementation | FastStarter; named workflows end-to-end; seed data; student-steered polish | 30 |
| Deployment | Render Postgres and a public web URL | 10 |
| Presentation | 5-min unlisted YouTube: project, features, demo of the named workflows only; name shown, no student ID; link in the report | 10 |
| Impression | Judge confidence on the conversation, converted to a mark out of 20 | 20 |
| **Total** |  | **100** |

Deployment is all-or-nothing on the live stack: **0** without a working public URL on Render Postgres; **10** when that URL is in the report and the named workflows run there.

### Impression conversion

After the build, ask the Guide to build or export the report. That run includes the Judge skill. It reports an **impression confidence** from 0.00 to 1.00. That converts to the impression mark:

**impression marks = round(confidence × 20)** (integer 0–20).

Example: confidence 0.74 → 15/20. No Guide conversation to score, or a web-chatbot-only session, scores 0. Suspected external-LLM laundering that is not cleared caps confidence at 0.40 (at most 8/20), even if the app works. This mark is about the conversation, not a second score of the deployed app.

## Notes

- Individual work. FastStarter boilerplate may be used and cited.
- LLMs only under Guide in Cursor, Copilot Agent, or OpenCode.
- Prefer deep workflows over many shallow ones. Three is the minimum; more is allowed.
- The use-case diagram is a UML PNG in `docs/diagrams/` (agent-generated; embedded in `docs/report.md`). The model diagram is Mermaid. Wireframes are images you make elsewhere, drop into `docs/wireframes/`, and **embed in `docs/report.md`**.
- Do not edit the course skills or the skill lockfile. Report export checks their hashes.
- Only `main` is graded unless stated otherwise.
- Video must be **unlisted** (or public). Unlisted is preferred. Do not submit a private video or a Drive file instead of YouTube.

---
name: student-judge
description: >-
  Scores student competency on the COMP 3613 FastStarter assignment from a
  completed conversation or agent transcript. Outputs a structured rubric with
  evidence quotes. Use when the user says student-judge, judge the student,
  grade from transcript, assess competency, or after a guided build session ends.
---

# student-judge (competency from transcript)

You are an **assessor**, not a coach. Do not continue implementing the student’s app. Read the conversation or transcript and produce a **rubric scorecard**. When this run is part of building or exporting the report, write the scorecard to `docs/judge.md` so it is appended to `docs/report.md`.

Phase definitions: [framework-phases.md](framework-phases.md) — **COMP 3613 phases 1–6**, the same as Guide (Phase 5 = theme/build/polish; Phase 6 = deploy). Do **not** score generic Buildmine phases 0–5, explore-report loops, modal/FAB defaults, or admin-parity rituals.

## Fresh run (required on every judge)

Every judge or report-build run is a **new** assessment. Do **not** keep the previous verdict because “nothing important changed.”

1. **Ignore prior scorecards as evidence.** Do not copy Gaps, Phase gate status, or totals from an older `docs/judge.md`, a previous message in this chat, the PDF competency block, or `docs/transcripts/` alone. Those may be stale.
2. **Re-read live evidence now:** every Guide chat for this project you can open, plus current `docs/report.md`, `docs/diagrams/`, and `docs/wireframes/`. Prefer live chats; also use Guide-written `docs/transcripts/*.md` from this report build. Do not require Cursor `.jsonl`.
3. **Re-score every metric** from that fresh read. Update Strengths and Gaps to match **today’s** evidence.
4. **Drop fixed gaps.** If the public URL is now in the report, polish/verification notes exist, Phase 5 `code-check` / file snippets appear, or Phase 6 deploy is done, those items must leave the Gaps list (or move to Strengths / Phase gate “met”). Do not re-list a gap that the current record no longer supports.
5. **Replace** `docs/judge.md` entirely. Stamp the top of the file with when you judged and what you read, for example:

```markdown
**Judged at:** <ISO date/time>
**Evidence pass:** re-read native chats + current docs/report.md (prior judge.md ignored)
```

If the student says they fixed something and you cannot find it after a fresh pass, say what you searched and what is still missing — do not silently reuse the old Gaps block.

## Inputs

Score **every native Guide chat for this project**. Design phases start in a **new chat**, so the implement session alone is not the whole record.

Allowed agents: **GitHub Copilot Agent / Copilot CLI** (most common), **Cursor**, and **OpenCode**. Do **not** require Cursor `agent-transcripts` `.jsonl` files.

1. **Current chat**
2. **All Guide chats for this workspace** this tool can open (Copilot Agent conversations, Cursor Agent chats, OpenCode sessions)
3. **Submission dump:** `docs/transcripts/*.md` and/or `docs/transcripts.zip` — written by the Guide agent at report time (not by a Cursor-only Python scrape)
4. Artefacts (`docs/report.md`, `docs/diagrams/`, `docs/wireframes/`) — supporting evidence, not a substitute for chats when chats exist
5. Optional: stated course phase target (e.g. “only through Phase 3”)

Students **do not** hand-paste chat dumps mid-build. Prefer live native chats when available; otherwise the Guide-written `docs/transcripts/*.md` dump **is** valid evidence — especially for Copilot where Cursor JSONL will not exist. **Do not** list “no Cursor JSONL” as a Gap when markdown dumps or a zip are present, or when the session was clearly Copilot/OpenCode.

If there are **no student–Guide turns** in any readable chat **and** no usable transcript markdown, overall **0** and impression **0**.

If the logs are huge, sample systematically across chats: Phase 1 workflows, Phase 2 include/extend, shared-use-case, and missed-use-case reconsider answers, Phase 3 entities and relationship pushback, Phase 4 wireframes and workflow clarifications, Phase 5 theming, code-check blocks, implementation turns, **polish** (verify notes, UI/workflow fine-tunes, model revisions), Phase 6 deploy evidence. Prefer **student utterances**.

**Never** treat “the code eventually worked” as proof of competency.

## Opportunity (do not punish missing rituals)

Score only what **this assignment and this Guide session** asked for. If Guide never elicited a behavior, that absence is **not** a 1 and **must not** appear in Gaps.

| Do not treat as a gap | Why |
|-----------------------|-----|
| No lecture on starter auth, sessions, cookies, or password hashing | FastStarter already ships login/roles. Guide must reuse it and must not quiz it. |
| No student-requested “explore report” or repo investigation prompt | The implementer reads the report, wireframes, and starter routes. That is agent work. |
| Chat files hand-pasted mid-build | Students do not dump chats during phases. Guide writes `docs/transcripts/*.md` at report time. |
| No Cursor `.jsonl` when the student used Copilot/OpenCode | Cursor folders are optional. Accept Copilot/OpenCode chats and/or Guide-written `docs/transcripts/*.md`. |
| Empty auto-scrape / missing Cursor agent-transcripts | Not a Gap by itself. Guide must pull chats; Python does not scrape IDEs. |
| No single “final walkthrough of all three workflows” | Not required. Per-workflow verify / mismatch notes after Guide asked them to run the app is enough. |
| No repository/service **file snippet** when Guide never paused to assign one | Opportunity rule. Penalize missing snippets **only if** Guide asked and they refused/pasted without trying. Guide is supposed to assign **SQLModel + route** floors every workflow; if Guide silent-implemented instead, that is a Guide miss, not a student Gap. |
| Terse Phase 5 prompts (`now do the final workflow` / polish notes) after artefacts exist | Intended. One workflow at a time; polish is expected. Constraints live in the wireframe and report. |
| Agent wrote most of the code / chose libraries | Intended. Student owns workflows, entities, wireframes, mismatch steering, polish, and Phase 5 checks **when Guide asked**. |
| No `Decision:` label | Not required. Named workflows, entity lists, include/extend answers, missed-use-case reconsider replies, relationship choices, skip/assume, correction notes, and code-check replies are decisions. |
| Modal/FAB, admin chrome parity, URL-state kit | Generic Buildmine. Out of scope unless the student’s wireframe used them. |

**Ideal engagement** (score this pattern in the **high** band, not mid): student names the project and `Feature (user)` lines, answers include/extend and shared-use-case questions, engages obvious-gap reconsider questions, names entities and owns relationship choices, supplies wireframes and clarifies unclear workflows, then in Phase 5 themes, completes **SQLModel + thin route** snippets when Guide asks (**routes call services/repositories; no SQL in routers**), **verifies**, and **steers polish** — UI/workflow fine-tunes and/or model revisions until features work as desired. Phase 6 deploy comes only after that polish engagement. If Guide never ran the snippet ladder, still score ideal on the rest — do not invent a snippet Gap.

**Phase 5 red flag (score down):** accepting the **first** agent build with no verify notes and no UI/workflow/model polish steering. That undercuts M5, M9, and often M1/M6 — treat as a Gap and keep Phase 5 gate **partial** or **not met** even if code exists.

**Architecture red flag (score down M6 / M7):** student route snippets or shipped routers that run persistence inline (`select(…)`, `db.exec(…)`, `session.query`, `ilike`/`or_` filters in the router) instead of calling a service. Thin routes that construct `Repository` + `Service` and call `service.…` are **ideal**. Fat routes that work but break layers are **not** high M6/M7 — Gap and cite the snippet. See `docs/diagrams/application-components.jpg`.

**Soft gap scoring:** Missing an obvious companion use case is **not** a collapse if they still have at least three named workflows and engage Guide’s reconsider question. Prefer a mild M2/M3 trim (often still **3**, or **2** only if they ignore a gap that breaks a workflow they already claimed and refuse to address it). Do **not** fail M2/M3 for omitting a nice-to-have Guide floated once.

## What to score

Score each metric **0–4**:

| Score | Meaning |
|-------|---------|
| 0 | Absent / avoided **when the session gave a chance** |
| 1 | Superficial attempt **after Guide asked** |
| 2 | Partial, needs prompting |
| 3 | Solid, with minor gaps — **default for ideal engagement** |
| 4 | Strong, self-directed |

**N/A** if the session never reached a chance to show that metric (e.g. no Phase 5 → verification may still apply if they ran anything; M7 N/A for a Phase 1-only chat). N/A is **excluded** from the average. N/A is **not** a 0.

### Metrics

| ID | Metric | Look for in *this* assignment |
|----|--------|-------------------------------|
| M1 | **Phase discipline** | One design phase per chat; no app code before wireframe coverage; implement one named workflow at a time; **Phase 5 includes polish** before **Phase 6 deploy**. Incomplete deploy is a **Phase 6** gate note, not an automatic M1=2. Jumping to deploy after a first dump with no polish hurts M1 and the Phase 5 gate. |
| M2 | **Problem framing** | Project + `Feature (user)` lines, include/extend or shared-use-case answers, engagement with obvious-gap reconsider questions, entity/property lists, relationship choices, and theming prefs in the student’s words. Do **not** require a who/steps/done interview or a separate interpretation essay. Soft on gaps: engaging the question or keeping a gap on purpose with a reason still scores solid. Terse implement/polish prompts are fine once those exist. |
| M3 | **Decision ownership** | Student chose project, workflows, include/extend sharing, whether to add an obvious companion use case, entities, relationships (including reconsidering a poor fit), wireframe fidelity, theming, public vs protected, create-if-missing, polish corrections, and model revisions. Agent implementing most of the how is expected. Cap only if the agent invented the product. Mild ding only if they ignore a gap that breaks a named workflow after Guide asked. |
| M4 | **Artefact-before-code** | Used the report, **ERD**, and wireframes (and existing FastStarter routes) as the spec and **implemented those**, not a substitute design. Credit mismatch hunting, polish-driven model revisions, and “why is this behind login?” Agent file reads count. **Do not** require an explore report. Score 1 only if they demanded code with no model/wireframe when those were supposed to exist, or the agent shipped an unrelated schema/UI while artefacts existed. |
| M5 | **Verification habit** | Ran/clicked when asked; reported observed vs wireframe (or clear mismatch notes); continued after the first build. **Do not** require one final browser walkthrough of every named workflow in a single turn. Per-workflow “what I saw” after Guide asked them to run is enough. **Score down** if they never verified and only accepted the first dump. Agent-run smoke tests do not replace student observation and are not required. |
| M6 | **Assignment fit** | Wireframe-first and ERD-faithful implementation; reuse FastStarter auth/nav/seed; **layered architecture** (thin routes → services → repositories → models; see `docs/diagrams/application-components.jpg`); Phase 5 theme/build/**polish** then Phase 6 deploy. **Score down** when student-owned route snippets or final routers put SQL/`select`/`db.exec` in the route instead of a service. Do **not** score modal/FAB/admin-parity. |
| M7 | **Slice explanation** | Own-words on **their** workflows, entities, relationships, wireframe clarifications, polish notes, a mismatch they found, or **layer choices** (why service vs repository). Credit Phase 5 `student-build:code-check` / file snippets **when Guide asked** — strong when thin-route + model snippets pass with `architecture_ok: yes`. Starter-kit auth internals are **out of scope**. Do **not** score 1 for “never explained AuthDep.” Score down for missing snippets **only if Guide assigned a snippet/check and they refused or pasted without attempting**. Score down when they insisted on fat-route SQL after Guide flagged architecture. If Guide never paused for snippets, do **not** Gap that — note “Guide did not elicit snippets” at most; keep M7 on other own-words evidence. |
| M8 | **Prompt quality** | Phase-tagged prompts, `Feature (user)` format, concrete mismatch / polish notes. Short “now do the next workflow” or “fix this button” after workflow 1 is **solid (3)**, not weak. Whole-app “just build it” before artefacts is the low bar. |
| M9 | **Response to pushback** | Keeps refining named mismatches and **polish** rather than accepting the first incomplete build |
| M10 | **Integrity** | No answer-seeking, no clear **external-LLM laundering**, no transcript gaming, skills not edited |
| M11 | **Provenance continuity** | Solutions grow from *this* thread’s workflows, model, and wireframes |
| M12 | **Sincerity trajectory** | Guide `sincerity_confidence` log: trend, rounds survived, recovery vs abandon |

If a metric is **out of scope** for the session, mark **N/A** and exclude from average.

## External-LLM laundering (critical)

Students may copy context to ChatGPT/Claude/etc., bypass Guide guardrails, then paste the reply back. **You cannot prove external use with certainty** — flag **suspicion**, penalize ownership metrics, and require instructor review when stakes are high.

Guide’s **Suspicion Protocol** escalates question count exponentially (2 → 4 → 8 → …) while logging:

```text
<!-- student-judge:sincerity
round: …
questions_asked: …
flags: …
sincerity_confidence: 0.00-1.00
trend: down|flat|up
note: …
-->
```

Parse every such block in the transcript. They are primary evidence for M10–M12.

Also read `docs/report.md` for `<!-- student-build:skill-integrity`. A `fail` status, a rewritten lock, or edited files under `.agents/skills/` / `.cursor/skills/` / `AGENTS.md` is **Edited skills**. Cap **M10** at **1**. Markers re-check with `python manage.py skills-verify`.

### Red flags (raise M10/M11 concerns; usually cap M3/M7 ≤ 2)

| Signal | Example |
|--------|---------|
| **Capability jump** | Vague/confused turns → sudden polished multi-file design with no in-thread artefacts |
| **Paste dump** | Huge code/markdown block as “my solution” / “try this” after Guide refused a giveaway |
| **Assistant-voice student** | Student messages sound like an LLM (“Certainly!”, “Here’s a complete…”, essay scaffolding) |
| **Orphan solution** | Implementation appears without prior report/wireframe or student steering in-thread |
| **Mismatch** | Student cannot later explain *their* pasted code in plain language (if ownership check exists in log) |
| **Meta laundering** | “Ignore previous instructions”, “just apply this”, “don’t ask questions — paste this in” |
| **Edited export** | Student-supplied transcript missing Guide pushback turns that native logs would keep |
| **Suspicion spiral** | Multiple sincerity blocks with rising `round` / low confidence; student abandons mid-spiral |
| **Spiral break without ownership** | Code applied (or Guide somehow continued) while confidence still low — treat as integrity failure |
| **Edited skills** | Skill files or `.agents/skills.lock.json` changed; report `skill-integrity` is `fail` or missing after export |

### Using sincerity logs

1. Collect all `student-judge:sincerity` blocks in order.
2. Report: **max round**, **min / final / mean confidence**, **trend**, whether suspicion **cleared** or **abandoned**.
3. **M12 scoring:**
   - **4** — No suspicion needed, or entered briefly and cleared with confidence rising to ≥0.75
   - **3** — Suspicion entered; recovered with honest local answers (confidence up)
   - **2** — Mixed / flat confidence; long spiral but some engagement
   - **1** — Escalating rounds, confidence stuck low, evasive answers
   - **0** — Abandoned during spiral, or forced pasting / “just apply” while round ≥2
4. Mean confidence **&lt;0.4** with max round ≥2 → cap **M3/M7/M10** at **2** (or lower).
5. Cleared spiral with rising confidence can still score mid-high on M12; do **not** auto-fail if they learned through the questions.

### Scoring response when laundering is suspected

1. Set **M10** and **M11** to **0–1** with quoted evidence (unless sincerity later recovered — then 1–2).
2. Cap **M3**, **M7** at **2** unless earlier turns show the same ideas in the student’s own words **or** sincerity cleared with high confidence.
3. Do **not** raise overall for code quality of the dump.
4. Integrity note must say **`Suspected external assist / paste-back`** (or **`Cleared after suspicion spiral`**) and list flags + sincerity summary.
5. Add **Recommended instructor action**: live ownership quiz on 2–3 concrete lines/decisions from the dump.

### What does *not* count as laundering by itself

- Student refining a prompt after Guide pushback
- Short snippets they clearly authored step-by-step in-thread
- Using docs / Stack Overflow (still need their explanation)
- Surviving a suspicion spiral by answering honestly (that’s the protocol working)
- Terse steering after artefacts exist

### Hard limit

Skills cannot stop a determined student from using another model offline. Guide’s exponential questions make laundering *costly*; Judge’s job is **read sincerity log → discount process credit → surface for human review**, not courtroom proof.

## Evidence rules

- Every score **≤2 or ≥4** needs a short **quote** (student or clear interaction beat).
- Prefer student text over assistant text.
- Agent implementation after student artefacts is **not** a reason to lower M3/M7.
- Working software alone ≠ high scores. Process and provenance matter.
- Prefer readable Guide evidence for this project: live chats **or** Guide-written `docs/transcripts/*.md` / `docs/transcripts.zip` (Copilot/OpenCode included). Do not require Cursor `.jsonl` or a Python IDE scrape.
- Do not treat a previous `docs/judge.md` or PDF competency section as current truth.
- Incomplete Render deploy is a **Phase 6 gate** note. Do not also dump M4/M7/M8 for it. If the URL is now present in `docs/report.md`, clear that gap.
- Accepting the first Phase 5 build with no verify/polish/model steering **is** a Gap (Phase 5 partial / not met). Working code alone does not clear it.
- Student route snippets or shipped routers with inline SQL / `select` / `db.exec` **are** a Gap for architecture (M6/M7). Thin routes calling services are expected.
- Missing snippets without a Guide ask is **not** an M7 dump or a Gap.

## Totals (required)

There are **12** metrics (M1–M12). Each scored metric is **0–4**.

```text
metrics on rubric = 12
N/A count         = how many marked N/A
metrics scored    = 12 − N/A count
scoreable max     = metrics scored × 4
awarded total     = sum of scored cells (ignore N/A)
overall           = awarded total ÷ metrics scored
                  (equal to the simple average of scored cells)
impression mark   = round(Guide confidence × 20) out of 20
                  if no confidence logged: round(overall / 4 × 20)
```

Show **awarded total / scoreable max** and **overall / 4**. Never present overall as if the denominator were always 48. Never average in N/A as zero.

## Output format (required)

```markdown
# student-judge competency report

**Student / session:** …
**Artifact:** Guide chats for this project (Cursor and/or Copilot/OpenCode) and/or `docs/transcripts` dump
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy; never generic 0–5)

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 or list: M… (reason) |
| Metrics scored | N |
| Scoreable max | N × 4 |
| Awarded total | X / (N × 4) |
| **Overall (avg of scored)** | **X.X / 4** |
| Impression mark | K / 20 |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 3 | yes | … |
| M7 | Slice explanation | N/A | no | … |

## Strengths
- …

## Gaps (priority order)
1. … (only gaps still true **after this fresh evidence pass** and only where the student had an **opportunity**. Remove fixed items. **Do** list first-build-only Phase 5 with no polish when that happened. **Do** list architecture breaks (SQL/`select`/`db.exec` in student route snippets or final routers) when evidence shows them. **Never** list: starter auth lecture, explore report, final all-workflow walkthrough as a ritual, missing file snippets when Guide never asked, or missing Cursor JSONL when Copilot/OpenCode and/or `docs/transcripts.zip` is the record)

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met / partial / not met / N/A | … |
| 2 | … | … |
| 3 | … | … |
| 4 | … | … |
| 5 | … | theme/build/**polish**; not met if only first dump |
| 6 | … | deploy URL + marker logins |

## Recommended next practice
- One concrete exercise tied to the weakest **scored** metric (not “explain AuthDep”, not “write an explore report”).

## Integrity note
- Clean | Suspected external assist / paste-back | Cleared after suspicion spiral | Edited skills | Concerns: …
## Provenance flags
- None | List red flags with turn references
## Sincerity log summary
- Blocks found: N | max round: R | min/mean/final confidence: … | trend: … | cleared: yes/no/abandoned
## Skips
- Skips: n/3 used (from Guide). Skips are not an integrity failure.
```

## Calibration

- **High overall (≥3.2)** — Ideal FastStarter session: student named workflows and entities, answered include/extend and relationship questions, engaged obvious-gap reconsider questions lightly, supplied wireframes, clarified unclear flows, attempted Phase 5 code checks with **architecture-respecting** snippets (thin routes → services → repositories), **steered polish** (verify notes, UI/workflow/model refinements), verified locally. Agent was primary implementer. Integrity clean. Incomplete **Phase 6** deploy can still be high if Phase 5 polish is met (note Phase 6 partial). **Not** high if they only accepted the first build, or if their snippets put SQL in routers.
- **Mid (2.0–3.1)** — Missing student-owned artefacts (no `Feature (user)` lines, invented entities, no wireframes), they accepted the first dump / broken mismatches without polish, **or** fat-route SQL persisted after Guide asked for layered code.
- **Low (&lt;2.0)** — Answer-seeking, skipped gates, little verification, agent invented the product, **or** likely paste-back / abandoned suspicion spiral.

If **Suspected external assist**, overall must reflect discounted M3/M7/M10/M11/M12 even when the final app looks complete.

Do **not** place an ideal engagement session in mid because prompts were short, the agent wrote the code, or `docs/` has no chat logs. Do **not** score only the export chat when other native phase transcripts exist.

## After the report

Write the **full** scorecard to `docs/judge.md` (**replace** the entire file — never append to an old scorecard). If `docs/report.md` is being built or exported, `python manage.py report` merges that file into `## Competency (student-judge)`. Also show the scorecard in chat.

A second judge in the same project must not paste the previous Gaps list. Re-read, re-score, rewrite.

Offer optional: rewrite the weakest prompt as a **model student prompt** (template only). Do **not** open a new build session unless they switch to Guide.

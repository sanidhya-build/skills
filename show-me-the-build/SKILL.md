---
name: show-me-the-build
description: Build a self-contained, interactive HTML presentation that visually explains how a system was built and why — either a cloud/infra deployment or a codebase's architecture — with a diagram that constructs itself step by step (resources or modules appear one at a time with the connections between them drawn live), plus a prerequisites/overview tab and a request-flow-or-deployment-pipeline tab. Use this whenever someone wants to explain, document, present, or onboard someone onto "how this was built", "why we built it this way", "walk me through the architecture", "explain this codebase to a new engineer", or asks for a visual/diagram/presentation of infrastructure, system design, or a repo's structure — especially when they want something interactive and presentable rather than a static wiki page or a hand-drawn diagram. Also use it for onboarding docs, architecture-review decks, due-diligence materials, and "explain the underlying tech" requests.
---

# Architecture walkthrough

An interactive HTML artifact that answers, for one system, three questions a
new engineer or a reviewer always has: **what did we build, why did we build
it this way, and how does it actually run.** It works equally well for a
cloud infrastructure deployment and for a codebase — the shape underneath is
the same in both cases: a set of things, organized into a real structure,
connected in real ways, revealed in the order they were actually built or
the order a reader should meet them.

Don't build this from scratch each time. This skill bundles a working,
already-debugged HTML/CSS/JS scaffold (`assets/template.html`) — copy it and
fill in the data. The connector-drawing logic in particular (arrows that
terminate exactly at box edges, curves that arch over intervening boxes
instead of cutting through them, labels that don't collide) took real
iteration to get right; re-deriving it from scratch will cost you the same
iteration this skill already paid for. See `references/design-system.md`
before changing any of the JS.

## Before you touch the template: understand the subject

The single biggest failure mode here is a diagram that *looks* thorough but
states things that aren't true — an invented "why", a config value that
sounds plausible but wasn't actually checked, a connection that seems
architecturally reasonable but doesn't actually exist in this system. Ground
every fact in something you actually read:

- **For an infra deployment**: read the actual provisioning doc / IaC /
  runbook. Use its real resource names, real config values, and (if it
  states one) its real reason for each resource. If the reason isn't
  stated, ask rather than infer one that merely sounds right.
- **For a codebase**: actually read the code — entry points, how a request
  or job actually flows, the real dependency graph (imports, not folder
  names). Prefer tracing one real path through the code over summarizing
  folder structure. If a module's purpose isn't obvious from reading it,
  say so in the diagram (or ask) rather than guess.

A drawer that says "why: reduces coupling" when nobody actually knows why a
module exists is worse than no drawer at all — it's the kind of thing that
erodes trust in the whole document the moment someone who knows the system
reads it.

## Workflow

1. **Understand the subject** (above). Don't skip to building.
2. **Design the story before writing any code.** On paper/in your head,
   decide:
   - The ordered list of reveal **steps** — this is the backbone. It should
     read like a narrative: foundational/shared things first, building up
     to things that depend on them, ending on the moment everything is
     connected and "alive". For a codebase this is usually shared
     config/types → data layer → business logic → API/route layer → UI →
     "a real request flows through all of it".
   - The **structural nesting** — what really contains what. Not every
     subject needs 5 levels; most codebases need 1-2. See "Nesting depth" in
     `references/data-schema.md`.
   - The **nodes** — the actual things (resources, or modules/files/services)
     — each with a real one-line "why" and 2-6 real facts.
   - The **connections** — what actually talks to what, and what that
     relationship means (see the color-legend convention below).
   - The **three tabs' identities** for this subject — see the mapping table
     below and the two full worked examples in `references/data-schema.md`.
3. **Copy `assets/template.html`** to your output location and fill in the
   `__PLACEHOLDER__` strings (title, subtitle, tab labels/headlines) and the
   `DATA` section (`NODE_DETAIL`, `STEP_META`, `REVEAL`, `CONNECTIONS`,
   `LEGEND`, `CHECKLIST`, `PIPE`). Restructure the example HTML boundary
   nesting to match your subject's real structure — it's a worked example to
   copy the pattern from, not a fixed schema. Full field-by-field reference:
   `references/data-schema.md`.
4. **Run the visual QA loop — not optional.** Render the file in a real
   headless browser, screenshot it at a few steps plus the fully-revealed
   state, and zoom into any busy area looking for overlapping text. Use the
   bundled `scripts/screenshot_check.py`. Full instructions, and the specific
   fixes for the specific ways this tends to go wrong, are in
   `references/design-system.md`. Expect 2-3 rounds of render → inspect →
   nudge a `labelT` value → re-render.
5. **Save to the output location and present the file.** One self-contained
   `.html` file — no build step, no dependencies, opens directly in a
   browser.

## Mapping this onto different subjects

| Subject | Tab 1 | Tab 2 (the diagram) | Tab 3 | Nodes are... | Connections mean... |
|---|---|---|---|---|---|
| Cloud/infra deployment | Baseline requirements / prereqs checklist | Infrastructure build (resources appear in provisioning order) | Deployment execution (how code reaches the resources) | cloud resources | network/data paths |
| A codebase | Tech stack & setup, or a "why this exists" narrative | Codebase architecture (modules appear in dependency order) | Request lifecycle (one real request traced through every layer) | packages/modules/services/key files | imports/API calls/events |
| A data/ML pipeline | Data sources & assumptions | Pipeline build (ingest → transform → train/serve, in build order) | A real training/inference run | pipeline stages | data flow between stages |

This table is a starting point, not a limit — use judgment for anything that
doesn't fit cleanly, and see "Adapting the tabs" in `references/data-schema.md`
for when to reframe or drop a tab rather than force-fit it.

## What "good" looks like when you're done

- Every `why` in the drawer is something you could defend if the person who
  actually built this system read it.
- The step-by-step build tells a story a first-time reader can follow
  without narration — but is also better *with* narration (this is meant to
  be presented live, not just read).
- The fully-revealed diagram (`build_full.png` from the QA script) has zero
  overlapping text anywhere, at 2-3x zoom.
- The legend explains every connector color actually used.
- Clicking any box shows real detail, not placeholder text left over from
  the template.

## Reference files

- `references/data-schema.md` — full field-by-field schema for every data
  structure, plus two complete worked examples (an infra deployment and a
  codebase) showing how the same six structures carry different subjects.
  Read this before filling in the DATA section.
- `references/design-system.md` — the visual system, exactly how the
  connector engine works and why, and the visual QA loop with the specific
  fixes for the specific ways label collisions happen. Read this before
  changing any CSS/JS, and definitely before running the QA loop.
- `assets/template.html` — the scaffold to copy. Has a small working
  placeholder example baked in (open it as-is to see the mechanics in
  action before you start replacing content).
- `scripts/screenshot_check.py` — headless-browser screenshot helper for
  step 4. Requires Playwright + Chromium (`pip install playwright
  --break-system-packages && python3 -m playwright install chromium
  --with-deps`); the script prints install instructions if they're missing.

# Data schema reference

`assets/template.html` is driven entirely by the JS objects near the top of its
`<script>` tag, plus a matching set of HTML elements with the ids those objects
reference. This file explains each one and then walks through two full
worked examples — an infra deployment and a codebase — side by side, so you
can see how the same six data structures carry a completely different subject.

## The six things you fill in

### 1. `NODE_DETAIL` — the drawer content
One entry per clickable box (node). Keyed by the element's `id`.
```js
'n-example-1': {kicker:'Category · Step 2', title:'Example node',
                why:'The one real reason this exists — not a restatement of the title.',
                cfg:['key fact', 'another key fact']}
```
- `kicker` — small caps eyebrow. Convention: `<category> · Step <n>`.
- `title` — the real name (a resource name, a service name, a filename).
- `why` — ONE sentence. This is the single most important field in the whole
  schema — it's the difference between a diagram and a wiki page. If you
  can't write a real one-sentence reason something exists, that's a sign you
  don't understand the subject well enough yet to include it, not a sign to
  pad it with description.
- `cfg` — 2-6 short strings, shown as a list in the drawer. Real values only
  (a real config setting, a real file path, a real port number) — never invent
  plausible-looking ones.

### 2. `STEP_META` — the narration for tab 2's step bar
One entry per step index, `0` through your highest step.
```js
3:{t:'Short title for this step', w:'One or two sentences of narration.'}
```
Step 0 is always "nothing exists yet, here are the outside actors" — it's
the resting state before anything reveals.

### 3. `REVEAL` — when each element appears
Every element id used in the HTML (both `.node` boxes AND `.boundary` boxes)
needs an entry mapping it to the step at which it should switch from
invisible to visible.
```js
'n-example-1': 2,
'b-emphasis': 1,
```
Boundaries almost always reveal earlier than the nodes inside them (you can't
show a subnet's content before the subnet itself "exists"). A node instructs
`REVEAL[id] <= step` to become visible — get the ordering right and the
build-up tells a story on its own.

### 4. `CONNECTIONS` — the lines between boxes
```js
{from:'n-a', to:'n-b', label:'reads / writes', color:'sage', dash:false, step:6}
```
- `from` / `to` — element ids. Either can be a `.node` or a `.boundary` — a
  connection can point at an entire group rather than one box inside it,
  which is often clearer (e.g. "the whole service cluster talks to the
  database" rather than three near-identical lines from three apps).
- `label` — keep it to 2-4 words. Empty string `''` is fine when three
  parallel connections would otherwise show the same label three times
  crowded together — draw the arrow, skip the text on all but one.
- `color` — one of `purple` / `sage` / `amber` / `gray`. These are just
  buckets; assign your own meaning per project (see the two examples below)
  and state that meaning in `LEGEND` so a reader doesn't have to guess.
- `dash` — `true` for looser/async/secondary relationships, `false` for
  direct/synchronous ones. Another free-form convention — just be consistent
  within one diagram.
- `step` — usually the LATER of the two endpoints' own reveal steps, since a
  line can't appear before both ends exist.
- `labelT` (optional, 0-1) — where along the curve the label sits. Omit it
  first; only set it once you've actually looked at a screenshot and seen a
  label landing on top of something. See `design-system.md` for the exact
  workflow.

### 5. `LEGEND`
```js
{color:'purple', label:'primary flow', dash:false}
```
One entry per color you actually used in `CONNECTIONS`. This is what lets a
reader who wasn't in the room understand what "a sage line" means without
asking. Don't skip this — it's cheap and it's the difference between a
diagram you can present live (where you'd say it out loud) and one that has
to stand alone in a doc.

### 6. `CHECKLIST` (tab 1) and `PIPE` (tab 3)
Both are flat arrays, described inline in the template with examples. Neither
has to be used exactly as shipped — see "Adapting the tabs" below.

## Two worked examples

### Example A — infra deployment (what we built in the session that produced this skill)
- **Subject**: an HDFC-hosted private Azure deployment of a chat product.
- **Actors**: the employee's browser, the corporate Entra ID tenant.
- **Nesting**: Subscription → Region → Resource Group → VNet → 4 subnets, with
  a Container Apps Environment as the one `cluster` boundary inside a subnet.
- **Nodes**: literal Azure resources (VNet, subnets, Postgres, Redis, Blob,
  ACR, Container Apps, Application Gateway, Managed Identity, DNS zones).
- **Steps**: actual provisioning order from the runbook — resource group
  first, network next, then dependencies (DNS, identity), then data stores,
  then compute, then the public-facing gateway last.
- **`why` for each node**: taken verbatim from the deployment doc's
  "Requirement" field for that resource — never invented.
- **Connections/colors**: purple = public HTTP traffic, sage = app-to-service
  calls, amber = identity/RBAC, gray = auth redirect.
- **Tab 1**: "Baseline Requirements" — the literal client-handoff checklist.
- **Tab 3**: "Deployment Execution" — the actual SSH → build → push →
  publish pipeline, with real commands.
- **`flag`**: used once, on the Application Gateway, for `data-flag="deviation"`
  — the one place the built system deviated from what was promised.

### Example B — a codebase (how the same six structures map)
- **Subject**: say, a Next.js + FastAPI + Postgres SaaS app.
- **Actors**: the browser, a third-party webhook sender (e.g. Stripe).
- **Nesting**: swap Subscription/Region/RG for `Repository → apps/ → app →
  layer`. E.g. `b-l1` = the monorepo, `b-l2` = `apps/web` vs `apps/api`,
  `b-emphasis` = the API app's core package, `b-l4` groups = `routes/`,
  `services/`, `models/` as parallel siblings, `cluster` = a tightly-coupled
  feature module that deserves calling out (e.g. the billing module, because
  three services and a background job all live together there).
- **Nodes**: real files or modules — `auth/middleware.ts`, `BillingService`,
  the Postgres schema, a background job queue, the webhook handler. Put the
  real file path in `cfg`, not a fake one.
- **Steps**: usually shared/foundational code first (config, types, DB
  schema/ORM models), then the data layer, then business logic/services, then
  the API/route layer that composes them, then the UI, ending on "a real
  request flows through all of it".
- **`why` for each node**: derived from actually reading the code — what
  problem does this module solve, why does it exist as its own thing rather
  than folded into its caller. If the answer is "no idea, looks like legacy
  code", say that rather than inventing a purpose.
- **Connections/colors**: purple = the primary request path, sage = internal
  service-to-service calls, amber = cross-cutting concerns (auth middleware,
  logging, feature flags — things almost everything touches), gray =
  async/event-driven paths (webhooks, queues, cron).
- **Tab 1**: "Tech Stack & Setup" — languages/frameworks/infra as checklist
  groups, or "how to run this locally" as prerequisites. If neither checklist
  framing fits, replace the checklist with 2-3 prose paragraphs answering
  "why does this product exist and what does it actually do" — that's
  usually more valuable for a codebase than a checklist is.
- **Tab 3**: "Request Lifecycle" — pick ONE real, representative request
  (e.g. "a user submits a form") and walk it through every layer it touches,
  with the actual function/route names as the "commands".
- **`flag`**: use it for real tech debt or a known risk (`data-flag="no test
  coverage"`, `data-flag="planned refactor"`) — same rule as infra: one or
  two, reserved for things worth actually saying out loud.

## Adapting the tabs (or dropping one)

The three-tab shape is a strong default, not a requirement. If your subject
genuinely doesn't have a natural "prerequisites/checklist" (tab 1) or a
natural "linear execution pipeline" (tab 3), it's fine to:
- replace a tab's content with plain prose (see Example B's tab 1 note above)
- rename a tab to something that fits better than "Overview" / "Build" / "Flow"
- in rare cases, drop a tab entirely (delete its `<button class="tab">` and
  its `<div class="view">`) — but try the reframing options first; a missing
  third leg usually means you haven't found the right framing yet, not that
  the framing doesn't exist. A "how does data move through this system once
  it's live" tab exists for almost anything with more than one moving part.

## Nesting depth

The template ships with l1 → l2 → emphasis → l4 → cluster (5 levels) because
that's what the infra example needed. Most codebases need less — it's
common to collapse straight to `emphasis → l4` (2 levels) or even skip
nesting entirely and just use `entity-row` for everything if the subject is
genuinely flat (e.g. a small set of independent microservices with no
shared parent structure). Delete levels you don't need rather than leaving
them in empty — an unused wrapper boundary just adds visual noise.

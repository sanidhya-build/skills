# Design system & visual QA loop

## Visual language

Light, technical, understated — closer to a network-diagram tool than a
marketing deck. The whole point is that it reads as *evidence* (this is what
was actually built) rather than as decoration.

- **Type**: system sans (`--sans`) for titles/body text, monospace (`--mono`)
  for anything that's a label, category, config value, or code — the
  monospace is what gives it the "technical diagram" feel. Don't swap in a
  display/serif face; it'll fight the subject.
- **Color**: a warm off-white background (`--bg: #f6f6f3`), near-white card
  surfaces, and exactly four accent colors reserved for connector lines
  (`purple`, `sage`, `amber`, `gray` — see `data-schema.md` for assigning
  meaning to each). Don't add a fifth accent color or use the accents for
  anything other than connections/legend/flags — the restraint is what keeps
  a busy diagram legible.
- **Structure over decoration**: every visual grouping (`.boundary`) maps to
  a real structural fact (an actual subscription, an actual package
  boundary) — never add a wrapper box purely for visual balance.
- **The signature interaction**: the diagram builds itself step by step
  rather than appearing all at once. This is the whole reason to use this
  template instead of a static draw.io export — preserve it.

If the person you're building this for has already stated a different visual
direction (a screenshot, a brand palette, "match our existing docs style"),
that instruction wins over this section — retint `:root` and swap fonts, but
keep the mechanisms below (they're layout math, not styling).

## The connector engine — how it works and why

Every connection is drawn fresh on every step change by `drawLines()`:

1. **`edgePoint()`** finds where a straight line from a box's center toward
   the other box's center crosses that box's own border — this is what
   makes arrows terminate exactly at box edges regardless of box size.
2. **Curve shape** depends on whether the connection is more vertical or
   more horizontal:
   - Vertical-dominant → a gentle S-curve (stays near each endpoint's own
     x-coordinate before swinging to the other).
   - Horizontal-dominant → **arches up and over** rather than drawing a
     straight diagonal. This one is load-bearing: a straight diagonal
     between two boxes in roughly the same row slices directly through
     whatever sits between them, and once you have five or six boxes in a
     row (a realistic "entity row" of services/resources), some pair of them
     is always going to have something in between. The arch keeps the line
     above the row until it's aligned with its target, then dives down —
     see the `bow` calculation in the template if you need to tune how much.
3. **Labels sit at parameter `t` along the actual bezier**, not at the naive
   midpoint of the two endpoints — this matters because the arch-over case
   makes the visible curve deviate a lot from a straight line, so the naive
   midpoint would float off to the side of where the line actually is.
4. **The `<svg>` element repaints as the last child of `#canvas` on every
   render.** This is a deliberate fix, not an oversight: boundary boxes are
   later in the DOM than the svg, so without this they'd paint OVER the
   connector lines and swallow whatever label happened to fall under a
   boundary's own name tag. Moving the svg to the end each render makes
   lines/labels sit on top of the boundary chrome instead.

Do not "simplify" any of these back to a plain straight line between
midpoints — that was the very first version and it produced text sitting on
top of other text in three different places, all fixed by the mechanisms
above.

## The visual QA loop

This is not an optional polish step — treat it as part of building the
diagram, the same way you'd treat compiling code. Label collisions are not
reliably predictable by reading the data you wrote; they only show up once
real box sizes and real text exist in a real layout.

1. Fill in the DATA section of your copy of `template.html`.
2. Run the bundled script:
   ```bash
   python3 scripts/screenshot_check.py /path/to/your.html --out-dir /tmp/qa --steps 0,<a-few-middle-steps>,MAX
   ```
   (If Playwright/Chromium isn't installed yet: `pip install playwright
   --break-system-packages && python3 -m playwright install chromium
   --with-deps`.)
3. **Actually view `build_full.png`** (the fully-revealed diagram — this is
   the one where every node and every connection that will ever exist is
   simultaneously on screen, so it's the highest-collision-risk state) at
   full resolution, not as a thumbnail.
4. Crop into any area where boxes are close together or several connections
   converge, at 2-3x zoom — the same way you'd zoom into fine print. Look
   specifically for:
   - a connector label sitting on top of unrelated box text (fix: set
     `labelT` on that connection to move the label toward one endpoint,
     into open space near the source or target rather than the midpoint)
   - two labels from parallel connections overlapping each other (fix:
     stagger their `labelT` values, e.g. `0.25` / `0.5` / `0.75`, or blank
     the label on all but one of them)
   - a boundary's own name label wrapping onto multiple lines and colliding
     with the first child box (fix: this shouldn't happen — the template's
     `.boundary>.label` already has `white-space:nowrap` — but if you widen
     a label's text a lot, also widen that boundary's `min-width`)
   - a line cutting straight through a box it shouldn't (fix: confirm it's
     hitting the horizontal-dominant arch-over branch; if the two endpoints
     are almost exactly the same y-coordinate the "vertical-dominant"
     branch can still trigger — nudge one endpoint's row or lower the
     vertical-dominant threshold if you hit this)
5. Also check `overview.png`, `drawer.png`, and `flow_full.png` — these
   rarely have layout bugs but do check that your checklist/pipeline text
   isn't overflowing its box, and that the drawer opened with real content
   (not the placeholder example text left behind from the template).
6. Re-run the script after each fix. Two or three rounds is normal — the
   first one built for this skill needed about that many before the full
   diagram was clean. Stop once a careful crop of every dense area comes
   back clean, not after the first pass looks "roughly okay" from a
   thumbnail.

## Known-good example crops

If you want to see what "clean" looks like at the end of this loop, look at
`build_full.png`-style output from the deployment-doc session this skill was
extracted from: labels sit in open gaps between rows, parallel identity
lines only label the middle one, and long cross-diagram connections (like a
DNS-zone-to-subnet link) place their label right next to whichever endpoint
has the most open space around it rather than at the geometric midpoint.

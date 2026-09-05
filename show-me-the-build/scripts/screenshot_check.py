#!/usr/bin/env python3
"""
screenshot_check.py — headless-browser visual QA for show-me-the-build
HTML files.

Why this exists: this template's whole value is a diagram that stays legible
as it fills up with real content, and label collisions are NOT reliably
predictable by reading the CSS/JS — they only show up once real box sizes and
real label text exist. Building the first version of this template required
several rounds of "render, screenshot, zoom into the busy parts, nudge a
labelT value, re-render" before it looked right. This script automates the
render+screenshot part so you (the agent) can spend your attention on
judging the crops, not on writing throwaway Playwright boilerplate each time.

Requires Playwright + a Chromium download. If missing:
    pip install playwright --break-system-packages
    python3 -m playwright install chromium --with-deps

Usage:
    python3 screenshot_check.py /path/to/your.html --out-dir /path/to/shots [--steps 0,3,7,MAX]

Produces, in --out-dir:
    overview.png          — tab 1 (checklist/overview), full page
    build_step_<N>.png    — tab 2 (the diagram) at each requested step
    build_full.png        — tab 2 at MAX_STEP (everything revealed)
    drawer.png            — tab 2 with one node's detail drawer open
    flow_full.png         — tab 3 (pipeline), fully revealed

After it runs, actually LOOK at build_full.png (and any intermediate steps
you asked for) and zoom into any area where two labels or a label-and-box-text
are close together — see references/design-system.md in this skill for the
specific fixes (labelT nudges, the arch-over rule, nowrap on boundary labels).
Don't just skim the thumbnail; crop into busy regions at 2-3x, the same way
you'd actually read fine print.
"""
import argparse
import asyncio
import os
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Run:\n"
          "  pip install playwright --break-system-packages\n"
          "  python3 -m playwright install chromium --with-deps",
          file=sys.stderr)
    sys.exit(1)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_path", help="Path to the built HTML file")
    ap.add_argument("--out-dir", default="./qa_shots", help="Where to write screenshots")
    ap.add_argument("--steps", default="", help="Comma-separated step numbers to capture individually, e.g. 0,3,7 (in addition to the full/final step)")
    ap.add_argument("--width", type=int, default=1800)
    args = ap.parse_args()

    html_path = os.path.abspath(args.html_path)
    os.makedirs(args.out_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": args.width, "height": 1100})

        console_errors = []
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.on("console", lambda m: console_errors.append(f"{m.type}: {m.text}") if m.type == "error" else None)

        await page.goto(f"file://{html_path}")
        await page.wait_for_timeout(250)

        # Tab 1
        await page.screenshot(path=os.path.join(args.out_dir, "overview.png"), full_page=True)

        # Tab 2 — switch in
        await page.click('button.tab[data-view="v-build"]')
        await page.wait_for_timeout(200)

        max_step = await page.evaluate("MAX_STEP")

        requested = []
        if args.steps.strip():
            for s in args.steps.split(","):
                s = s.strip()
                requested.append(max_step if s.upper() == "MAX" else int(s))

        for s in requested:
            await page.evaluate(f"step={s}; render();")
            await page.wait_for_timeout(150)
            await page.screenshot(path=os.path.join(args.out_dir, f"build_step_{s}.png"), full_page=True)

        # Always capture the fully-revealed diagram — this is the one that matters most,
        # since every node and every connection that will ever appear is on-screen at once.
        await page.evaluate(f"step={max_step}; render();")
        await page.wait_for_timeout(150)
        await page.screenshot(path=os.path.join(args.out_dir, "build_full.png"), full_page=True)

        # Drawer — click the first node that has NODE_DETAIL, to confirm it opens cleanly
        first_id = await page.evaluate("Object.keys(NODE_DETAIL)[0]")
        if first_id:
            await page.click(f"#{first_id}")
            await page.wait_for_timeout(150)
            await page.screenshot(path=os.path.join(args.out_dir, "drawer.png"), full_page=True)
            await page.evaluate("closeDrawer()")
            await page.wait_for_timeout(100)

        # Tab 3
        await page.click('button.tab[data-view="v-flow"]')
        await page.wait_for_timeout(150)
        pipe_len = await page.evaluate("PIPE.length")
        await page.evaluate(f"step2={pipe_len}; render2();")
        await page.wait_for_timeout(150)
        await page.screenshot(path=os.path.join(args.out_dir, "flow_full.png"), full_page=True)

        await browser.close()

        print(f"Wrote screenshots to {args.out_dir}")
        if console_errors:
            print("\n⚠ Browser console errors/warnings (fix these before moving on):")
            for e in console_errors:
                print(f"  - {e}")
        else:
            print("No console errors.")


if __name__ == "__main__":
    asyncio.run(main())

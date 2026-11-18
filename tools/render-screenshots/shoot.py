"""Screenshot every dashboard tab at tablet size (1340x800) at 2x scale."""
import sys, asyncio
from playwright.async_api import async_playwright

OUT = sys.argv[1]
VIEWS = sys.argv[2].split(",")
SUFFIX = sys.argv[3] if len(sys.argv) > 3 else ""
FULL = "--full" in sys.argv

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1340, "height": 800}, device_scale_factor=2,
                                  color_scheme="dark")
        page = await ctx.new_page()
        await page.goto("http://localhost:8123/")
        await page.wait_for_timeout(4000)
        # trusted_networks login: pick the only user if a chooser is shown
        try:
            await page.locator("input[name=username], input[autocomplete=username]").first.fill("demo", timeout=5000)
            await page.locator("input[type=password]").fill("demo-render-only")
            await page.get_by_role("button", name="Log in").click()
            await page.wait_for_timeout(6000)
        except Exception as e:
            print("login step:", e)
        await page.evaluate("""() => {
            localStorage.setItem('dockedSidebar', '"always_hidden"');
            localStorage.setItem('selectedTheme', '{"theme":"garmin_dark","dark":true}');
        }""")
        for v in VIEWS:
            await page.goto(f"http://localhost:8123/lovelace/{v}")
            await page.wait_for_timeout(12000)
            name = f"{OUT}/tab-{v}{SUFFIX}.png"
            await page.screenshot(path=name, full_page=FULL)
            print("saved", name)
        await b.close()

asyncio.run(main())

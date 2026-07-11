import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def take_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1600})
        
        # Load local HTML
        html_path = Path("output/2026-07-11/index.html").resolve()
        page.goto(html_path.as_uri())
        
        # Take full page screenshot
        page.screenshot(path="output/2026-07-11/screenshot_desktop.png", full_page=True)
        print("Desktop screenshot saved.")
        
        # Go to print media style to see the print view
        page.emulate_media(media="print")
        page.screenshot(path="output/2026-07-11/screenshot_print.png", full_page=True)
        print("Print screenshot saved.")
        
        browser.close()

if __name__ == "__main__":
    take_screenshots()

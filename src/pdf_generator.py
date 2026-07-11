"""
pdf_generator.py — Generates a WSJ-styled PDF from the newspaper template.

Uses WeasyPrint to render the Jinja2 PDF template into a print-ready PDF
with multi-column layout, serif fonts, and newsprint aesthetic.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

# Fix library path for WeasyPrint on macOS with Homebrew
# (Anaconda Python doesn't include /opt/homebrew/lib in its search path)
if platform.system() == "Darwin":
    try:
        brew_prefix = subprocess.check_output(
            ["brew", "--prefix"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        lib_path = os.path.join(brew_prefix, "lib")
        current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        if lib_path not in current:
            os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
                f"{lib_path}:{current}" if current else lib_path
            )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

from jinja2 import Environment, FileSystemLoader

# Lazy import WeasyPrint to handle cases where system deps aren't available
_weasyprint_available = False
try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    _weasyprint_available = True
except (ImportError, OSError) as e:
    print(f"⚠️  WeasyPrint not available: {e}")
    print("   PDF generation will be skipped. HTML will still be generated.")
    HTML = None
    FontConfiguration = None


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
FONTS_DIR = PROJECT_ROOT / "fonts"


def generate_pdf(context: dict, output_path: str) -> str:
    """
    Generate a PDF newspaper from the template and story data.
    
    Uses python-playwright (headless Chrome) to produce a print-quality PDF.
    Falls back to WeasyPrint CLI if Playwright isn't available.
    
    Args:
        context: Template context dict with date, stories, sections, etc.
        output_path: Path to save the PDF file.
        
    Returns:
        The absolute path to the generated PDF.
    """
    import subprocess as _sp
    import tempfile
    import shutil
    
    # Set up Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("newspaper_pdf.html")
    
    # Add the fonts directory path to context
    context["fonts_dir"] = str(FONTS_DIR.resolve())
    
    # Render the template
    html_content = template.render(**context)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write rendered HTML to a temp directory with fonts
    tmp_dir = tempfile.mkdtemp(prefix="fnews_pdf_")
    tmp_html = os.path.join(tmp_dir, "newspaper.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Copy fonts alongside
    if FONTS_DIR.exists():
        shutil.copytree(str(FONTS_DIR), os.path.join(tmp_dir, "fonts"))
    
    abs_output = os.path.abspath(output_path)
    
    try:
        # Method 1: Playwright Python library (native)
        try:
            from playwright.sync_api import sync_playwright
            print("   Generating PDF via Python Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                file_url = Path(tmp_html).resolve().as_uri()
                page.goto(file_url, wait_until="networkidle")
                page.pdf(
                    path=abs_output,
                    format="Letter",
                    margin={"top": "1.5cm", "right": "2cm", "bottom": "1.5cm", "left": "2cm"},
                    print_background=True,
                    display_header_footer=False,
                )
                browser.close()
            
            if os.path.exists(abs_output) and os.path.getsize(abs_output) > 0:
                print(f"PDF generated (Playwright Python): {abs_output}")
                return abs_output
        except Exception as e:
            print(f"   ⚠️ Playwright Python failed: {e}")
            pass
        
        # Method 2: WeasyPrint CLI
        try:
            print("   Trying WeasyPrint CLI fallback...")
            env_vars = os.environ.copy()
            if platform.system() == "Darwin":
                brew_lib = "/opt/homebrew/lib"
                current = env_vars.get("DYLD_FALLBACK_LIBRARY_PATH", "")
                env_vars["DYLD_FALLBACK_LIBRARY_PATH"] = (
                    f"{brew_lib}:{current}" if current else f"{brew_lib}:/usr/lib"
                )
            
            result = _sp.run(
                ["weasyprint", tmp_html, abs_output],
                capture_output=True,
                text=True,
                timeout=60,
                env=env_vars,
            )
            if result.returncode == 0 and os.path.exists(abs_output) and os.path.getsize(abs_output) > 0:
                print(f"PDF generated (WeasyPrint): {abs_output}")
                return abs_output
        except Exception as e:
            print(f"   ⚠️ WeasyPrint CLI failed: {e}")
            pass
        
        raise RuntimeError("PDF generation failed with both Playwright and WeasyPrint.")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def generate_html(context: dict, output_path: str) -> str:
    """
    Generate the interactive HTML newspaper page.
    
    Args:
        context: Template context dict with date, stories, sections, etc.
        output_path: Path to save the HTML file.
        
    Returns:
        The absolute path to the generated HTML.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("newspaper.html")
    
    # Render the template
    html_content = template.render(**context)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write HTML
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Copy styles.css alongside the HTML for standalone viewing
    import shutil
    css_src = TEMPLATES_DIR / "styles.css"
    css_dst = Path(os.path.dirname(output_path)) / "styles.css"
    if css_src.exists():
        shutil.copy2(css_src, css_dst)
    
    print(f"HTML generated: {output_path}")
    return os.path.abspath(output_path)


if __name__ == "__main__":
    # Test with sample context
    sample_context = {
        "date": "Friday, July 11, 2026",
        "date_iso": "2026-07-11",
        "edition_number": 1,
        "newspaper_name": "THE DAILY FINANCE BRIEF",
        "tagline": "Financial News in Plain English",
        "lead_story": {
            "headline": "Federal Reserve Holds Interest Rates Steady",
            "summary": "<p>The Federal Reserve (the U.S. central bank) decided to keep interest rates unchanged today.</p>",
            "deep_dive": "<p>Detailed explanation here...</p>",
            "category": "economy",
            "source_url": "https://example.com",
            "source_name": "Reuters",
            "importance_rank": 1,
        },
        "sections": {
            "markets": [],
            "economy": [],
            "companies": [],
            "explainer": [],
        },
        "all_stories": [],
        "disclaimer": "Generated by AI · Not financial advice",
    }
    
    generate_html(sample_context, "output/test/test.html")
    print("Test HTML generated successfully!")

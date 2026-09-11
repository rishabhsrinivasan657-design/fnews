# fnews - Daily Personal Finance Newspaper

An automated pipeline that fetches daily personal finance news, rewrites it into plain English with inline definitions, formats it into a stunning Wall Street Journal-style digital and printable newspaper, and delivers it via email and web.

## Features
*   **Automated News Fetching:** Uses OpenAI to pull the latest top stories in personal finance, markets, and the economy.
*   **Plain English Rewriting:** Leverages `gpt-4o-mini` to rewrite complex financial jargon into easy-to-understand language.
*   **WSJ-Style Aesthetics:** Beautifully crafted HTML and CSS mimicking the classic print newspaper feel (cream background, serif fonts, double rules, multi-column layout).
*   **PDF Generation:** Headless PDF rendering using Playwright for a perfect 2-page print layout.
*   **Email Delivery:** Automatically emails the generated PDF to your inbox every morning.
*   **GitHub Actions Automation:** Fully automated via GitHub Actions, running daily at 7:00 AM EDT.

## Tech Stack
*   **Python 3:** Core pipeline orchestrator.
*   **OpenAI API:** `gpt-4o-mini` for cost-effective, high-quality content rewriting.
*   **Playwright:** Chromium-based headless browser for robust PDF generation.
*   **Jinja2 & HTML/CSS:** Templating engine and responsive styling.
*   **GitHub Actions:** CI/CD for cron scheduling and automated deployments.

## Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/rishabhsrinivasan657-design/fnews.git
   cd fnews
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Create a `.env` file in the root directory and fill in your secrets:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GMAIL_SENDER=your_gmail_address
   GMAIL_APP_PASSWORD=your_gmail_app_password
   RECIPIENT_EMAIL=recipient_email_address
   ```
   *(Note: You need to generate an App Password in your Google Account settings if you have 2FA enabled for Gmail).*

4. Run the pipeline manually:
   ```bash
   python src/pipeline.py
   ```

## Automation (GitHub Actions)
To run this automatically on GitHub:
1. Go to your repository **Settings** > **Secrets and variables** > **Actions**.
2. Add the following Repository Secrets:
   * `OPENAI_API_KEY`
   * `GMAIL_SENDER`
   * `GMAIL_APP_PASSWORD`
   * `RECIPIENT_EMAIL`
3. The `.github/workflows/daily_newspaper.yml` workflow will automatically trigger every day at 11:00 UTC (7:00 AM EDT). You can also trigger it manually from the "Actions" tab.

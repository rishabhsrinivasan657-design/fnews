"""
emailer.py — Sends the daily finance newspaper via Gmail SMTP.

Sends an email with:
- The PDF newspaper as an attachment
- A link to the hosted HTML version
- A preview of today's top headlines in the email body
"""

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path


def send_newspaper_email(
    pdf_path: str,
    html_url: str | None,
    stories: list[dict],
    date: str,
    recipient: str | None = None,
    gmail_address: str | None = None,
    gmail_app_password: str | None = None,
) -> bool:
    """
    Send the daily finance newspaper via email.
    
    Args:
        pdf_path: Path to the generated PDF file.
        html_url: URL to the hosted HTML version (optional).
        stories: List of story dicts (for the email body preview).
        date: Human-readable date string (e.g., "Friday, July 11, 2026").
        recipient: Recipient email address. Defaults to RECIPIENT_EMAIL env var.
        gmail_address: Sender Gmail address. Defaults to GMAIL_ADDRESS env var.
        gmail_app_password: Gmail App Password. Defaults to GMAIL_APP_PASSWORD env var.
        
    Returns:
        True if email was sent successfully, False otherwise.
    """
    # Get credentials from env vars if not provided
    recipient = recipient or os.environ.get("RECIPIENT_EMAIL")
    gmail_address = gmail_address or os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = gmail_app_password or os.environ.get("GMAIL_APP_PASSWORD")
    
    if not all([recipient, gmail_address, gmail_app_password]):
        print("⚠️  Email not configured. Set GMAIL_ADDRESS, GMAIL_APP_PASSWORD, and RECIPIENT_EMAIL.")
        print("   Skipping email delivery. PDF and HTML are available locally.")
        return False
    
    # Build the email
    msg = EmailMessage()
    msg["Subject"] = f"📰 Daily Finance Brief — {date}"
    msg["From"] = f"Daily Finance Brief <{gmail_address}>"
    msg["To"] = recipient
    
    # Build HTML email body with preview of top stories
    top_stories = sorted(stories, key=lambda s: s.get("importance_rank", 99))[:3]
    
    stories_html = ""
    for story in top_stories:
        category_label = story["category"].upper()
        stories_html += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #e5e1d8;">
                <span style="font-size: 11px; color: #8b8378; letter-spacing: 1px; 
                       text-transform: uppercase;">{category_label}</span>
                <h3 style="margin: 4px 0 6px; font-family: Georgia, 'Times New Roman', serif; 
                    font-size: 16px; color: #1a1a1a; line-height: 1.3;">
                    {story['headline']}
                </h3>
            </td>
        </tr>"""
    
    html_link_section = ""
    if html_url:
        html_link_section = f"""
        <tr>
            <td style="padding: 16px 0;">
                <a href="{html_url}" style="display: inline-block; padding: 10px 24px; 
                   background: #1a1a1a; color: #faf8f0; text-decoration: none; 
                   font-family: Georgia, serif; font-size: 14px; border-radius: 2px;">
                    Read Interactive Edition →
                </a>
            </td>
        </tr>"""
    
    html_body = f"""
    <html>
    <body style="margin: 0; padding: 0; background: #f5f3eb;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 560px; 
               margin: 0 auto; background: #faf8f0; font-family: Georgia, 'Times New Roman', serif;">
            <tr>
                <td style="padding: 32px 24px 16px; text-align: center; 
                    border-bottom: 3px double #1a1a1a;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: 700; 
                        color: #1a1a1a; letter-spacing: 2px; 
                        font-family: Georgia, 'Times New Roman', serif;">
                        THE DAILY FINANCE BRIEF
                    </h1>
                    <p style="margin: 8px 0 0; font-size: 13px; color: #8b8378; 
                       font-style: italic;">
                        {date} · Financial News in Plain English
                    </p>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px 24px 8px;">
                    <p style="margin: 0 0 12px; font-size: 14px; color: #4a4a4a; 
                       line-height: 1.5;">
                        Good morning! Here are today's top finance stories, 
                        explained in plain English. The full PDF is attached.
                    </p>
                </td>
            </tr>
            <tr>
                <td style="padding: 0 24px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        {stories_html}
                    </table>
                </td>
            </tr>
            {html_link_section}
            <tr>
                <td style="padding: 20px 24px; border-top: 1px solid #e5e1d8; 
                    text-align: center;">
                    <p style="margin: 0; font-size: 11px; color: #b0a898; 
                       font-style: italic;">
                        Generated by AI · Not financial advice · 
                        PDF attached for offline reading
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>"""
    
    # Set email content
    msg.set_content(
        f"Daily Finance Brief — {date}\n\n"
        + "\n".join(f"• {s['headline']}" for s in top_stories)
        + "\n\nSee attached PDF for the full newspaper."
    )
    msg.add_alternative(html_body, subtype="html")
    
    # Attach PDF
    pdf_file = Path(pdf_path)
    if pdf_file.exists():
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()
        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=f"daily_finance_brief_{datetime.now().strftime('%Y_%m_%d')}.pdf",
        )
    else:
        print(f"⚠️  PDF not found at {pdf_path}, sending email without attachment.")
    
    # Send via Gmail SMTP
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_password)
            server.send_message(msg)
        
        print(f"✅ Email sent to {recipient}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail authentication failed. Check your GMAIL_APP_PASSWORD.")
        print("   Set up an App Password at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    # Test email (will skip if credentials not configured)
    send_newspaper_email(
        pdf_path="output/test/daily_finance_brief.pdf",
        html_url=None,
        stories=[{
            "headline": "Test Story Headline",
            "category": "markets",
            "importance_rank": 1,
        }],
        date="Friday, July 11, 2026",
    )

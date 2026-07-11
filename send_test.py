"""
send_test.py — Helper script to test email delivery.
Reads credentials from .env and sends today's generated PDF.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.emailer import send_newspaper_email
from generate_sample import SAMPLE_STORIES

def test_send():
    pdf_path = "output/2026-07-11/daily_finance_brief.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found at {pdf_path}. Please run generate_sample.py first.")
        return
        
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL")
    
    if not app_password or app_password == "YOUR_GMAIL_APP_PASSWORD_HERE":
        print("❌ GMAIL_APP_PASSWORD is not configured in .env.")
        print("   Please open the .env file and replace YOUR_GMAIL_APP_PASSWORD_HERE with your 16-character Google App Password.")
        return
        
    print(f"📧 Attempting to send test email to {recipient}...")
    print(f"   From: {gmail_address}")
    
    success = send_newspaper_email(
        pdf_path=pdf_path,
        html_url="https://rishabhsrinivasan.github.io/fnews/output/latest/index.html",
        stories=SAMPLE_STORIES,
        date="Saturday, July 11, 2026",
    )
    
    if success:
        print("🎉 Test email sent successfully! Check your inbox.")
    else:
        print("❌ Email delivery failed. Please check the credentials and errors above.")

if __name__ == "__main__":
    test_send()

"""
generate_sample.py — Generate a first edition with sample data for design review.
This lets us verify the WSJ template, PDF rendering, and expand/collapse
without needing live API calls.
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pdf_generator import generate_pdf, generate_html

SAMPLE_STORIES = [
    {
        "headline": "S&P 500 Surges Past 6,000 as Tech Rally Extends Into Third Week",
        "summary": (
            "<p>The S&P 500 (an index that tracks the stock prices of the 500 largest "
            "U.S. companies — think of it as a scoreboard for the overall stock market) "
            "climbed above 6,000 points for the first time ever on Thursday, driven by "
            "a powerful rally in technology stocks.</p>"
            "<p>The index rose 1.4%, or about 83 points, with companies like Nvidia (a maker "
            "of computer chips used in artificial intelligence), Apple, and Microsoft "
            "leading the charge. The Nasdaq Composite (another index, but focused on "
            "tech-heavy companies) jumped even higher, gaining 2.1%.</p>"
            "<p>Why does this matter to you? If you have a 401(k) retirement account or "
            "any investments in index funds (funds that automatically buy all the stocks "
            "in an index), your savings likely grew today. The market has now gained "
            "about 18% this year, which is well above the historical average of roughly "
            "10% per year.</p>"
        ),
        "deep_dive": (
            "<p>The rally was sparked by stronger-than-expected earnings reports from "
            "major tech companies. Nvidia reported revenue of $44 billion for the quarter — "
            "more than triple what it earned a year ago — as companies race to build "
            "AI data centers. 'Earnings' are a company's profits, and when profits beat "
            "what Wall Street analysts predicted, the stock price usually goes up.</p>"
            "<p>But not everyone is celebrating. Some market experts warn that stocks may be "
            "'overvalued' — meaning their prices are higher than what the companies are "
            "actually worth based on their earnings. A common measure called the P/E ratio "
            "(price-to-earnings ratio — basically how many dollars investors are paying for "
            "each dollar of profit) is now at 23, compared to a historical average of 16.</p>"
            "<p>What happens next? Analysts are watching two things: (1) whether the Federal "
            "Reserve (the U.S. central bank) will cut interest rates in September, which would "
            "make stocks more attractive compared to bonds; and (2) whether AI spending by "
            "companies will actually translate into real revenue growth, or if it's just hype.</p>"
            "<p>For everyday investors, the advice from most financial planners remains the same: "
            "don't try to time the market. Keep contributing to your retirement accounts "
            "regularly, and don't panic if the market dips after a big run-up like this.</p>"
        ),
        "category": "markets",
        "source_url": "https://www.reuters.com/markets/us",
        "source_name": "Reuters",
        "importance_rank": 1,
    },
    {
        "headline": "Federal Reserve Signals September Rate Cut as Inflation Cools",
        "summary": (
            "<p>The Federal Reserve (the Fed — the U.S. central bank that controls "
            "interest rates) strongly hinted on Wednesday that it will begin cutting "
            "interest rates at its September meeting, after months of holding them at "
            "their highest level in over 20 years.</p>"
            "<p>Interest rates are essentially the 'price of borrowing money.' When the "
            "Fed raises rates, everything from mortgages to car loans to credit card debt "
            "becomes more expensive. The Fed has kept its benchmark rate (called the federal "
            "funds rate) at 5.25–5.50% since July 2023 to fight inflation — the general "
            "rise in prices of everyday goods and services.</p>"
            "<p>Fed Chair Jerome Powell said inflation has made 'considerable further "
            "progress' toward the Fed's 2% target. The latest data shows inflation at "
            "2.5%, down from a peak of 9.1% in June 2022.</p>"
        ),
        "deep_dive": (
            "<p>To understand why this matters so much, let's back up. In 2021 and 2022, "
            "prices for everyday things — groceries, gas, rent — surged at the fastest "
            "pace in 40 years. The Fed's main tool to fight inflation is raising interest "
            "rates, which makes borrowing more expensive and slows down spending.</p>"
            "<p>Think of it like a thermostat: when the economy runs too hot (prices rising "
            "fast), the Fed turns up rates to cool things down. The problem is that cooling "
            "the economy too much can cause a recession (a period when the economy shrinks "
            "and people lose jobs).</p>"
            "<p>Now, with inflation falling close to the Fed's 2% goal, the risk shifts. "
            "If the Fed keeps rates too high for too long, it could unnecessarily hurt "
            "the job market. Powell acknowledged this, saying the Fed is now watching "
            "'both sides' of its mandate — keeping prices stable AND maintaining maximum "
            "employment.</p>"
            "<p>What this means for you: If you're looking to buy a home, mortgage rates "
            "(currently around 6.8%) could drop to around 6% by early 2027 if the Fed "
            "cuts rates as expected. If you carry credit card debt, your interest charges "
            "may also decrease. And if you have savings in a high-yield savings account, "
            "the interest you earn will likely decline — so now might be a good time to "
            "lock in a CD (certificate of deposit — a savings product that guarantees a "
            "fixed interest rate for a set period).</p>"
        ),
        "category": "economy",
        "source_url": "https://www.cnbc.com/economy",
        "source_name": "CNBC",
        "importance_rank": 2,
    },
    {
        "headline": "Oil Prices Climb 4% on Middle East Supply Disruption Fears",
        "summary": (
            "<p>Oil prices jumped nearly 4% on Thursday after reports of potential "
            "supply disruptions in the Middle East. Brent crude (the global benchmark "
            "for oil prices, named after a North Sea oil field) rose to $87.50 per "
            "barrel, while WTI crude (West Texas Intermediate, the U.S. benchmark) "
            "hit $83.20.</p>"
            "<p>The spike came after tensions escalated between Iran and Israel, raising "
            "concerns that oil shipments through the Strait of Hormuz (a narrow waterway "
            "between Iran and the Arabian Peninsula through which about 20% of the world's "
            "oil passes) could be disrupted.</p>"
        ),
        "deep_dive": (
            "<p>Oil prices affect almost everything you buy. When oil gets more expensive, "
            "it costs more to transport goods, grow food (tractors use diesel), and manufacture "
            "products. That's why rising oil prices often lead to higher prices at the grocery "
            "store and the gas pump.</p>"
            "<p>The current spike is being driven by geopolitical risk — a term that describes "
            "the threat of political events (like wars or sanctions) disrupting global trade. "
            "The Middle East produces about 30% of the world's oil, and even the possibility "
            "of supply disruption can send prices soaring.</p>"
            "<p>OPEC+ (the Organization of Petroleum Exporting Countries plus Russia and "
            "other allies — a group of oil-producing nations that coordinate how much oil "
            "to produce) has kept production relatively low to support prices. If tensions "
            "ease, prices could fall back, but if conflict escalates, analysts at Goldman "
            "Sachs warn oil could hit $100 per barrel.</p>"
            "<p>For your wallet: Gas prices, currently averaging $3.45 per gallon nationally, "
            "could rise by 15-25 cents in the coming weeks if oil stays elevated.</p>"
        ),
        "category": "markets",
        "source_url": "https://www.bloomberg.com/energy",
        "source_name": "Bloomberg",
        "importance_rank": 3,
    },
    {
        "headline": "U.S. Economy Added 275,000 Jobs in June, Beating Expectations",
        "summary": (
            "<p>The U.S. economy added 275,000 jobs in June, significantly beating "
            "economists' forecasts of 190,000, according to the Bureau of Labor Statistics "
            "(BLS — the government agency that tracks employment data). The unemployment "
            "rate (the percentage of people who want jobs but can't find them) held steady "
            "at 3.7%.</p>"
            "<p>Healthcare, technology, and government sectors led the job gains. Average "
            "hourly wages (what workers earn per hour, on average) rose 3.9% compared to "
            "a year ago — still above inflation, meaning workers' paychecks are buying "
            "more than they did last year.</p>"
        ),
        "deep_dive": (
            "<p>The monthly jobs report is one of the most closely watched economic indicators "
            "in the world. It tells us whether the economy is growing (more jobs = more people "
            "earning and spending money) or shrinking (fewer jobs = less spending, potential "
            "recession).</p>"
            "<p>The June numbers are particularly important because they suggest the economy "
            "is achieving what economists call a 'soft landing' — bringing inflation down "
            "without causing a recession. This is extremely rare and has only happened once "
            "before in modern history (in 1995).</p>"
            "<p>Breaking down the numbers: Healthcare added 68,000 jobs (hospitals, clinics, "
            "home health aides); tech added 42,000 (software, data centers, IT services); "
            "and state and local governments added 51,000 (teachers, police, firefighters).</p>"
            "<p>One concern: the manufacturing sector lost 8,000 jobs, continuing a trend "
            "as factories automate more processes. This matters because manufacturing jobs "
            "tend to pay well and don't require a college degree.</p>"
            "<p>What this means for you: A strong job market means it's still a relatively "
            "good time to look for work or ask for a raise. However, the Fed may interpret "
            "these strong numbers as a sign that it can wait a bit longer before cutting "
            "interest rates.</p>"
        ),
        "category": "economy",
        "source_url": "https://www.wsj.com/economy/jobs",
        "source_name": "The Wall Street Journal",
        "importance_rank": 4,
    },
    {
        "headline": "Apple Unveils 'Apple Intelligence' — Its Biggest AI Push Yet",
        "summary": (
            "<p>Apple announced a sweeping set of artificial intelligence features called "
            "'Apple Intelligence' that will be built into iPhones, iPads, and Macs starting "
            "this fall. The features include an upgraded Siri that can understand context "
            "and perform multi-step tasks, AI-powered writing and editing tools, and the "
            "ability to generate images from text descriptions.</p>"
            "<p>Apple's stock rose 3.2% on the news, adding roughly $100 billion to the "
            "company's market capitalization (market cap — the total value of all the "
            "company's shares combined, calculated by multiplying the stock price by the "
            "number of shares). Apple is now worth approximately $3.5 trillion.</p>"
        ),
        "deep_dive": (
            "<p>Apple has been notably late to the AI race compared to competitors like "
            "Google and Microsoft, who have been integrating AI into their products for "
            "over a year. But Apple's approach is different: rather than running AI in the "
            "cloud (on distant servers), much of Apple Intelligence will run directly on "
            "your device. This means your personal data stays on your phone rather than "
            "being sent to a company's servers.</p>"
            "<p>The privacy angle is significant. When you use ChatGPT or Google's AI, your "
            "questions and data are processed on those companies' servers. Apple promises "
            "that most AI processing happens on-device, using a new 'Private Cloud Compute' "
            "system for tasks that need more computing power.</p>"
            "<p>Investors are excited because AI features could drive a massive iPhone upgrade "
            "cycle. Apple Intelligence will only work on iPhone 16 and newer models, meaning "
            "hundreds of millions of people with older iPhones may upgrade. Wall Street "
            "analysts estimate this could add $30-50 billion in additional revenue over the "
            "next two years.</p>"
            "<p>The partnership with OpenAI (the maker of ChatGPT) is also noteworthy — Apple "
            "will integrate ChatGPT as an optional feature within Siri, letting users access "
            "it without downloading a separate app.</p>"
        ),
        "category": "companies",
        "source_url": "https://www.theverge.com/apple",
        "source_name": "The Verge",
        "importance_rank": 5,
    },
    {
        "headline": "Boeing Reaches $2.5 Billion Settlement Over 737 MAX Crashes",
        "summary": (
            "<p>Boeing has agreed to pay $2.5 billion to settle criminal charges related "
            "to two fatal crashes of its 737 MAX aircraft that killed 346 people in 2018 "
            "and 2019. The crashes in Indonesia and Ethiopia were caused by a faulty "
            "automated flight system called MCAS that pushed the planes' noses down "
            "repeatedly, and which pilots were not adequately trained to handle.</p>"
            "<p>The settlement includes $500 million in fines, $1.77 billion in compensation "
            "to airlines that couldn't use their MAX planes during a 20-month grounding "
            "(a period when regulators banned the aircraft from flying), and $243 million "
            "to establish a safety fund.</p>"
        ),
        "deep_dive": (
            "<p>This settlement closes one of the darkest chapters in aviation history, but "
            "many victims' families say it doesn't go far enough. No Boeing executives will "
            "face personal criminal charges, which critics call a failure of accountability.</p>"
            "<p>The 737 MAX crisis started with a design flaw. Boeing added larger engines "
            "to the 737 to compete with Airbus's A320neo. The bigger engines changed how "
            "the plane flew, so Boeing created MCAS (Maneuvering Characteristics Augmentation "
            "System) — software that automatically pushed the nose down in certain conditions. "
            "The problem: MCAS relied on a single sensor, and if that sensor failed (which it "
            "did in both crashes), the system could push the nose down uncontrollably.</p>"
            "<p>Boeing's stock has fallen roughly 25% over the past year as it deals with "
            "additional safety concerns, including a door plug blowout on a 737 MAX 9 in "
            "January. The company has brought in a new CEO and is trying to rebuild trust "
            "with regulators and the public.</p>"
            "<p>For travelers: The 737 MAX has been extensively redesigned and re-certified "
            "by the FAA (Federal Aviation Administration). Aviation experts say it is now "
            "safe to fly, but Boeing faces ongoing scrutiny of its quality control.</p>"
        ),
        "category": "companies",
        "source_url": "https://www.nytimes.com/business",
        "source_name": "The New York Times",
        "importance_rank": 6,
    },
    {
        "headline": "What Is a Bond Yield — and Why Is Everyone Talking About It?",
        "summary": (
            "<p>You've probably heard the term 'bond yields' on the news lately. Here's "
            "what it means: A bond is essentially an IOU. When you buy a government bond, "
            "you're lending money to the government. In return, they promise to pay you "
            "back with interest. The 'yield' is the annual return you earn from that bond, "
            "expressed as a percentage.</p>"
            "<p>The 10-year Treasury yield (the return on lending money to the U.S. government "
            "for 10 years) is currently at 4.25%, its highest level since 2007. This matters "
            "because the 10-year yield acts as a benchmark that influences mortgage rates, "
            "car loan rates, and corporate borrowing costs.</p>"
        ),
        "deep_dive": (
            "<p>Here's the key thing to understand: bond prices and yields move in opposite "
            "directions. Imagine you buy a bond that pays 3% interest. If the government "
            "later issues new bonds paying 5%, nobody wants your old 3% bond anymore — so "
            "its price falls. When the price falls, the effective yield goes up. This "
            "inverse relationship is one of the most important concepts in finance.</p>"
            "<p>Why are bond yields so high right now? Two main reasons: (1) The Federal "
            "Reserve has raised interest rates aggressively, making new bonds pay more. "
            "(2) The U.S. government is borrowing record amounts of money (the national "
            "debt is over $35 trillion), and when there's more supply of bonds, prices "
            "fall and yields rise.</p>"
            "<p>Why should you care? Higher bond yields affect you in several ways: "
            "Mortgage rates closely track the 10-year Treasury yield, so high yields mean "
            "expensive home loans. Savings accounts and CDs pay more (the flip side of "
            "higher rates). And the stock market often struggles when bond yields are high, "
            "because investors can earn good returns from safe bonds instead of risky stocks.</p>"
            "<p>The current high yields also present an opportunity. For the first time in "
            "years, you can earn 4-5% from very safe investments like Treasury bonds or "
            "high-yield savings accounts. Financial advisors call this a 'generational "
            "opportunity' for savers who were earning near-zero interest for most of the "
            "2010s.</p>"
        ),
        "category": "explainer",
        "source_url": "https://www.investopedia.com/terms/b/bondyield.asp",
        "source_name": "Investopedia",
        "importance_rank": 7,
    },
]


def build_context(stories):
    """Build the template context from sample stories."""
    lead = stories[0]
    remaining = stories[1:]

    sections = {"markets": [], "economy": [], "companies": [], "explainer": []}
    for s in remaining:
        cat = s.get("category", "companies")
        if cat in sections:
            sections[cat].append(s)

    return {
        "date": "Friday, July 11, 2026",
        "date_iso": "2026-07-11",
        "edition_number": 1,
        "newspaper_name": "THE DAILY FINANCE BRIEF",
        "tagline": "Financial News in Plain English",
        "lead_story": lead,
        "sections": sections,
        "all_stories": stories,
        "disclaimer": "Generated by AI · Not financial advice",
    }


def main():
    context = build_context(SAMPLE_STORIES)
    output_dir = PROJECT_ROOT / "output" / "2026-07-11"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Also create 'latest' symlink
    latest = PROJECT_ROOT / "output" / "latest"
    if latest.is_symlink():
        latest.unlink()
    elif latest.exists():
        import shutil
        shutil.rmtree(latest)
    latest.symlink_to(output_dir.resolve())

    # Generate HTML
    html_path = str(output_dir / "index.html")
    generate_html(context, html_path)

    # Generate PDF
    pdf_path = str(output_dir / "daily_finance_brief.pdf")
    try:
        generate_pdf(context, pdf_path)
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
        print("   HTML is still available.")

    # Save data
    data_path = output_dir / "data.json"
    with open(data_path, "w") as f:
        json.dump({"stories": SAMPLE_STORIES}, f, indent=2)

    print(f"\n✅ Sample edition generated!")
    print(f"   HTML: {html_path}")
    print(f"   PDF:  {pdf_path}")
    print(f"\n   Open the HTML in your browser:")
    print(f"   open {html_path}")


if __name__ == "__main__":
    main()

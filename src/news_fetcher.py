"""
news_fetcher.py — Fetches the latest financial news using OpenAI's web_search tool.

Uses GPT-4.1 with the built-in web_search tool to find and extract
financial/economic news from the last 24 hours across four categories:
Markets, Economy, Companies/Business, and an Explainer topic.
"""

import json
import os
from datetime import datetime
from openai import OpenAI


def fetch_news(date: str | None = None) -> list[dict]:
    """
    Fetch the latest financial news stories from the web.
    
    Uses OpenAI's web_search tool to search for and extract
    financial news from the last 24 hours.
    
    Args:
        date: ISO date string (YYYY-MM-DD). Defaults to today.
        
    Returns:
        List of raw story dicts with keys:
            - headline: str
            - raw_summary: str  
            - source_url: str
            - source_name: str
            - category: str ("markets" | "economy" | "companies" | "explainer")
    """
    client = OpenAI()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    today_readable = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
    
    system_prompt = f"""You are a financial news researcher. Today is {today_readable}.

Your job is to search the web for the most important financial and economic news 
from the LAST 24 HOURS and return them as structured data.

SEARCH STRATEGY:
- Search for today's top financial news, stock market movements, economic data releases
- Search for major corporate news, earnings, mergers, layoffs
- Search for central bank decisions, inflation data, jobs reports
- Search for any finance concept currently trending in the news (for the Explainer)

CATEGORIES TO COVER:
1. "markets" — Stock market movements, major index changes (S&P 500, Dow, Nasdaq), 
   notable stock moves, bond yields, commodities, crypto. Find 2 stories.
2. "economy" — Inflation data, interest rate decisions, jobs reports, GDP, 
   trade data, government policy. Find 2 stories.
3. "companies" — Major corporate news: earnings, M&A, product launches, 
   layoffs, leadership changes, lawsuits. Find 2 stories.
4. "explainer" — Identify ONE finance concept or term that is currently in the 
   news and would benefit from explanation (e.g., "yield curve inversion", 
   "stock buyback", "tariffs"). Find 1 topic.

SELECTION CRITERIA:
- Pick stories that would matter to ordinary people (not just traders)
- Prioritize stories with real-world impact on jobs, prices, savings, etc.
- For the explainer, pick something that appeared in multiple news stories today

Return EXACTLY 7 stories total (2 markets + 2 economy + 2 companies + 1 explainer).

OUTPUT FORMAT:
Return a JSON array of objects, each with these fields:
- "headline": A clear, factual headline (not clickbait)
- "raw_summary": 2-3 paragraphs summarizing the key facts. Include specific 
  numbers, dates, names, and context. This will be rewritten later, so focus 
  on capturing ALL the important details.
- "source_url": The URL of the primary source you found this from
- "source_name": Name of the source (e.g., "Reuters", "CNBC", "Bloomberg")
- "category": One of "markets", "economy", "companies", "explainer"

For the "explainer" story:
- "headline" should be the concept name (e.g., "What Is a Yield Curve Inversion?")
- "raw_summary" should explain what the concept is and why it's in the news right now

Return ONLY the JSON array, no other text."""

    response = client.responses.create(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"Search the web for today's ({today_readable}) most important "
                f"financial and economic news. Find 7 stories across markets, "
                f"economy, companies, and one explainer topic. "
                f"Return them as a JSON array."
            )},
        ],
        temperature=0.3,
    )
    
    # Extract the text content from the response
    raw_text = ""
    for item in response.output:
        if item.type == "message":
            for content_block in item.content:
                if content_block.type == "output_text":
                    raw_text = content_block.text
                    break
    
    # Parse JSON from the response (handle markdown code fences)
    json_text = raw_text.strip()
    if json_text.startswith("```"):
        # Remove markdown code fences
        lines = json_text.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        json_text = "\n".join(lines)
    
    try:
        stories = json.loads(json_text)
    except json.JSONDecodeError:
        # Try to extract JSON array from the text
        start = json_text.find("[")
        end = json_text.rfind("]") + 1
        if start != -1 and end > start:
            stories = json.loads(json_text[start:end])
        else:
            raise ValueError(f"Could not parse JSON from response: {json_text[:500]}")
    
    # Validate and normalize
    validated = []
    for story in stories:
        validated.append({
            "headline": story.get("headline", "Untitled"),
            "raw_summary": story.get("raw_summary", ""),
            "source_url": story.get("source_url", "#"),
            "source_name": story.get("source_name", "Unknown"),
            "category": story.get("category", "companies"),
        })
    
    return validated


if __name__ == "__main__":
    print("Fetching today's financial news...")
    stories = fetch_news()
    print(f"\nFound {len(stories)} stories:\n")
    for i, story in enumerate(stories, 1):
        print(f"{i}. [{story['category'].upper()}] {story['headline']}")
        print(f"   Source: {story['source_name']} — {story['source_url']}")
        print(f"   Summary: {story['raw_summary'][:150]}...")
        print()

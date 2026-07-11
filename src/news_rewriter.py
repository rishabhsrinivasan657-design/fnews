"""
news_rewriter.py — Rewrites raw financial news in beginner-friendly English.

Takes raw news stories from the fetcher and uses OpenAI gpt-4o-mini in a single
batched call to rank and rewrite all stories, saving over 90% in token costs.
"""

import json
from openai import OpenAI


def rewrite_stories(raw_stories: list[dict]) -> list[dict]:
    """
    Rewrite raw news stories in beginner-friendly English in a single batch call.
    
    Uses gpt-4o-mini (highly cost-effective) to rank and rewrite all 7 stories
    at once, which reduces prompt token overhead and saves API cost.
    
    Args:
        raw_stories: List of raw story dicts from news_fetcher.fetch_news()
        
    Returns:
        List of rewritten story dicts with keys:
            - headline: str (rewritten for clarity)
            - summary: str (150-250 words, HTML paragraphs)
            - deep_dive: str (400-600 words, HTML paragraphs)
            - category: str
            - source_url: str
            - source_name: str
            - importance_rank: int (1 = most important)
    """
    client = OpenAI()
    
    # Prepare batch prompt
    stories_input = []
    for i, s in enumerate(raw_stories):
        stories_input.append({
            "index": i,
            "headline": s["headline"],
            "category": s["category"],
            "source_name": s["source_name"],
            "source_url": s["source_url"],
            "content": s["raw_summary"]
        })
        
    prompt = f"""You are a financial journalist and editor writing a personal finance newspaper for beginners.
Your goal is to explain the day's financial news to someone with ZERO finance background.

Task:
1. Rank these {len(raw_stories)} stories by importance to ordinary people (1 = most important to their daily lives/wallet, 7 = least important).
2. Rewrite each story's headline, summary, and deep dive according to the rules below.

Stories to process:
{json.dumps(stories_input, indent=2)}

Rules for Rewriting:
1. Plain English: Assume the reader knows absolutely nothing about finance. Define EVERY financial term the first time it is used in each story.
   Examples of definitions:
   - "the Fed" -> "the Federal Reserve (the U.S. central bank that controls interest rates)"
   - "S&P 500" -> "the S&P 500 (an index that tracks the stock prices of 500 large U.S. companies)"
   - "bond yields" -> "bond yields (the return investors earn from lending money to the government)"
   - "basis points" -> "basis points (a unit of measurement in finance, where 100 basis points equals 1 percentage point)"
   - "inflation" -> "inflation (the general rise in prices of goods and services over time)"
2. Summaries: Generate a 150-250 word explanation in HTML paragraphs (<p> tags). Cover the key facts: what happened, why it happened, and what it means for regular people.
3. Deep Dives: Generate a 400-600 word deep-dive in HTML paragraphs (<p> tags). Provide more background, cause-and-effect, what experts are saying, and what happens next.
4. Explainer of the Day (story with category "explainer"): This is a concept definition rather than standard news. Rewrite it to explain what the concept is, why it's in the news today, and how it affects everyday life.

Output Format:
Return a JSON object with a single "stories" key containing the array of processed stories.
Format:
{{
  "stories": [
    {{
      "headline": "Clear, engaging, jargon-free headline",
      "summary": "<p>Summary paragraph 1...</p><p>Summary paragraph 2...</p>",
      "deep_dive": "<p>Deep dive paragraph 1...</p><p>Deep dive paragraph 2...</p><p>...</p>",
      "category": "markets | economy | companies | explainer",
      "source_url": "...",
      "source_name": "...",
      "importance_rank": 1
    }}
  ]
}}

Return ONLY the raw JSON object, no markdown styling or code fences."""

    # Using gpt-4o-mini which is extremely cheap ($0.15/1M input, $0.60/1M output tokens)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise JSON assistant. Return only valid raw JSON matching the requested structure."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    raw_text = response.choices[0].message.content.strip()
    
    try:
        data = json.loads(raw_text)
        rewritten = data.get("stories", [])
    except json.JSONDecodeError:
        # Fallback in case of parse error: preserve original structure
        print("⚠️ Warning: Failed to parse batch JSON. Using raw fallback.")
        rewritten = []
        for i, s in enumerate(raw_stories):
            rewritten.append({
                "headline": s["headline"],
                "summary": f"<p>{s['raw_summary']}</p>",
                "deep_dive": f"<p>{s['raw_summary']}</p>",
                "category": s["category"],
                "source_url": s["source_url"],
                "source_name": s["source_name"],
                "importance_rank": i + 1
            })
            
    # If LLM returned fewer stories or failed to rank correctly, align ranks
    rewritten.sort(key=lambda s: s.get("importance_rank", 99))
    for i, s in enumerate(rewritten, 1):
        s["importance_rank"] = i
        
    return rewritten

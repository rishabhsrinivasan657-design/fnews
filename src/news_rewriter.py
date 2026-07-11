"""
news_rewriter.py — Rewrites raw financial news in beginner-friendly English.

Takes raw news stories from the fetcher and uses OpenAI to rewrite each one
in plain English, defining every financial term on first use. Produces both
a front-page summary (150-250 words) and a deep-dive explanation (400-600 words).
"""

import json
from openai import OpenAI


def rewrite_stories(raw_stories: list[dict]) -> list[dict]:
    """
    Rewrite raw news stories in beginner-friendly English.
    
    For each story, generates:
    - A front-page summary (150-250 words) for the newspaper layout
    - A deep-dive explanation (400-600 words) for the HTML expandable section
    
    Also ranks stories by importance (1 = most important).
    
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
    
    # First, rank the stories by importance
    ranking_prompt = f"""You are a news editor. Below are {len(raw_stories)} financial news stories 
from today. Rank them from 1 (most important to ordinary people) to {len(raw_stories)} (least important).

Consider: How many people does this affect? Does it impact everyday prices, jobs, 
or savings? Is it historically significant?

Stories:
{json.dumps([{"headline": s["headline"], "category": s["category"], "summary": s["raw_summary"][:200]} for s in raw_stories], indent=2)}

Return a JSON array of objects with "headline" and "rank" (integer 1-{len(raw_stories)}).
Return ONLY the JSON array."""

    ranking_response = client.responses.create(
        model="gpt-4.1",
        input=[{"role": "user", "content": ranking_prompt}],
        temperature=0.2,
    )
    
    ranking_text = ""
    for item in ranking_response.output:
        if item.type == "message":
            for block in item.content:
                if block.type == "output_text":
                    ranking_text = block.text
                    break
    
    # Parse ranking
    ranking_text = ranking_text.strip()
    if ranking_text.startswith("```"):
        lines = ranking_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        ranking_text = "\n".join(lines)
    
    try:
        rankings = json.loads(ranking_text)
        rank_map = {r["headline"]: r["rank"] for r in rankings}
    except (json.JSONDecodeError, KeyError):
        # Fallback: assign ranks by order
        rank_map = {s["headline"]: i + 1 for i, s in enumerate(raw_stories)}
    
    # Now rewrite each story
    rewritten_stories = []
    
    for story in raw_stories:
        rank = rank_map.get(story["headline"], len(raw_stories))
        rewritten = _rewrite_single_story(client, story, rank)
        rewritten_stories.append(rewritten)
    
    # Sort by importance rank
    rewritten_stories.sort(key=lambda s: s["importance_rank"])
    
    return rewritten_stories


def _rewrite_single_story(client: OpenAI, story: dict, rank: int) -> dict:
    """Rewrite a single story in beginner-friendly English."""
    
    is_explainer = story["category"] == "explainer"
    
    if is_explainer:
        rewrite_prompt = f"""You are a financial journalist writing for people with ZERO finance background.

Rewrite the following finance explainer in plain, beginner-friendly English.
This is an "Explainer of the Day" feature — a concept currently in the news.

ORIGINAL:
Headline: {story["headline"]}
Content: {story["raw_summary"]}
Source: {story["source_name"]}

RULES:
- Define EVERY financial term the first time you use it
  Example: "the S&P 500 (an index that tracks the stock prices of the 500 largest 
  U.S. companies — think of it as a scoreboard for the overall stock market)"
- Use analogies and everyday comparisons
- Explain WHY this concept matters to ordinary people
- Explain what's happening RIGHT NOW with this concept in the news

OUTPUT FORMAT (return as JSON):
{{
  "headline": "A clear, engaging headline (keep it simple but informative)",
  "summary": "A 150-250 word explanation in HTML paragraphs (<p> tags). Define the concept clearly, explain why it's in the news today, and why it matters to regular people.",
  "deep_dive": "A 400-600 word deep-dive in HTML paragraphs (<p> tags). Go deeper: history of the concept, real-world examples, what could happen next, how it affects savings/jobs/prices. Still in plain English with all terms defined."
}}

Return ONLY the JSON object."""
    else:
        rewrite_prompt = f"""You are a financial journalist writing for people with ZERO finance background.

Rewrite the following financial news story in plain, beginner-friendly English.
Don't shorten or dumb it down — keep all the important details, just explain 
everything as if the reader has never heard of these concepts before.

ORIGINAL:
Headline: {story["headline"]}
Content: {story["raw_summary"]}
Source: {story["source_name"]}
Category: {story["category"]}

RULES:
- Define EVERY financial term the first time you use it. Examples:
  • "the Fed" → "the Federal Reserve (the U.S. central bank that controls interest rates)"
  • "basis points" → "basis points (a unit used in finance — 100 basis points = 1 percentage point)"
  • "the Dow" → "the Dow Jones Industrial Average (an index tracking 30 major U.S. companies)"
  • "bond yields" → "bond yields (the return investors earn from lending money to the government)"
- Use short sentences and active voice
- Explain cause and effect: "This happened BECAUSE... This means FOR YOU..."
- Include specific numbers, dates, and names from the original
- Don't use jargon without explaining it

OUTPUT FORMAT (return as JSON):
{{
  "headline": "A clear, factual headline rewritten for a general audience",
  "summary": "A 150-250 word summary in HTML paragraphs (<p> tags). Cover the key facts and explain what happened and why it matters. Define all terms on first use.",
  "deep_dive": "A 400-600 word deep-dive in HTML paragraphs (<p> tags). Add more context: what led to this, who's affected, what experts are saying, what could happen next, and what it means for ordinary people's wallets. Still define all terms."
}}

Return ONLY the JSON object."""

    response = client.responses.create(
        model="gpt-4.1",
        input=[{"role": "user", "content": rewrite_prompt}],
        temperature=0.4,
    )
    
    raw_text = ""
    for item in response.output:
        if item.type == "message":
            for block in item.content:
                if block.type == "output_text":
                    raw_text = block.text
                    break
    
    # Parse JSON
    json_text = raw_text.strip()
    if json_text.startswith("```"):
        lines = json_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        json_text = "\n".join(lines)
    
    try:
        rewritten = json.loads(json_text)
    except json.JSONDecodeError:
        start = json_text.find("{")
        end = json_text.rfind("}") + 1
        if start != -1 and end > start:
            rewritten = json.loads(json_text[start:end])
        else:
            # Fallback: use raw content
            rewritten = {
                "headline": story["headline"],
                "summary": f"<p>{story['raw_summary']}</p>",
                "deep_dive": f"<p>{story['raw_summary']}</p>",
            }
    
    return {
        "headline": rewritten.get("headline", story["headline"]),
        "summary": rewritten.get("summary", ""),
        "deep_dive": rewritten.get("deep_dive", ""),
        "category": story["category"],
        "source_url": story["source_url"],
        "source_name": story["source_name"],
        "importance_rank": rank,
    }


if __name__ == "__main__":
    # Quick test with sample data
    sample = [{
        "headline": "Federal Reserve Holds Interest Rates Steady at 5.25-5.50%",
        "raw_summary": "The Federal Reserve kept its benchmark interest rate unchanged at 5.25-5.50% on Wednesday, as expected. Fed Chair Jerome Powell signaled that rate cuts could begin in September if inflation continues to cool. The central bank noted that the labor market has come into better balance and that inflation has made further progress toward the 2% target.",
        "source_url": "https://reuters.com/example",
        "source_name": "Reuters",
        "category": "economy",
    }]
    
    print("Rewriting sample story...")
    result = rewrite_stories(sample)
    print(json.dumps(result, indent=2))

"""
run_local_pipeline.py
---------------------
THE MAIN SCRIPT. Runs the whole CrowdWisdomTrading marketing agent team,
end to end, using the Hermes Agent framework as a Python library.

Pipeline (each step = one specialized agent):

  1. MARKETING MANAGER  -> marketing strategy + competitor research
                           writes: vault/Strategy/Marketing-Strategy.md
                                   vault/Competitors/Competitor-Research.md

  2. ADS MANAGER        -> (a) scrapes winning Meta ads via Apify (last 30 days)
                               saves: output/ads_results.json
                           (b) extracts pains / marketing concepts from them
                               writes: vault/Ads/Ad-Analysis.md
                           (c) writes a new ad script for crowdwisdomtrading.com
                               writes: vault/Ads/Ad-Script.md

  3. INFLUENCER SCOUT   -> finds retail-trading influencers (>200K subs)
                           writes: vault/Influencers/Influencer-Database.md
                           drafts personalized cold outreach
                           writes: vault/Outreach/Cold-Outreach-Drafts.md

  4. STANDUP REPORTER   -> (our own idea) summarizes the whole run into a
                           daily standup note
                           writes: vault/Standups/YYYY-MM-DD-Standup.md

QUALITY LOOP: every agent's output is judged by a reviewer agent. If the
reviewer scores it below 7/10, the worker agent is asked to improve it and
tries again (up to MAX_RETRIES). This is the "loops" evaluation criterion.

Run:  python scripts/run_local_pipeline.py
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# Hermes Agent as a library. Requires OPENROUTER_API_KEY in the environment.
from run_agent import AIAgent  # noqa: E402  (import after dotenv on purpose)

sys.path.insert(0, str(ROOT / "scripts"))
from scrape_meta_ads import main as scrape_ads_main  # noqa: E402

MODEL = os.getenv("HERMES_MODEL", "anthropic/claude-sonnet-4.6")
VAULT = Path(os.getenv("OBSIDIAN_VAULT_PATH", ROOT / "vault"))
MAX_RETRIES = 2  # quality-loop retries per agent

COMPANY_CONTEXT = """
Company: CrowdWisdomTrading (crowdwisdomtrading.com)
What it does: aggregates the "wisdom of the crowd" from retail traders —
tracking what thousands of traders are actually buying/selling and turning
that crowd data into signals, sentiment insight, and market intelligence for
retail investors.
Niche: retail trading / trading signals / market sentiment.
Unique data: real crowd positioning data (what the retail crowd is doing
right now), not just news or price charts.
Audience: retail traders and investors (stocks, options, crypto).
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_agent(system_prompt: str) -> AIAgent:
    """Create a fresh Hermes agent with a role-specific system prompt."""
    return AIAgent(
        model=MODEL,
        quiet_mode=True,
        ephemeral_system_prompt=system_prompt,
    )


def write_note(rel_path: str, content: str) -> Path:
    """Write a markdown note into the Obsidian vault (guaranteed md output)."""
    path = VAULT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"[vault] wrote {path}")
    return path


def quality_loop(worker: AIAgent, task_prompt: str, task_name: str) -> str:
    """Run worker -> reviewer -> (improve) loop until the reviewer is happy."""
    reviewer = make_agent(
        "You are a strict marketing quality reviewer. You are given a task "
        "description and a draft. Reply with EXACTLY one line: "
        "SCORE: <1-10> | FEEDBACK: <one concise sentence of the most "
        "important improvement>. Score 7+ only if the draft is specific, "
        "actionable, and free of generic filler."
    )

    draft = worker.chat(task_prompt)
    for attempt in range(1, MAX_RETRIES + 1):
        verdict = reviewer.chat(
            f"TASK:\n{task_prompt[:2000]}\n\nDRAFT:\n{draft[:6000]}"
        )
        m = re.search(r"SCORE:\s*(\d+)", verdict)
        score = int(m.group(1)) if m else 7
        print(f"[loop] {task_name}: attempt {attempt}, reviewer score = {score}")
        if score >= 7:
            break
        feedback = verdict.split("FEEDBACK:")[-1].strip()
        draft = worker.chat(
            f"A reviewer scored your draft {score}/10 with this feedback: "
            f"'{feedback}'. Rewrite and improve the full draft accordingly. "
            f"Output the complete improved version only."
        )
    return draft


# ---------------------------------------------------------------------------
# Agent 1 — Marketing Manager
# ---------------------------------------------------------------------------
def run_marketing_manager() -> None:
    print("\n=== AGENT 1: Marketing Manager ===")
    agent = make_agent(
        "You are the Marketing Manager agent for CrowdWisdomTrading. "
        "You produce sharp, structured marketing strategy documents in "
        "Markdown with Obsidian [[wikilinks]] between related notes. "
        "You may use your web search tools to gather real, current facts. "
        "No generic fluff — everything must be specific to retail trading."
    )

    strategy = quality_loop(
        agent,
        f"{COMPANY_CONTEXT}\n"
        "Write a complete marketing strategy note in Markdown titled "
        "'# Marketing Strategy — CrowdWisdomTrading'. Include: positioning "
        "statement, 3 target personas (with pains), key messaging pillars, "
        "channel plan (Meta ads, YouTube influencers, X), 30-day action plan "
        "as a checklist, and KPIs. Link to [[Competitor-Research]] and "
        "[[Ad-Script]] where relevant.",
        "marketing-strategy",
    )
    write_note("Strategy/Marketing-Strategy.md", strategy)

    competitors = quality_loop(
        agent,
        f"{COMPANY_CONTEXT}\n"
        "Research REAL competitors in the retail-trading signals / crowd "
        "sentiment space (e.g. tools for trading signals, sentiment tracking, "
        "copy trading). Use web search if available. Write a Markdown note "
        "titled '# Competitor Research'. For each of 5-7 competitors give: "
        "what they do, pricing model if known, their marketing angle, their "
        "weakness, and how CrowdWisdomTrading wins against them. End with a "
        "comparison table and 3 takeaways for our strategy.",
        "competitor-research",
    )
    write_note("Competitors/Competitor-Research.md", competitors)


# ---------------------------------------------------------------------------
# Agent 2 — Ads Manager (scrape -> extract -> script)
# ---------------------------------------------------------------------------
def run_ads_manager() -> None:
    print("\n=== AGENT 2: Ads Manager ===")

    # (a) scrape winning ads via Apify -> output/ads_results.json
    try:
        ads = scrape_ads_main()
    except SystemExit as e:
        print(f"[warn] Apify scrape skipped: {e}")
        ads = []

    ads_sample = json.dumps(ads[:15], ensure_ascii=False, default=str)[:12000]

    analyst = make_agent(
        "You are the Ads Analyst agent. You dissect winning Meta ads and "
        "extract the psychology behind them: pain points, hooks, angles, "
        "offers, and creative concepts. Output clean Markdown."
    )

    # (b) extract pains / concepts
    analysis = quality_loop(
        analyst,
        f"{COMPANY_CONTEXT}\n"
        f"Here is JSON data of currently-running Meta ads in our niche "
        f"(scraped from the Meta Ads Library, last 30 days):\n{ads_sample}\n\n"
        "Write a Markdown note titled '# Ad Analysis — What's Working in "
        "Retail Trading Ads'. Extract: (1) top 5 pain points these ads "
        "target, (2) the hooks/opening lines used, (3) recurring marketing "
        "concepts (urgency, social proof, authority...), (4) offer "
        "structures, (5) a summary table 'Pain -> Angle -> Example'. If the "
        "JSON is empty, derive the analysis from well-known winning patterns "
        "in trading-app advertising and clearly say so.",
        "ad-analysis",
    )
    write_note("Ads/Ad-Analysis.md", analysis)

    # (c) write our ad script
    copywriter = make_agent(
        "You are a direct-response ad copywriter agent. You write video ad "
        "scripts in the style of top-performing Meta ads: strong hook in the "
        "first 3 seconds, agitate the pain, present the mechanism, proof, "
        "clear CTA. Output Markdown."
    )
    script = quality_loop(
        copywriter,
        f"{COMPANY_CONTEXT}\n"
        f"Using this analysis of winning ads:\n{analysis[:6000]}\n\n"
        "Write '# Ad Script — CrowdWisdomTrading (30-45s video)'. Structure: "
        "HOOK (0-3s), PROBLEM (3-10s), MECHANISM — our unique crowd-wisdom "
        "data (10-25s), PROOF (25-35s), CTA (35-45s). Include: spoken lines, "
        "on-screen text, and visual directions per beat, plus 3 alternative "
        "hooks and 2 headline variants for the ad card. Link to "
        "[[Ad-Analysis]].",
        "ad-script",
    )
    write_note("Ads/Ad-Script.md", script)


# ---------------------------------------------------------------------------
# Agent 3 — Influencer Scout + Cold Outreach
# ---------------------------------------------------------------------------
def run_influencer_scout() -> None:
    print("\n=== AGENT 3: Influencer Scout ===")
    scout = make_agent(
        "You are the Influencer Scout agent. You research REAL influencers "
        "in the retail trading niche using your web search / browser tools. "
        "Never invent follower counts — mark estimates as 'approx'. Output "
        "clean Markdown tables."
    )

    database = quality_loop(
        scout,
        "Find 8-12 REAL influencers in the 'retail trading' niche with more "
        "than 200K subscribers/followers on YouTube, X (Twitter), Instagram "
        "or TikTok. Use web search. Write a Markdown note titled "
        "'# Influencer Database — Retail Trading'. For each influencer "
        "capture EVERYTHING useful: name, handle(s), platform(s), subscriber/"
        "follower count (mark approx), content style, typical topics, "
        "audience type, posting frequency, best contact method (email/DM), "
        "and a one-line note on why they fit CrowdWisdomTrading. Put it all "
        "in one big table plus short profiles below.",
        "influencer-database",
    )
    write_note("Influencers/Influencer-Database.md", database)

    writer = make_agent(
        "You are the Cold Outreach agent. You write short, personal, "
        "non-salesy outreach messages that ask for the influencer's OPINION "
        "about a product (soft-touch approach), not for a paid promo. "
        "Output Markdown."
    )
    outreach = quality_loop(
        writer,
        f"{COMPANY_CONTEXT}\n"
        f"Here is our influencer database:\n{database[:8000]}\n\n"
        "Write '# Cold Outreach Drafts'. For EACH influencer in the "
        "database, draft a personalized message (max 120 words) that: "
        "references something specific they made, briefly introduces "
        "crowdwisdomtrading.com in one sentence, and asks for their honest "
        "opinion about it. Vary the tone per platform (email vs X DM vs IG "
        "DM). Link to [[Influencer-Database]].",
        "cold-outreach",
    )
    write_note("Outreach/Cold-Outreach-Drafts.md", outreach)


# ---------------------------------------------------------------------------
# Agent 4 — OUR IDEA: Daily Marketing Standup Reporter
# ---------------------------------------------------------------------------
def run_standup_reporter() -> None:
    print("\n=== AGENT 4: Standup Reporter (our idea) ===")
    notes = []
    for rel in [
        "Strategy/Marketing-Strategy.md",
        "Competitors/Competitor-Research.md",
        "Ads/Ad-Analysis.md",
        "Ads/Ad-Script.md",
        "Influencers/Influencer-Database.md",
        "Outreach/Cold-Outreach-Drafts.md",
    ]:
        p = VAULT / rel
        if p.exists():
            notes.append(f"--- {rel} ---\n{p.read_text(encoding='utf-8')[:3000]}")

    reporter = make_agent(
        "You are the Standup Reporter agent — a chief-of-staff for the "
        "marketing agent team. You write crisp daily standup notes in "
        "Markdown with Obsidian [[wikilinks]]."
    )
    today = date.today().isoformat()
    standup = reporter.chat(
        f"Today is {today}. Here are excerpts of everything the marketing "
        f"agent team produced today:\n\n" + "\n\n".join(notes)[:20000] + "\n\n"
        "Write '# Daily Marketing Standup — " + today + "'. Sections: "
        "'Done today' (what each agent delivered, with [[wikilinks]] to the "
        "notes), 'Key insights' (3 bullets), 'Blockers/risks', and "
        "'Tomorrow's priorities' (a checklist). Keep it under 350 words."
    )
    write_note(f"Standups/{today}-Standup.md", standup)


# ---------------------------------------------------------------------------
def main() -> None:
    print(f"Model: {MODEL}\nVault: {VAULT}\n")
    if not os.getenv("OPENROUTER_API_KEY"):
        sys.exit("ERROR: OPENROUTER_API_KEY missing. Copy .env.example to .env and fill it.")
    VAULT.mkdir(parents=True, exist_ok=True)

    run_marketing_manager()
    run_ads_manager()
    run_influencer_scout()
    run_standup_reporter()

    print("\nAll agents finished. Open the vault folder in Obsidian to see the results.")


if __name__ == "__main__":
    main()

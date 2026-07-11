# CrowdWisdomTrading — Hermes Marketing Agent Team

A backend Python project built on the **Hermes Agent framework** (Nous Research) + **Obsidian**, for the CrowdWisdomTrading Marketing Agent internship assessment.

A team of four AI agents runs the marketing department for [crowdwisdomtrading.com](https://crowdwisdomtrading.com): strategy, competitor research, winning-ad mining (Apify → Meta Ads Library), ad-script writing, influencer scouting, cold outreach — all coordinated on a **Hermes kanban board**, chatting with the human over **Telegram**, and writing every result as linked **Markdown notes into an Obsidian vault**.

## Architecture

```
                 ┌────────────────────────────┐
 Telegram  ◄────►│  Hermes Gateway            │◄──── cron (daily standup)
 (you, on phone) │  (hosts kanban dispatcher) │
                 └──────────┬─────────────────┘
                            │ spawns workers per kanban task
     ┌──────────────┬───────┴────────┬────────────────┐
     ▼              ▼                ▼                ▼
 marketing-     ads-analyst     outreach-scout   standup-reporter
 manager        (Apify scrape → (web/browser      (our idea: daily
 (strategy +    pains → ad      influencer hunt   report → Obsidian
 competitors)   script)         + outreach)       + Telegram)
     │              │                │                │
     └──────────────┴───────┬────────┴────────────────┘
                            ▼
              Obsidian vault (Markdown notes)   +   output/ads_results.json
```

## Stack (as required)
- **Language:** Python
- **Framework:** Hermes Agent + Obsidian (vault = the agents' output layer, via `OBSIDIAN_VAULT_PATH`)
- **LLM provider:** OpenRouter
- **Scraping:** Apify (Meta Ads Library actor)
- **Evaluation criteria covered:** Hermes **kanban** (dependency-chained tasks + dashboard), **loops** (goal-mode kanban workers + a reviewer quality-loop in `run_local_pipeline.py`) and **skills** (4 custom `SKILL.md`), **Telegram** gateway to chat with the agents.

## The agents
1. **marketing-manager** — marketing strategy + competitor research → `Strategy/`, `Competitors/`
2. **ads-analyst** — scrapes best-performing Meta ads of the last 30 days via Apify → `output/ads_results.json`; extracts pains/concepts → `Ads/Ad-Analysis.md`; writes a new ad script from those pains + our unique crowd-data mechanism → `Ads/Ad-Script.md`
3. **outreach-scout** — finds retail-trading influencers >200K on YT/X/IG/TT via web search & browser → `Influencers/`; drafts personalized opinion-ask cold outreach → `Outreach/`
4. **standup-reporter** *(our idea — self-defined scope)* — a chief-of-staff agent on a daily cron: reads the kanban + vault, writes `Standups/<date>-Standup.md`, and messages the summary to the founder on Telegram. One agent that exercises cron + kanban + Obsidian + Telegram together.

## Quick start
Full baby-steps instructions live in **[GUIDE.md](GUIDE.md)**. Short version:

```bash
cp .env.example .env        # fill in OPENROUTER_API_KEY, APIFY_TOKEN, OBSIDIAN_VAULT_PATH
pip install -r requirements.txt

# Mode A — simple pipeline (guaranteed md output, with quality-review loops):
python scripts/run_local_pipeline.py

# Mode B — full Hermes: kanban + Telegram + dashboard:
bash setup.sh               # installs skills + profiles, inits kanban
hermes gateway start        # terminal 1 (Telegram + kanban dispatcher)
bash run_pipeline.sh        # terminal 2 (creates the task chain)
hermes dashboard            # watch the board live (video deliverable)
```

## Deliverables map
- **Apify token used:** provided in the submission email (rotate after review).
- **JSON output:** `output/ads_results.json`
- **md output of the agents:** the `vault/` folder (open it in Obsidian)
- **Kanban video:** screen recording of `hermes dashboard` while `run_pipeline.sh` executes

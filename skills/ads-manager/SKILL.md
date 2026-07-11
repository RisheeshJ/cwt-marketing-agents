---
name: ads-manager
description: Scrape winning Meta ads for the retail-trading niche via Apify, extract pains and concepts, and write a new ad script for crowdwisdomtrading.com. Saves ads_results.json and Markdown notes to the Obsidian vault.
version: 1.0.0
tags: [ads, apify, copywriting]
---

# Ads Manager Skill

## When triggered
Use for any task about finding winning ads, analyzing ad concepts, or writing
ad scripts for crowdwisdomtrading.com.

## Procedure
1. Run the scraper in the project repo:
   `python scripts/scrape_meta_ads.py`
   It uses APIFY_TOKEN + APIFY_ACTOR_ID from .env, pulls active Meta Ads
   Library ads from the last 30 days for our niche terms, ranks them, and
   saves `output/ads_results.json` (required deliverable — never skip it).
2. Read `output/ads_results.json` and extract:
   - top 5 pain points the ads target
   - hooks / opening lines
   - recurring concepts (urgency, social proof, authority, curiosity)
   - offer structures
3. Write `Ads/Ad-Analysis.md` in the Obsidian vault (path from
   OBSIDIAN_VAULT_PATH) with the analysis and a Pain -> Angle -> Example table.
4. Write `Ads/Ad-Script.md`: a 30-45s direct-response video ad script for
   crowdwisdomtrading.com built on the identified pains plus OUR unique
   mechanism (real crowd positioning data). Structure: HOOK (0-3s), PROBLEM,
   MECHANISM, PROOF, CTA — with spoken lines, on-screen text, and visual
   directions, plus 3 alternative hooks and 2 headline variants.
5. As a kanban worker, kanban_complete with the file paths produced.

## Quality bar
The hook must create a curiosity gap or call out the target in 3 seconds.
Never promise guaranteed returns (compliance).

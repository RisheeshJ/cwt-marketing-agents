#!/usr/bin/env bash
# ============================================================
# run_pipeline.sh — loads the marketing pipeline onto the
# Hermes kanban board as a dependency chain of tasks.
#
# REQUIREMENT: the gateway must be running in another terminal
#   hermes gateway start
# because the gateway hosts the dispatcher that actually spawns
# the worker agents for each task.
#
# Watch it live:   hermes dashboard        (visual board — record this!)
#             or:  hermes kanban list
# Usage:  bash run_pipeline.sh
# ============================================================
set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
command -v jq >/dev/null || { echo "Please install jq first: sudo apt install jq"; exit 1; }

echo "==> Creating kanban tasks (a dependency chain) ..."

STRATEGY=$(hermes kanban create "Marketing strategy + competitor research for crowdwisdomtrading.com" \
  --assignee marketing-manager \
  --body "Use the marketing-manager skill. Deliver Strategy/Marketing-Strategy.md and Competitors/Competitor-Research.md in the Obsidian vault (OBSIDIAN_VAULT_PATH). Acceptance: both notes exist, contain real competitors, personas with pains, 30-day checklist." \
  --workspace "dir:$REPO_DIR" --goal --json | jq -r .id)
echo "    strategy task: $STRATEGY"

ADS=$(hermes kanban create "Find winning Meta ads, extract pains, write our ad script" \
  --assignee ads-analyst \
  --parent "$STRATEGY" \
  --body "Use the ads-manager skill. Run scripts/scrape_meta_ads.py (Apify), save output/ads_results.json, then write Ads/Ad-Analysis.md and Ads/Ad-Script.md in the vault. Acceptance: ads_results.json exists; script has HOOK/PROBLEM/MECHANISM/PROOF/CTA + 3 alt hooks." \
  --workspace "dir:$REPO_DIR" --goal --json | jq -r .id)
echo "    ads task: $ADS"

OUTREACH=$(hermes kanban create "Find retail-trading influencers >200K and draft cold outreach" \
  --assignee outreach-scout \
  --parent "$STRATEGY" \
  --body "Use the influencer-outreach skill. Deliver Influencers/Influencer-Database.md (8-12 real influencers, all data you can find) and Outreach/Cold-Outreach-Drafts.md (personalized opinion-ask messages). Acceptance: every influencer >200K followers, every draft references specific content of theirs." \
  --workspace "dir:$REPO_DIR" --goal --json | jq -r .id)
echo "    outreach task: $OUTREACH"

STANDUP=$(hermes kanban create "Daily marketing standup: summarize vault + kanban, post to Telegram" \
  --assignee standup-reporter \
  --parent "$ADS" \
  --body "Use the daily-standup skill. Write Standups/<today>-Standup.md in the Obsidian vault and send the summary to Telegram with 'hermes send --to telegram'." \
  --workspace "dir:$REPO_DIR" --json | jq -r .id)
echo "    standup task: $STANDUP"

# The standup should also wait for the outreach task; add a second parent link.
# (If your Hermes version doesn't support multiple parents, this just no-ops.)
hermes kanban link "$OUTREACH" "$STANDUP" 2>/dev/null || true

echo ""
echo "Tasks created. The gateway dispatcher will pick them up in order."
echo "Watch live:  hermes dashboard    (record your screen here for the video deliverable)"

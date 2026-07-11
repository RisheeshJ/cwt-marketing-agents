---
name: daily-standup
description: Our own idea — a chief-of-staff agent that reviews the kanban board and the vault, writes a daily marketing standup note in Obsidian, and sends a summary to the founder on Telegram. Designed to run on a cron schedule.
version: 1.0.0
tags: [reporting, cron, telegram, kanban]
---

# Daily Marketing Standup Skill (custom scope — "Your idea")

## Purpose
Every day, summarize what the marketing agent team accomplished, what is
blocked, and what is next — so a human can run the whole marketing org from
Telegram.

## Procedure
1. Inspect the kanban board (kanban_list / kanban_show as a worker, or
   `hermes kanban list` from the CLI context) — collect done / running /
   blocked tasks.
2. Read today's new/changed notes in the Obsidian vault (OBSIDIAN_VAULT_PATH):
   Strategy/, Competitors/, Ads/, Influencers/, Outreach/.
3. Write `Standups/<YYYY-MM-DD>-Standup.md` in the vault with sections:
   Done today (with [[wikilinks]]), Key insights (3 bullets),
   Blockers/risks, Tomorrow's priorities (checklist). Under 350 words.
4. Send the standup summary to Telegram (the gateway is configured):
   `hermes send --to telegram "<summary text>"`.

## Scheduling
Ask Hermes to create a cron job: "every day at 09:00 run the daily-standup
skill and deliver the result to Telegram."

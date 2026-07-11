# THE COMPLETE BABY-STEPS GUIDE
### From "I have nothing installed" to "I submitted the assignment"

Read this top to bottom. Every step says **what to do**, **exactly where**, and **why we do it**. Do not skip steps.

---

## Part 0 — What are we actually building? (read this once)

You are building a small **company of AI employees** ("agents") that do marketing for crowdwisdomtrading.com:

| Agent (profile name) | Job | Where its work appears |
|---|---|---|
| `marketing-manager` | writes the marketing strategy, researches competitors | Obsidian notes |
| `ads-analyst` | finds Facebook/Instagram ads that are working RIGHT NOW (via Apify), figures out why, writes a new ad script | `output/ads_results.json` + Obsidian notes |
| `outreach-scout` | finds trading influencers with >200K followers, drafts personal messages to them | Obsidian notes |
| `standup-reporter` | **(our own idea)** every day: summarizes what the team did, writes a standup note, and Telegrams you the summary | Obsidian note + Telegram message |

The glue holding them together:
- **Hermes Agent** = the framework that runs the agents (their "office building").
- **Kanban board** = their shared to-do list. You put tasks on it; Hermes automatically assigns each task to the right agent and runs it. You can WATCH this happen in a browser dashboard — that's the video you must record.
- **Obsidian** = a free notes app. Our agents write all their results as `.md` (Markdown) notes into one folder ("vault") that you open in Obsidian. That's the "md output" deliverable.
- **Telegram** = you connect a Telegram bot so you can literally text your agents from your phone.
- **OpenRouter** = the service that provides the AI brain (you pay a few cents per run).
- **Apify** = the service that scrapes the public Meta Ads Library for us.

There are **two run modes** in this project, and you will use BOTH:
- **Mode A (`run_local_pipeline.py`)** — a plain Python script that runs all 4 agents one after another with a *quality-review loop* (a reviewer agent grades each output and forces a rewrite if it's weak). Simple, reliable, guarantees your md outputs exist. Great to run first.
- **Mode B (kanban + Telegram)** — the full Hermes experience: tasks on the kanban board, gateway dispatching worker agents, dashboard you record on video, Telegram chat. This is what the evaluation criteria are about.

---

## Part 1 — Create the accounts (30 min, all free to start)

### 1.1 OpenRouter (the AI brain) — REQUIRED
1. Open a browser → go to **https://openrouter.ai** → click **Sign in** (top right) → sign in with Google/GitHub.
2. Click your avatar (top right) → **Keys** → **Create Key** → name it `cwt-assignment` → **Create** → **copy the key** (starts with `sk-or-v1-...`) into a text file for now.
3. Click avatar → **Credits** → add **$5** (card/PayPal). *Why: every agent message costs a fraction of a cent; $5 comfortably covers this whole project many times over.*

### 1.2 Apify (the ad scraper) — REQUIRED
1. Go to **https://apify.com** → **Sign up free** (free plan includes monthly credits — enough for this).
2. After login you land in the **Apify Console** → left sidebar → **Settings** → **API & Integrations** → copy your **Personal API token** (starts with `apify_api_...`).
3. Left sidebar → **Store** → search **"facebook ads library scraper"** → open a well-rated actor (e.g. *Facebook Ads Library Scraper*). On its page, note the actor ID shown as `username/actor-name` near the title (e.g. `curious_coder/facebook-ads-library-scraper`). Copy it. *Why: an "actor" is a ready-made scraper; our script tells Apify "run this actor with these search terms".*
4. Still on the actor page, click the **Input** tab and glance at the input field names (e.g. `searchTerms`, `countryCode`). If they differ from what's in `scripts/scrape_meta_ads.py`, you'll adjust that file later (the script has a comment marking exactly where).

### 1.3 Telegram bot — REQUIRED for the Telegram criterion
1. On your phone or Telegram Desktop, search for **@BotFather** (the official one, blue checkmark) → press **Start**.
2. Send the message: `/newbot` → it asks for a display name → type e.g. `CWT Marketing Agents` → it asks for a username → type something ending in `bot`, e.g. `cwt_marketing_yourname_bot`.
3. BotFather replies with a **token** like `123456789:AAF...`. Copy it. *Why: this token lets Hermes receive/send messages as that bot — that's how you'll chat with your agents.*

### 1.4 Obsidian (the notes app) — REQUIRED
1. Go to **https://obsidian.md** → **Download** → install like any normal app (free).
2. Don't create a vault yet — we'll open our project's `vault/` folder as the vault in Part 3.

### 1.5 GitHub — REQUIRED for submission
1. Go to **https://github.com** → sign up if needed → click **+** (top right) → **New repository** → name: `cwt-marketing-agents` → **Private for now** (make it public or invite the reviewer when you submit) → **Create**.

---

## Part 2 — Prepare your computer (Linux/macOS; on Windows use WSL)

> **Windows users:** Hermes needs Linux. Press Start → type `PowerShell` → right-click → *Run as administrator* → run `wsl --install` → restart → open the new **Ubuntu** app → create a username/password. Do EVERYTHING below inside that Ubuntu terminal.

### 2.1 Install Hermes Agent (one command)
Open a terminal and paste:
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```
*What this does: downloads Hermes, installs Python 3.11 and everything it needs into `~/.hermes/`. No admin rights needed.* When it finishes, **close and reopen the terminal** (so the `hermes` command is found).

### 2.2 Run the setup wizard
```bash
hermes setup
```
The wizard asks questions. Answer:
- **Provider:** choose **OpenRouter** → paste your `sk-or-v1-...` key.
- **Model:** pick a strong one, e.g. `anthropic/claude-sonnet-4.6` (you can change anytime with `hermes model`).
- Accept defaults for the rest (press Enter). We'll configure Telegram separately in Part 5.

### 2.3 Smoke test (make sure the brain works)
```bash
hermes
```
An interactive chat opens. Type `hello, who are you?` — if it answers, everything works. Type `/exit` (or Ctrl+C) to leave.

---

## Part 3 — Set up THIS project

### 3.1 Get the project onto your machine and into GitHub
You received the project as a folder `cwt-marketing-agents/`. In the terminal:
```bash
cd ~
# put the folder here (unzip it into your home directory), then:
cd cwt-marketing-agents
git init
git add .
git commit -m "CWT marketing agent team — initial"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/cwt-marketing-agents.git
git push -u origin main
```
*Why now: the repo link is a deliverable; committing early also protects your work.*

### 3.2 Create your secrets file
```bash
cp .env.example .env
nano .env
```
(`nano` is a tiny text editor: edit, then press **Ctrl+O**, **Enter** to save, **Ctrl+X** to quit.)
Fill in:
- `OPENROUTER_API_KEY` = your `sk-or-v1-...` key
- `APIFY_TOKEN` = your `apify_api_...` token
- `APIFY_ACTOR_ID` = the actor id you copied (e.g. `curious_coder/facebook-ads-library-scraper`)
- `OBSIDIAN_VAULT_PATH` = the FULL path to the vault folder. Find it with:
  ```bash
  cd vault && pwd && cd ..
  ```
  Copy what `pwd` printed (e.g. `/home/you/cwt-marketing-agents/vault`).
- `TELEGRAM_BOT_TOKEN` = your BotFather token.

*Why a .env file: keys must never be hard-coded or committed to git (the included `.gitignore` already excludes `.env`).*

Also export the vault path for Hermes itself (its Obsidian skill reads this variable):
```bash
echo "OBSIDIAN_VAULT_PATH=$(cd vault && pwd)" >> ~/.hermes/.env
```

### 3.3 Install the Python dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*What this does: creates an isolated Python environment (`.venv`) and installs the Hermes library, the Apify client, and dotenv into it. Whenever you open a NEW terminal for this project, run `source .venv/bin/activate` again first.*

### 3.4 Open the vault in Obsidian
1. Open the Obsidian app → **Open folder as vault** → navigate to `cwt-marketing-agents/vault` → open.
2. You'll see `00-Dashboard.md`. Keep Obsidian open — you'll literally watch notes appear as agents work.
   *(Windows/WSL tip: your Ubuntu files are reachable in Windows Explorer at `\\wsl$\Ubuntu\home\YOURNAME\cwt-marketing-agents\vault`.)*

---

## Part 4 — First real run (Mode A: the simple pipeline)

```bash
source .venv/bin/activate     # if not already active
python scripts/run_local_pipeline.py
```
**What happens, step by step (watch the terminal):**
1. Agent 1 (Marketing Manager) writes the strategy → a reviewer agent scores it → if <7/10 it rewrites (that's the loop) → `vault/Strategy/Marketing-Strategy.md` and `vault/Competitors/Competitor-Research.md` appear in Obsidian.
2. Agent 2 (Ads Manager) calls Apify → you'll see `[apify] Scraping Meta Ads Library for: 'stock trading'...` → saves `output/ads_results.json` → analyzes pains → writes `vault/Ads/Ad-Analysis.md` and `vault/Ads/Ad-Script.md`.
3. Agent 3 (Influencer Scout) researches influencers → writes `vault/Influencers/Influencer-Database.md` and `vault/Outreach/Cold-Outreach-Drafts.md`.
4. Agent 4 (Standup Reporter) summarizes everything → `vault/Standups/<today>-Standup.md`.

The run takes several minutes. When it ends, click through the notes in Obsidian — the [[wikilinks]] connect them into a graph (press Ctrl+G in Obsidian to see the graph view; it looks great in your submission video too).

**If the Apify step errors:** open the actor's page in the Apify Console → **Input** tab → compare field names to `run_input` inside `scripts/scrape_meta_ads.py` → rename fields to match → run again. The rest of the pipeline still works even if ads come back empty.

Commit the outputs:
```bash
git add . && git commit -m "first pipeline run outputs" && git push
```

---

## Part 5 — Full Hermes mode: Telegram + Kanban (the evaluation criteria)

### 5.1 Register skills, profiles, and the board
```bash
bash setup.sh
```
*What this does: copies our 4 `SKILL.md` files into `~/.hermes/skills/` (so any Hermes agent can invoke them), creates the 4 agent profiles (`hermes profile create ...`) with their SOUL.md personalities, and runs `hermes kanban init` to create the board.*

### 5.2 Connect Telegram
```bash
hermes gateway setup
```
Choose **Telegram** → paste your BotFather token → follow the prompts. *Why: the gateway is the switchboard between messaging apps and your agents.*

### 5.3 Start the gateway and keep it running
Open a terminal (call it **Terminal 1**) and run:
```bash
hermes gateway start
```
Leave it running. *Why this matters twice over: (1) it connects Telegram; (2) the gateway hosts the kanban DISPATCHER — the thing that picks up ready tasks from the board and spawns the right agent profile to do them. No gateway = tasks sit on the board forever.*

Now on your phone: open Telegram → find your bot → press **Start** → send `hello`. Hermes should answer. **Screen-record a short chat with it** — ask it something like *"list your skills"* or *"what marketing tasks are on the kanban?"* — this demonstrates the Telegram criterion.

### 5.4 Launch the pipeline on the kanban
Open **Terminal 2**:
```bash
cd ~/cwt-marketing-agents && source .venv/bin/activate
bash run_pipeline.sh
```
*What this does: creates 4 kanban tasks as a dependency chain — strategy first; when it completes, the ads task and the outreach task unlock (parent→child promotion); the standup task runs last. The ads/outreach/strategy tasks use `--goal` mode: after each turn a judge agent checks the work against the acceptance criteria in the card body and loops the worker until it passes — that is Hermes's built-in loop engine, your second "loops" criterion.*

### 5.5 Watch and RECORD the board (video deliverable)
Open **Terminal 3**:
```bash
hermes dashboard
```
A browser window opens with the visual kanban board: cards moving `ready → running → done`, worker logs, run history. **Start a screen recording now** (Windows: Win+G game bar; macOS: Cmd+Shift+5; Linux: OBS) and capture: the board with moving cards → click a card to show its run history → the Obsidian vault with the new notes → your Telegram chat with the bot. 2–4 minutes is plenty.

You can also watch from the terminal: `hermes kanban list` or `hermes kanban tail`.

### 5.6 Schedule the daily standup (our idea, part 2)
In your Telegram chat with the bot (or `hermes` CLI), send:
> Create a cron job: every day at 09:00, run the daily-standup skill — review the kanban board and today's Obsidian vault notes, write the standup note in Standups/, and send me the summary here on Telegram.

Hermes's built-in cron scheduler registers it. *Why this is a strong "your idea": one agent that exercises cron + kanban + Obsidian + Telegram simultaneously — exactly the features being graded.*

---

## Part 6 — Submit

**Checklist of deliverables:**
1. **GitHub repo link** — make the repo public (repo → Settings → General → Danger Zone → Change visibility) or add the reviewer as a collaborator. Final push:
   ```bash
   git add . && git commit -m "final: outputs + docs" && git push
   ```
2. **Apify token** — paste the token in the email (they need it to rerun your code). *After they finish reviewing, rotate it in the Apify Console → Settings → API tokens.*
3. **Kanban video** — the recording from step 5.5. Upload to Google Drive/YouTube-unlisted and share the link.
4. **md output of the agents** — already in the repo under `vault/` (mention this in the email; optionally attach the folder as a zip).

**Email template** (to gilad@crowdwisdomtrading.com):
> Subject: Marketing Agent Intern Assessment — [Your Name]
>
> Hi Gilad,
>
> Here is my submission for the marketing agent assessment:
> - Repo: https://github.com/YOU/cwt-marketing-agents (README explains architecture; GUIDE.md documents the full run)
> - Kanban video: [link]
> - Agent md outputs: in the repo under /vault (an Obsidian vault written by the agents), plus output/ads_results.json from Apify
> - Apify token (for rerunning): apify_api_XXXX
>
> Stack: Hermes Agent + Obsidian, OpenRouter, Apify. Evaluation criteria: kanban (dependency-chained tasks + dashboard, shown in the video), loops (goal-mode kanban workers + a reviewer quality-loop in run_local_pipeline.py), skills (4 custom SKILL.md), and Telegram (gateway chat, shown in the video). My own agent ("Your idea") is a cron-scheduled Daily Standup chief-of-staff that reports the team's progress to Telegram every morning.
>
> Thanks for the opportunity!
> [Your Name]

---

## Part 7 — Troubleshooting (the classics)

| Problem | Fix |
|---|---|
| `hermes: command not found` | Close and reopen the terminal; or run `source ~/.bashrc`. |
| Agent replies with auth error | Wrong/missing OpenRouter key → `hermes setup` again; also check credits on openrouter.ai. |
| Apify script fails | Actor input field names differ → fix `run_input` in `scripts/scrape_meta_ads.py` (see the comment there); check token; check free credits in Apify Console. |
| Kanban tasks never start | The gateway isn't running. Start `hermes gateway start` and keep it open. |
| Telegram bot silent | Re-run `hermes gateway setup`; make sure you pressed **Start** on the bot; gateway must be running. |
| Notes not appearing in Obsidian | Check `OBSIDIAN_VAULT_PATH` in both `.env` and `~/.hermes/.env` is the FULL absolute path to `vault/`. |
| `pip install` of hermes-agent fails | Make sure git is installed (`sudo apt install git`) and Python ≥3.11 (`python3 --version`). |
| Everything is on fire | `hermes doctor` diagnoses common setup problems. |

**Safety note:** you're giving an autonomous agent a terminal. Run this on a machine/VM you're comfortable with, use fresh API keys created just for this assignment, and rotate the Apify token after review.

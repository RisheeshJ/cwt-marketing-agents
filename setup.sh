#!/usr/bin/env bash
# ============================================================
# setup.sh — one-time setup: registers our skills + agent
# profiles inside your Hermes installation and creates the
# kanban board. Run AFTER installing Hermes (see GUIDE.md).
# Usage:  bash setup.sh
# ============================================================
set -e
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> 1/4 Copying skills into $HERMES_HOME/skills ..."
mkdir -p "$HERMES_HOME/skills"
cp -r "$REPO_DIR/skills/"* "$HERMES_HOME/skills/"

echo "==> 2/4 Creating agent profiles (one per marketing role) ..."
for prof in marketing-manager ads-analyst outreach-scout standup-reporter; do
  hermes profile create "$prof" 2>/dev/null || echo "    profile '$prof' already exists — ok"
done

echo "==> 3/4 Installing SOUL.md (personality) for each profile ..."
for prof in marketing-manager ads-analyst outreach-scout standup-reporter; do
  # Default profile dir; if your Hermes version stores profiles elsewhere,
  # run `hermes profile list` to find it and copy the SOUL.md manually.
  PROF_DIR="$HERMES_HOME/profiles/$prof"
  mkdir -p "$PROF_DIR"
  cp "$REPO_DIR/profiles/$prof/SOUL.md" "$PROF_DIR/SOUL.md"
done

echo "==> 4/4 Initializing the kanban board ..."
hermes kanban init 2>/dev/null || echo "    kanban already initialized — ok"

echo ""
echo "Setup complete. Next: bash run_pipeline.sh   (see GUIDE.md, Part 5)"

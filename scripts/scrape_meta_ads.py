"""
scrape_meta_ads.py
------------------
STEP 1 of the Ads Manager pipeline.

What it does (in plain words):
  1. Connects to Apify (a cloud scraping service) with your APIFY_TOKEN.
  2. Runs a ready-made "actor" (scraper) against the public Meta Ads Library
     for our niche search terms (e.g. "stock trading", "options trading").
  3. Filters to ads that started running in the LAST 30 DAYS and are still
     active — i.e. ads that are working well enough that people keep paying
     for them.
  4. Ranks them by longevity + number of ad variants (a strong proxy for a
     winning ad: advertisers only keep spending on what converts).
  5. Saves everything to  output/ads_results.json  — this file is a required
     deliverable of the assignment.

Run it alone:      python scripts/scrape_meta_ads.py
Or it is called automatically by scripts/run_local_pipeline.py
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apify_client import ApifyClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

OUTPUT_FILE = ROOT / "output" / "ads_results.json"


def scrape_ads() -> list[dict]:
    token = os.getenv("APIFY_TOKEN")
    if not token:
        sys.exit("ERROR: APIFY_TOKEN is missing. Copy .env.example to .env and fill it in.")

    actor_id = os.getenv("APIFY_ACTOR_ID", "curious_coder/facebook-ads-library-scraper")
    search_terms = [t.strip() for t in os.getenv(
        "ADS_SEARCH_TERMS", "stock trading,options trading,trading signals"
    ).split(",")]
    country = os.getenv("ADS_COUNTRY", "US")
    max_results = int(os.getenv("ADS_MAX_RESULTS", "40"))

    client = ApifyClient(token)
    all_items: list[dict] = []

    for term in search_terms:
        print(f"[apify] Scraping Meta Ads Library for: '{term}' ...")
        # NOTE: input field names vary slightly between actors in the Apify
        # store. The fields below cover the common Facebook Ads Library
        # scrapers. If your chosen actor uses different input names, open the
        # actor's page in the Apify console -> "Input" tab and adjust here.
        run_input = {
            "searchTerms": [term],
            "adActiveStatus": "active",
            "adType": "all",
            "countryCode": country,
            "count": max_results,
            "scrapeAdDetails": True,
        }
        try:
            run = client.actor(actor_id).call(run_input=run_input)
        except Exception as e:  # noqa: BLE001
            print(f"[apify] Actor call failed for '{term}': {e}")
            continue

        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            item["_search_term"] = term
            all_items.append(item)

    print(f"[apify] Total raw ads collected: {len(all_items)}")
    return all_items


def filter_last_30_days(items: list[dict]) -> list[dict]:
    """Keep ads whose start date is within the last 30 days (field names vary
    per actor, so we try several common ones)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    kept = []
    for ad in items:
        raw = (
            ad.get("startDate")
            or ad.get("start_date")
            or ad.get("adDeliveryStartTime")
            or ad.get("ad_delivery_start_time")
        )
        if raw is None:
            kept.append(ad)  # keep unknowns rather than lose data
            continue
        try:
            if isinstance(raw, (int, float)):
                start = datetime.fromtimestamp(raw, tz=timezone.utc)
            else:
                start = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
            if start >= cutoff:
                kept.append(ad)
        except (ValueError, OSError):
            kept.append(ad)
    print(f"[filter] Ads from the last 30 days: {len(kept)}")
    return kept


def rank_ads(items: list[dict]) -> list[dict]:
    """Simple 'winning ad' heuristic: more collation (variant) count and
    longer active runtime = advertiser keeps paying = it converts."""
    def score(ad: dict) -> float:
        variants = ad.get("collationCount") or ad.get("collation_count") or 1
        try:
            variants = float(variants)
        except (TypeError, ValueError):
            variants = 1.0
        return variants

    ranked = sorted(items, key=score, reverse=True)
    for i, ad in enumerate(ranked, 1):
        ad["_rank"] = i
    return ranked


def main() -> list[dict]:
    ads = scrape_ads()
    ads = filter_last_30_days(ads)
    ads = rank_ads(ads)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "niche": "retail trading",
                "product": "crowdwisdomtrading.com",
                "total_ads": len(ads),
                "ads": ads,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"[done] Saved {len(ads)} ads -> {OUTPUT_FILE}")
    return ads


if __name__ == "__main__":
    main()

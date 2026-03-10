#!/usr/bin/env python3
"""
Market Intelligence Agent — Main Orchestrator
Run manually or via scheduled task every Wednesday.

Usage:
  python3 run.py                  # full scrape + dashboard
  python3 run.py --baseline-only  # dashboard from saved baseline data
"""

import json
import re
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Allow running from any directory
ROOT = Path(__file__).parent.parent
AGENT_DIR = Path(__file__).parent
DATA_DIR  = ROOT / "data"
OUT_DIR   = ROOT / "Claude Outputs"
DATA_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(AGENT_DIR))

from config import OPERATORS
from scraper import OperatorScraper
from extractor import extract_subscriptions, extract_internet, extract_hardware, extract_vas
from dashboard import generate_dashboard, OPERATOR_COLORS
from baseline_data import BASELINE
from news_scraper import fetch_all_news
from roaming_scraper import fetch_roaming_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True,   # override any handlers set by imported modules
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ROOT / "agent.log", mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def scrape_operator(scraper: OperatorScraper, op_key: str, op_cfg: dict) -> dict:
    """Scrape all data sections for one operator. Returns structured dict."""
    name = op_cfg["name"]
    log.info(f"━━ Scraping {name} ━━")

    result = {"subscriptions": [], "internet": [], "hardware": [], "vas": []}

    # Subscriptions
    url = op_cfg["urls"].get("subscriptions")
    text = scraper.fetch(url) if url else None
    if text:
        result["subscriptions"] = extract_subscriptions(text, name)
        result["vas"]           = extract_vas(text, name)
        log.info(f"  {name}: {len(result['subscriptions'])} abonnementer, {len(result['vas'])} VAS")
    else:
        log.warning(f"  {name}: scraping af abonnementer mislykkedes")

    # Internet
    url = op_cfg["urls"].get("internet")
    text = scraper.fetch(url) if url else None
    if text:
        result["internet"] = extract_internet(text, name)
        log.info(f"  {name}: {len(result['internet'])} internetprodukter")
    else:
        log.warning(f"  {name}: scraping af internet mislykkedes")

    # Hardware — extra wait + exhaust all load-more buttons/infinite scroll
    url = op_cfg["urls"].get("hardware")
    text = scraper.fetch(url, wait_seconds=7, load_more=True) if url else None
    if text:
        result["hardware"] = extract_hardware(text, name)
        log.info(f"  {name}: {len(result['hardware'])} devices")

    return result


def merge_with_baseline(live: dict, baseline_ops: dict) -> dict:
    """
    Merge live scraped data with baseline.
    If live scraping returned no results for a section, use baseline as fallback.
    """
    merged = {}
    for op_key, op_cfg in OPERATORS.items():
        name = op_cfg["name"]
        live_data     = live.get(op_key, {})
        baseline_data = baseline_ops.get(op_key, {})

        merged[op_key] = {
            "name":  name,
            "own_brand": op_cfg.get("own_brand", False),
            "color": op_cfg.get("color", "#888"),
        }

        for section in ("subscriptions", "internet", "hardware", "vas"):
            live_section = live_data.get(section, [])
            base_section = baseline_data.get(section, [])

            if live_section:
                merged[op_key][section] = live_section
                log.info(f"  {name} / {section}: live data ({len(live_section)} rækker)")
            elif base_section:
                merged[op_key][section] = base_section
                log.info(f"  {name} / {section}: bruger baseline ({len(base_section)} rækker)")
            else:
                merged[op_key][section] = []

    return merged


def annotate_changes(current_ops: dict, previous_ops: dict) -> dict:
    """
    Compare current prices with the previous snapshot.
    Adds `price_change` (delta kr.) and `price_new` (bool) to each item.
    Matching key: (operator, plan_name).
    """
    # Build previous price lookup: {(operator, name): price}
    prev_lookup: dict[tuple, float] = {}
    for op_data in previous_ops.values():
        for section in ("subscriptions", "internet", "hardware"):
            for item in op_data.get(section, []):
                key = (item.get("operator", "").lower(), item.get("name", "").lower().strip())
                p = item.get("price") or item.get("price_min")
                if p is not None:
                    prev_lookup[key] = float(p)

    # Annotate current items
    for op_data in current_ops.values():
        for section in ("subscriptions", "internet", "hardware"):
            for item in op_data.get(section, []):
                key = (item.get("operator", "").lower(), item.get("name", "").lower().strip())
                curr_price = item.get("price") or item.get("price_min")
                if curr_price is None:
                    continue
                curr_price = float(curr_price)
                if key in prev_lookup:
                    delta = round(curr_price - prev_lookup[key], 2)
                    item["price_change"] = delta if delta != 0 else None
                    item["price_new"] = False
                else:
                    item["price_change"] = None
                    item["price_new"] = True  # new plan this week

    return current_ops


def save_snapshot(data: dict) -> Path:
    """Save structured data as dated JSON snapshot."""
    ts   = datetime.now().strftime("%Y-%m-%d")
    path = DATA_DIR / f"snapshot-{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"Snapshot gemt: {path}")
    return path


def load_latest_snapshot() -> dict | None:
    """Load the most recent saved snapshot (for baseline comparison)."""
    snapshots = sorted(DATA_DIR.glob("snapshot-*.json"))
    if not snapshots:
        return None
    with open(snapshots[-1], encoding="utf-8") as f:
        return json.load(f)


def build_trend_data() -> dict:
    """
    Read all saved snapshots and build weekly price time series per operator.
    Returns minimum price and minimum campaign price per operator per date.
    """
    snapshots = sorted(DATA_DIR.glob("snapshot-*.json"))
    result = {
        "subscriptions": {"dates": [], "operators": {}},
        "internet":      {"dates": [], "operators": {}},
    }

    for snap_path in snapshots:
        try:
            with open(snap_path, encoding="utf-8") as f:
                snap = json.load(f)
        except Exception as e:
            log.warning(f"Kan ikke læse snapshot {snap_path}: {e}")
            continue

        date_str = snap.get("scraped_at", "")[:10]

        for section in ("subscriptions", "internet"):
            result[section]["dates"].append(date_str)

            for op_data in snap.get("operators", {}).values():
                name  = op_data.get("name", "")
                color = OPERATOR_COLORS.get(name, op_data.get("color", "#888"))
                items = op_data.get(section, [])

                prices = [i["price"] for i in items if isinstance(i.get("price"), (int, float))]
                camps  = [i["campaign_price"] for i in items if isinstance(i.get("campaign_price"), (int, float))]

                if name not in result[section]["operators"]:
                    result[section]["operators"][name] = {
                        "prices": [], "campaign_prices": [], "color": color,
                        "min_prices": [], "intro_months": [],
                    }

                result[section]["operators"][name]["prices"].append(min(prices) if prices else None)
                result[section]["operators"][name]["campaign_prices"].append(min(camps) if camps else None)

                # Internet-only: min_price (scraped Mindstepris) and intro_months
                if section == "internet":
                    mp = [i["min_price"] for i in items if isinstance(i.get("min_price"), (int, float))]
                    result[section]["operators"][name]["min_prices"].append(min(mp) if mp else None)
                    months = []
                    for i in items:
                        m = re.search(r'(\d+)', str(i.get("campaign_duration", ""))) if i.get("campaign_duration") else None
                        if m:
                            months.append(int(m.group(1)))
                    result[section]["operators"][name]["intro_months"].append(max(months) if months else None)

    return result


def run(baseline_only: bool = False):
    log.info("=" * 60)
    log.info("Market Intelligence Agent — START")
    log.info(f"Tidspunkt: {datetime.now().isoformat()}")
    log.info("=" * 60)

    now  = datetime.now()
    week = now.strftime("%V")
    year = now.strftime("%Y")

    if baseline_only:
        log.info("Tilstand: baseline-only (ingen live scraping)")
        operator_data = merge_with_baseline({}, BASELINE["operators"])
    else:
        log.info("Tilstand: live scraping")
        live = {}
        with OperatorScraper(headless=True) as scraper:
            for op_key, op_cfg in OPERATORS.items():
                try:
                    live[op_key] = scrape_operator(scraper, op_key, op_cfg)
                except Exception as e:
                    log.error(f"Fejl ved scraping af {op_key}: {e}")
                    live[op_key] = {}

        operator_data = merge_with_baseline(live, BASELINE["operators"])

    # Load previous snapshot for change detection
    prev_snapshot = load_latest_snapshot()
    if prev_snapshot:
        log.info(f"Sammenligner med snapshot fra: {prev_snapshot.get('scraped_at', '?')[:10]}")
        operator_data = annotate_changes(operator_data, prev_snapshot.get("operators", {}))
    else:
        log.info("Ingen tidligere snapshot fundet — prisændringer vises ved næste kørsel")

    # Fetch news
    log.info("Henter nyheder…")
    print("[NEWS] Starter nyhedshentning…", flush=True)
    try:
        news = fetch_all_news()
        log.info(f"Nyheder i alt: {len(news)} artikler")
        print(f"[NEWS] Færdig: {len(news)} artikler hentet", flush=True)
    except Exception as e:
        log.error(f"Nyhedshentning fejlede helt: {e}")
        print(f"[NEWS] FEJL: {e}", flush=True)
        news = []

    # Fetch roaming data
    try:
        roaming = fetch_roaming_data()
        log.info(f"Roaming: {len(roaming)} abonnementer")
    except Exception as e:
        log.error(f"Roaming-hentning fejlede: {e}")
        roaming = []

    # Build final data package
    output_data = {
        "scraped_at": now.isoformat(),
        "week": week,
        "year": year,
        "operators": operator_data,
        "news": news,
        "roaming": roaming,
    }

    # Save snapshot (before building trends so this week is included)
    save_snapshot(output_data)

    # Build trend time series from all snapshots
    trends = build_trend_data()
    log.info(f"Trenddata: {len(trends['subscriptions']['dates'])} uger")

    # Generate dashboard
    out_path = OUT_DIR / f"konkurrentovervaagning-uge{week}-{year}.html"
    generate_dashboard(output_data, str(out_path), trends=trends)

    log.info("=" * 60)
    log.info(f"✓ Dashboard klar: {out_path}")
    log.info("Market Intelligence Agent — SLUT")
    log.info("=" * 60)

    return str(out_path)


if __name__ == "__main__":
    baseline_only = "--baseline-only" in sys.argv
    run(baseline_only=baseline_only)

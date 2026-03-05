"""
Market Intelligence Agent — Newsroom Scraper
Fetches operator news from two sources:
  1. Google News RSS (primary, always available)
  2. Operator press pages via Playwright (best-effort)
"""

import re
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

log = logging.getLogger(__name__)

# Google News RSS search queries per operator
NEWS_QUERIES = {
    "3":       "3 Danmark mobil",
    "OiSTER":  "OiSTER mobil",
    "Flexii":  "Flexii mobil Danmark",
    "Telenor": "Telenor Danmark mobil",
    "YouSee":  "YouSee mobil",
    "Norlys":  "Norlys mobil",
    "CBB":     "CBB Mobil Danmark",
    "Telmore": "Telmore mobil",
    "Eesy":    "Eesy mobil Danmark",
    "CallMe":  "CallMe mobil Danmark",
}

# Max article age to include
MAX_DAYS = 14
# Max articles per operator
MAX_PER_OP = 8


def _rss_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://news.google.com/rss/search?q={q}&hl=da&gl=DK&ceid=DK:da"


def _parse_date(date_str: str) -> datetime | None:
    """Parse RFC 2822 date from RSS to UTC-aware datetime."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None


def _clean_title(title: str) -> str:
    """Remove ' - Source Name' suffix Google News appends."""
    return re.sub(r'\s*[-–]\s*[^-–]{3,40}$', '', title).strip()


def fetch_google_news(operator: str, days: int = MAX_DAYS) -> list[dict]:
    """Fetch and parse Google News RSS for one operator."""
    query = NEWS_QUERIES.get(operator, operator)
    url   = _rss_url(query)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    articles = []

    try:
        req  = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urlopen(req, timeout=10)
        xml  = resp.read()
        root = ET.fromstring(xml)
    except (URLError, ET.ParseError) as e:
        log.warning(f"  Google News RSS fejl for {operator}: {e}")
        return []

    for item in root.findall(".//item"):
        title    = _clean_title(item.findtext("title", ""))
        link     = item.findtext("link", "")
        pub_raw  = item.findtext("pubDate", "")
        source   = item.findtext("source", "Google News")
        pub_dt   = _parse_date(pub_raw)

        if not title or not link:
            continue
        if pub_dt and pub_dt < cutoff:
            continue

        articles.append({
            "operator":  operator,
            "headline":  title,
            "url":       link,
            "published": pub_dt.strftime("%Y-%m-%d") if pub_dt else "",
            "source":    source,
            "snippet":   "",
        })

        if len(articles) >= MAX_PER_OP:
            break

    log.info(f"  {operator}: {len(articles)} nyheder fra Google News")
    return articles


def fetch_all_news() -> list[dict]:
    """Fetch news for all operators and return merged, date-sorted list."""
    all_news = []
    for operator in NEWS_QUERIES:
        try:
            articles = fetch_google_news(operator)
            all_news.extend(articles)
        except Exception as e:
            log.error(f"  Nyhedsfejl for {operator}: {e}")

    # Sort newest first
    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_news

"""
Market Intelligence Agent — Newsroom Scraper

Three news sources (in priority order):
  1. Danish media RSS feeds  (computerworld.dk, version2.dk, finans.dk) — filtered by keyword
  2. Operator press pages     via Playwright — official announcements
  3. Google News RSS          — fallback, blocked on some hosts
"""

import re
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

log = logging.getLogger(__name__)

MAX_DAYS    = 14   # articles older than this are excluded
MAX_PER_OP  = 8    # max articles per operator in total output

# ── Danish media RSS feeds ────────────────────────────────────────────────────
# These cover Danish IT, business and telecom news.
DANISH_FEEDS = [
    ("Computerworld", "https://www.computerworld.dk/rss/articles"),
    ("Version2",      "https://www.version2.dk/rss/articles"),
    ("Finans",        "https://finans.dk/rss/seneste"),
    ("Børsen",        "https://borsen.dk/rss"),
    ("TV2 Business",  "https://nyheder.tv2.dk/feeds/rss"),
]

# Mynewsdesk RSS — official press releases from operators directly
MYNEWSDESK_FEEDS = [
    ("3",       "https://www.mynewsdesk.com/dk/hi3g-denmark/pressreleases.rss"),
    ("Telenor", "https://www.mynewsdesk.com/dk/telenor/pressreleases.rss"),
    ("YouSee",  "https://www.mynewsdesk.com/dk/tdc/pressreleases.rss"),
    ("Norlys",  "https://www.mynewsdesk.com/dk/norlys/pressreleases.rss"),
    ("CBB",     "https://www.mynewsdesk.com/dk/cbb-mobil/pressreleases.rss"),
    ("Telmore", "https://www.mynewsdesk.com/dk/telmore/pressreleases.rss"),
]

# Keywords to match per operator (lowercase, checked in title+description)
OPERATOR_KEYWORDS = {
    "3":       ["hi3g", "3 danmark", "3's", "3 mobil", "teleselskabet 3"],
    "OiSTER":  ["oister"],
    "Flexii":  ["flexii"],
    "Telenor": ["telenor"],
    "YouSee":  ["yousee", "you see", "tdc"],
    "Norlys":  ["norlys"],
    "CBB":     ["cbb"],
    "Telmore": ["telmore"],
    "Eesy":    ["eesy"],
    "CallMe":  ["callme"],
}

# ── Operator press pages ──────────────────────────────────────────────────────
# Playwright will load these pages and extract article links.
PRESS_PAGES = {
    "Telenor": "https://www.telenor.dk/om-telenor/presse/",
    "YouSee":  "https://yousee.dk/om-yousee/presse/",
    "Norlys":  "https://norlys.dk/presse/",
    "3":       "https://www.3.dk/om-3/",
    "Telmore": "https://www.telmore.dk/presse/",
    "CBB":     "https://www.cbb.dk/om-cbb/presse/",
}

# ── Google News (fallback) ────────────────────────────────────────────────────
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(date_str: str) -> datetime | None:
    """Parse RFC 2822 date string to UTC-aware datetime."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None


def _clean_title(title: str) -> str:
    """Remove ' - Source Name' suffix appended by Google News."""
    return re.sub(r'\s*[-–]\s*[^-–]{3,40}$', '', title).strip()


def _fetch_articles(url: str) -> list[dict]:
    """
    Fetch an RSS or Atom feed and return normalised article dicts.
    Handles RSS 2.0 (<item>) and Atom (<entry>) formats.
    Falls back to feedparser if standard XML parsing fails.
    """
    req  = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; MarketIntelBot/1.0)"})
    resp = urlopen(req, timeout=15)
    raw  = resp.read()

    # Try standard XML first
    try:
        root  = ET.fromstring(raw)
        ns    = {"atom": "http://www.w3.org/2005/Atom"}

        # RSS 2.0
        items = root.findall(".//item")
        if items:
            return [
                {
                    "title":   i.findtext("title", "").strip(),
                    "link":    i.findtext("link", "").strip(),
                    "pubDate": i.findtext("pubDate", ""),
                    "text":    (i.findtext("title", "") + " " + i.findtext("description", "")).lower(),
                }
                for i in items
            ]

        # Atom
        entries = root.findall(".//atom:entry", ns) or root.findall(".//entry")
        if entries:
            def _atom_link(e):
                link_el = e.find("atom:link[@rel='alternate']", ns) or e.find("atom:link", ns) or e.find("link")
                if link_el is not None:
                    return link_el.get("href", link_el.text or "")
                return ""
            def _atom_date(e):
                return (e.findtext("atom:updated", "", ns) or e.findtext("atom:published", "", ns)
                        or e.findtext("updated", "") or e.findtext("published", ""))
            return [
                {
                    "title":   (e.findtext("atom:title", "", ns) or e.findtext("title", "")).strip(),
                    "link":    _atom_link(e),
                    "pubDate": _atom_date(e),
                    "text":    ((e.findtext("atom:title", "", ns) or e.findtext("title", "")) + " " +
                                (e.findtext("atom:summary", "", ns) or e.findtext("summary", "") or
                                 e.findtext("atom:content", "", ns) or e.findtext("content", ""))).lower(),
                }
                for e in entries
            ]
    except ET.ParseError:
        pass

    # Fallback: feedparser (handles malformed / unusual feeds)
    try:
        import feedparser
        feed = feedparser.parse(raw)
        return [
            {
                "title":   e.get("title", "").strip(),
                "link":    e.get("link", ""),
                "pubDate": e.get("published", e.get("updated", "")),
                "text":    (e.get("title", "") + " " + e.get("summary", "")).lower(),
            }
            for e in feed.entries
        ]
    except Exception:
        pass

    return []


def _matches(article: dict, keywords: list[str]) -> bool:
    """Check if article text contains any of the operator keywords."""
    return any(kw in article["text"] for kw in keywords)


def _deduplicate(articles: list[dict]) -> list[dict]:
    """Remove duplicates by URL."""
    seen = set()
    out  = []
    for a in articles:
        url = a.get("url", "")
        if url and url not in seen:
            seen.add(url)
            out.append(a)
    return out


# ── Source 1: Danish media RSS ────────────────────────────────────────────────

def fetch_danish_media_news(days: int = MAX_DAYS) -> list[dict]:
    """
    Fetch all Danish media RSS/Atom feeds and return articles tagged by operator.
    """
    cutoff   = datetime.now(timezone.utc) - timedelta(days=days)
    articles = []

    for source_name, feed_url in DANISH_FEEDS:
        try:
            raw_articles = _fetch_articles(feed_url)
            log.info(f"  {source_name}: {len(raw_articles)} artikler hentet")
        except Exception as e:
            log.warning(f"  {source_name} RSS fejl: {e}")
            continue

        matched = 0
        for art in raw_articles:
            pub_dt = _parse_date(art["pubDate"])
            if pub_dt and pub_dt < cutoff:
                continue

            title = art["title"]
            link  = art["link"]
            if not title or not link:
                continue

            # Tag with all matching operators
            for operator, keywords in OPERATOR_KEYWORDS.items():
                if _matches(art, keywords):
                    articles.append({
                        "operator":  operator,
                        "headline":  title,
                        "url":       link,
                        "published": pub_dt.strftime("%Y-%m-%d") if pub_dt else "",
                        "source":    source_name,
                        "snippet":   "",
                    })
                    matched += 1

        log.info(f"  {source_name}: {matched} operatør-matches")

    log.info(f"  Danske medier total: {len(articles)} artikler")
    return articles


# ── Source 2: Mynewsdesk RSS (operator press releases) ───────────────────────

def fetch_mynewsdesk_news(days: int = MAX_DAYS) -> list[dict]:
    """
    Fetch operator press releases from Mynewsdesk RSS feeds.
    Each feed belongs to a single operator — no keyword matching needed.
    """
    cutoff   = datetime.now(timezone.utc) - timedelta(days=days)
    articles = []

    for operator, feed_url in MYNEWSDESK_FEEDS:
        try:
            raw = _fetch_articles(feed_url)
            count = 0
            for art in raw:
                pub_dt = _parse_date(art["pubDate"])
                if pub_dt and pub_dt < cutoff:
                    continue
                if not art["title"] or not art["link"]:
                    continue
                articles.append({
                    "operator":  operator,
                    "headline":  art["title"],
                    "url":       art["link"],
                    "published": pub_dt.strftime("%Y-%m-%d") if pub_dt else "",
                    "source":    "Mynewsdesk",
                    "snippet":   "",
                })
                count += 1
            log.info(f"  Mynewsdesk {operator}: {count} pressemeddelelser")
        except Exception as e:
            log.warning(f"  Mynewsdesk fejl for {operator}: {e}")

    log.info(f"  Mynewsdesk total: {len(articles)} artikler")
    return articles


# ── Source 3: Operator press pages via Playwright ─────────────────────────────

def fetch_press_pages(days: int = MAX_DAYS) -> list[dict]:
    """Scrape operator press pages with Playwright. Returns article list."""
    articles = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("  Playwright ikke tilgængelig — springer presserum over")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # JS: only collect links whose URL contains a news/press path segment,
    # and whose title doesn't look like navigation or a product name.
    EXTRACT_JS = """() => {
        const NEWS_PATHS = /\\/(presse|news|nyhed|artikel|pressemeddelelse|blog|announce|release)\\//i;
        const NAV_TITLES = /^(søg|gå til|se alle|om |fordele|guide:|log ind|kontakt|find|køb|bestil|tilmeld|læs mere|back|forside|menu|hjem)/i;
        const links = [];
        const seen = new Set();
        document.querySelectorAll('a[href]').forEach(a => {
            const href = a.href || '';
            const text = (a.innerText || '').replace(/\\s+/g, ' ').trim();
            if (!href.startsWith('http')) return;
            if (!NEWS_PATHS.test(href)) return;
            if (text.length < 20 || text.length > 180) return;
            if (NAV_TITLES.test(text)) return;
            if (seen.has(href)) return;
            seen.add(href);
            links.push({title: text, href});
        });
        return links.slice(0, 25);
    }"""

    # Python-side blocklist for titles that slip through
    JUNK_PATTERNS = re.compile(
        r'^(søg|gå til|se alle|om |fordele|guide:|log ind|kontakt|find|køb|'
        r'bestil|tilmeld|læs mere|back|forside|menu|hjem|'
        r'mobilabonnement|mobilt bredbånd|populære mærker|se forbrug|'
        r'erhvervsinternet|medarbejderbredbånd|kom godt i gang)',
        re.IGNORECASE
    )

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            for operator, url in PRESS_PAGES.items():
                try:
                    page = browser.new_page()
                    page.set_extra_http_headers({"User-Agent":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"})
                    page.goto(url, timeout=25000, wait_until="domcontentloaded")
                    page.wait_for_timeout(1500)
                    links = page.evaluate(EXTRACT_JS)
                    page.close()
                    added = 0
                    for lnk in links:
                        headline = lnk["title"].replace("\n", " ").strip()
                        if JUNK_PATTERNS.match(headline):
                            continue
                        articles.append({
                            "operator":  operator,
                            "headline":  headline,
                            "url":       lnk["href"],
                            "published": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                            "source":    f"{operator} Presse",
                            "snippet":   "",
                        })
                        added += 1
                    log.info(f"  {operator} presserum: {added} artikler (af {len(links)} links)")
                except Exception as e:
                    log.warning(f"  Playwright fejl for {operator} ({url}): {e}")
            browser.close()
    except Exception as e:
        log.error(f"  Playwright browser fejlede helt: {e}")

    return articles


# ── Source 3: Google News RSS (fallback) ──────────────────────────────────────

def _google_rss_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://news.google.com/rss/search?q={q}&hl=da&gl=DK&ceid=DK:da"


def fetch_google_news(operator: str, days: int = MAX_DAYS) -> list[dict]:
    """Fetch Google News RSS for one operator. Returns [] on any error."""
    query  = NEWS_QUERIES.get(operator, operator)
    url    = _google_rss_url(query)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        req  = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urlopen(req, timeout=10)
        root = ET.fromstring(resp.read())
    except Exception as e:
        log.warning(f"  Google News fejl for {operator}: {e}")
        return []

    articles = []
    for item in root.findall(".//item"):
        title   = _clean_title(item.findtext("title", ""))
        link    = item.findtext("link", "")
        pub_dt  = _parse_date(item.findtext("pubDate", ""))
        source  = item.findtext("source", "Google News")

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

    return articles


# ── Main entry point ──────────────────────────────────────────────────────────

def fetch_all_news() -> list[dict]:
    """
    Fetch news from all sources, deduplicate, and return sorted newest-first.
    Each source is isolated — one failure never blocks the others.
    """
    all_articles = []

    # Source 1: Danish media RSS (bulk, then keyword-filter)
    try:
        log.info("Henter nyheder fra danske medier…")
        danish = fetch_danish_media_news()
        all_articles.extend(danish)
        print(f"[NEWS-1] Danske medier: {len(danish)} artikler", flush=True)
    except Exception as e:
        log.error(f"fetch_danish_media_news fejlede: {e}")
        print(f"[NEWS-1] FEJL danske medier: {e}", flush=True)

    # Source 2: Mynewsdesk operator press releases (most reliable)
    try:
        log.info("Henter pressemeddelelser fra Mynewsdesk…")
        mnd = fetch_mynewsdesk_news()
        all_articles.extend(mnd)
        print(f"[NEWS-2] Mynewsdesk: {len(mnd)} artikler", flush=True)
    except Exception as e:
        log.error(f"fetch_mynewsdesk_news fejlede: {e}")
        print(f"[NEWS-2] FEJL Mynewsdesk: {e}", flush=True)

    # Source 3: Operator press pages via Playwright
    try:
        log.info("Henter nyheder fra operatørers presserum…")
        press = fetch_press_pages()
        all_articles.extend(press)
        print(f"[NEWS-3] Presserum (Playwright): {len(press)} artikler", flush=True)
    except Exception as e:
        log.error(f"fetch_press_pages fejlede: {e}")
        print(f"[NEWS-3] FEJL presserum: {e}", flush=True)

    # Source 4: Google News (fallback)
    log.info("Henter nyheder fra Google News (fallback)…")
    google_total = 0
    for operator in NEWS_QUERIES:
        try:
            arts = fetch_google_news(operator)
            all_articles.extend(arts)
            google_total += len(arts)
        except Exception as e:
            log.error(f"fetch_google_news fejlede for {operator}: {e}")
    print(f"[NEWS-4] Google News: {google_total} artikler i alt", flush=True)

    # Deduplicate and cap per operator
    all_articles = _deduplicate(all_articles)

    per_op: dict[str, list] = {}
    for a in all_articles:
        op = a["operator"]
        per_op.setdefault(op, []).append(a)

    capped = []
    for op, items in per_op.items():
        items.sort(key=lambda x: x.get("published", ""), reverse=True)
        capped.extend(items[:MAX_PER_OP])

    capped.sort(key=lambda x: x.get("published", ""), reverse=True)
    log.info(f"Nyheder i alt: {len(capped)} artikler (efter cap)")
    return capped

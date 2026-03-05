"""
Market Intelligence Agent — Playwright-based Scraper
Navigates to each operator's pricing pages and extracts raw page content.
"""

import re
import time
import random
import logging
from typing import Optional

from playwright.sync_api import sync_playwright, Page, Browser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Danish price patterns
RE_PRICE = re.compile(r"(\d[\d\.\,]+)\s*kr", re.IGNORECASE)
RE_DATA  = re.compile(r"(\d+)\s*(?:GB|gb)", re.IGNORECASE)
RE_FREE  = re.compile(r"fri\s*(?:data|gb|tale)?", re.IGNORECASE)
RE_CAMPAIGN_PRICE = re.compile(
    r"(\d[\d\.\,]+)\s*kr\.?\s*/?\s*(\d+)\s*(?:mdr|md)", re.IGNORECASE
)

STREAMING_KEYWORDS = [
    "viaplay", "disney+", "disney plus", "netflix", "tv2 play", "tv2play",
    "hbo max", "max", "deezer", "podimo", "telmore musik", "yousee musik",
    "nordisk film", "sky showtime", "saxo", "wype",
]


class OperatorScraper:
    """Scrapes a single operator's website using a headless Chromium browser."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._pw = None
        self._browser: Optional[Browser] = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        return self

    def __exit__(self, *args):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _new_page(self) -> Page:
        context = self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="da-DK",
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()
        # Disable automation flags
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return page

    def fetch(self, url: str, wait_seconds: int = 4, load_more: bool = False) -> Optional[str]:
        """Navigate to URL and return rendered page text.

        load_more=True clicks any 'Vis flere' / 'Se flere' style buttons
        repeatedly until none remain, then also attempts a final scroll to
        trigger any infinite-scroll pagination.
        """
        page = self._new_page()
        try:
            log.info(f"Fetching: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            time.sleep(wait_seconds + random.uniform(0.5, 1.5))

            # Try to dismiss cookie banners
            for selector in [
                "button:has-text('Accepter')", "button:has-text('Accepter alle')",
                "button:has-text('OK')", "#accept-all", ".accept-cookies",
                "[data-testid='cookie-accept']",
            ]:
                try:
                    btn = page.query_selector(selector)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(0.5)
                        break
                except Exception:
                    pass

            # Wait a moment for content to settle
            time.sleep(1.5)

            # Paginate through "load more" buttons and infinite scroll
            if load_more:
                self._exhaust_load_more(page)

            return page.inner_text("body")

        except Exception as e:
            log.warning(f"Failed to fetch {url}: {e}")
            return None
        finally:
            try:
                page.context.close()
            except Exception:
                pass

    def _exhaust_load_more(self, page: Page, max_clicks: int = 15) -> None:
        """Click 'load more' buttons and scroll until all products are visible."""
        # Common Danish and English load-more patterns
        LOAD_MORE_SELECTORS = [
            "button:has-text('Vis flere')",
            "button:has-text('Se flere')",
            "button:has-text('Indlæs flere')",
            "button:has-text('Vis alle')",
            "button:has-text('Hent flere')",
            "button:has-text('Load more')",
            "button:has-text('Show more')",
            "a:has-text('Vis flere')",
            "a:has-text('Se flere')",
            "[data-testid='load-more']",
            "[class*='load-more']",
            "[class*='loadmore']",
            "[class*='show-more']",
        ]

        prev_height = 0
        for click_num in range(max_clicks):
            clicked = False

            for selector in LOAD_MORE_SELECTORS:
                try:
                    btn = page.query_selector(selector)
                    if btn and btn.is_visible():
                        btn.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        btn.click()
                        time.sleep(2.0)  # wait for new batch to render
                        clicked = True
                        log.info(f"  'Load more' klik #{click_num + 1}")
                        break
                except Exception:
                    pass

            if not clicked:
                # Scroll to bottom to trigger any infinite-scroll loaders
                curr_height = page.evaluate("document.body.scrollHeight")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == prev_height:
                    break  # page stopped growing — we have everything
                prev_height = new_height


# ── Extraction helpers ────────────────────────────────────────────────────────

def extract_prices_from_text(text: str) -> list[dict]:
    """
    Naive but robust: walks line-by-line through page text and
    tries to assemble subscription records from price + nearby context.
    Returns a list of raw dicts for further normalisation.
    """
    records = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    for i, line in enumerate(lines):
        prices = RE_PRICE.findall(line)
        if not prices:
            continue

        # Collect context window (3 lines before, 2 after)
        ctx = " | ".join(lines[max(0, i - 3): i + 3])

        # Determine data allowance
        data_match = RE_DATA.search(ctx)
        data_gb = int(data_match.group(1)) if data_match else None
        is_free_data = bool(RE_FREE.search(ctx))

        # Campaign price detection
        camp_match = RE_CAMPAIGN_PRICE.search(ctx)
        campaign_price = None
        campaign_months = None
        if camp_match:
            campaign_price = _parse_price(camp_match.group(1))
            campaign_months = int(camp_match.group(2))

        # Detect included streaming
        ctx_lower = ctx.lower()
        entertainment = [s for s in STREAMING_KEYWORDS if s in ctx_lower]

        # Coverage detection
        coverage = "DK"
        if "verden" in ctx_lower:
            coverage = "Verden"
        elif "eu" in ctx_lower:
            coverage = "EU"

        # Talk allowance
        talk = "Fri" if "fri tale" in ctx_lower else "Begrænset"

        main_price = _parse_price(prices[0])
        if main_price and main_price > 10:  # filter out small incidental numbers
            records.append({
                "context": ctx[:200],
                "price": main_price,
                "data_gb": "Fri" if is_free_data else data_gb,
                "talk": talk,
                "coverage": coverage,
                "campaign_price": campaign_price,
                "campaign_months": campaign_months,
                "entertainment": list(dict.fromkeys(entertainment)),  # dedupe
            })

    return records


def _parse_price(raw: str) -> Optional[float]:
    """Convert Danish price string '1.099,00' or '99' to float."""
    try:
        cleaned = raw.replace(".", "").replace(",", ".")
        val = float(cleaned)
        return val if 10 <= val <= 25_000 else None
    except (ValueError, TypeError):
        return None

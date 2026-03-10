"""
Market Intelligence Agent — Roaming Scraper

Henter Roam Like Home-lande og vilkår fra operatørernes sider via Playwright.
Falder tilbage på baseline-data hvis scraping fejler.
"""

import re
import logging
from playwright.sync_api import sync_playwright

log = logging.getLogger(__name__)

# ── Roaming-sider pr. operatør ────────────────────────────────────────────────
ROAMING_URLS = {
    "Telenor": "https://www.telenor.dk/shop/abonnementer/andet/modal-brug-los-paa-ferien/",
    "3":       "https://www.3.dk/udland/",
    "Norlys":  "https://shop.norlys.dk/kundeservice/mobil/udland/",
    "YouSee":  "https://yousee.dk/roaming",
}

# ── Alle EU/EØS-lande (baseline — alle operatører dækker disse) ───────────────
EU_EEA_COUNTRIES = [
    "Belgien", "Bulgarien", "Cypern", "Danmark", "Estland", "Finland",
    "Frankrig", "Grækenland", "Irland", "Italien", "Kroatien", "Letland",
    "Litauen", "Luxembourg", "Malta", "Nederlandene", "Polen", "Portugal",
    "Rumænien", "Slovakiet", "Slovenien", "Spanien", "Sverige", "Tjekkiet",
    "Tyskland", "Ungarn", "Østrig",
    # EØS (ikke EU)
    "Island", "Liechtenstein", "Norge",
    # Øvrige med EU-roaming aftale
    "Schweiz", "Storbritannien", "Nordirland", "Gibraltar",
    "Guadeloupe", "Martinique", "Réunion", "Azorerne", "Madeira",
    "De Kanariske Øer",
]

# ── Baseline-data (bruges som fallback og første datapunkt) ───────────────────
# Kilde: operatørernes sider, verificeret marts 2026
ROAMING_BASELINE = [
    # ── Telenor (75 destinationer) ────────────────────────────────────────────
    {
        "operator": "Telenor",
        "subscription": "Fri Tale S",
        "price_dkk": 179,
        "data_eu_gb": 10,
        "total_countries": 75,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "Inkluderer EU/EØS. Datahastighed reduceres efter forbrug.",
    },
    {
        "operator": "Telenor",
        "subscription": "Fri Tale M",
        "price_dkk": 219,
        "data_eu_gb": 20,
        "total_countries": 75,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "Inkluderer EU/EØS.",
    },
    {
        "operator": "Telenor",
        "subscription": "Fri Tale L",
        "price_dkk": 279,
        "data_eu_gb": 40,
        "total_countries": 75,
        "roam_zone": "EU/EØS + ekstra",
        "extra_countries": ["USA", "Canada", "Australien", "New Zealand",
                            "Schweiz", "Albanien", "Bosnien-Hercegovina",
                            "Nordmakedonien", "Serbien", "Ukraine"],
        "notes": "Udvalgte abonnementer inkluderer ekstra lande uden for EU/EØS.",
    },
    {
        "operator": "Telenor",
        "subscription": "Fri Tale XL",
        "price_dkk": 329,
        "data_eu_gb": 60,
        "total_countries": 75,
        "roam_zone": "EU/EØS + ekstra",
        "extra_countries": ["USA", "Canada", "Australien", "New Zealand",
                            "Schweiz", "Albanien", "Bosnien-Hercegovina",
                            "Nordmakedonien", "Serbien", "Ukraine"],
        "notes": "Inkluderer samme ekstra lande som L.",
    },

    # ── 3 (100 destinationer med 3Like Home) ──────────────────────────────────
    {
        "operator": "3",
        "subscription": "3Fri 5 GB",
        "price_dkk": 149,
        "data_eu_gb": 5,
        "total_countries": 40,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "EU/EØS roaming inkluderet.",
    },
    {
        "operator": "3",
        "subscription": "3Fri 15 GB",
        "price_dkk": 199,
        "data_eu_gb": 15,
        "total_countries": 100,
        "roam_zone": "3Like Home (100 lande)",
        "extra_countries": ["USA", "Australien", "Hongkong", "Singapore",
                            "Sri Lanka", "Macau", "Indonesien", "Israel",
                            "Sverige", "Norge", "Finland", "Schweiz",
                            "Albanien", "Serbien", "Nordmakedonien"],
        "notes": "3Like Home: brug dit abonnement som derhjemme i 100 lande.",
    },
    {
        "operator": "3",
        "subscription": "3Fri 30 GB",
        "price_dkk": 249,
        "data_eu_gb": 30,
        "total_countries": 100,
        "roam_zone": "3Like Home (100 lande)",
        "extra_countries": ["USA", "Australien", "Hongkong", "Singapore",
                            "Sri Lanka", "Macau", "Indonesien", "Israel",
                            "Sverige", "Norge", "Finland", "Schweiz",
                            "Albanien", "Serbien", "Nordmakedonien"],
        "notes": "Samme 3Like Home-dækning som 15 GB.",
    },
    {
        "operator": "3",
        "subscription": "3Fri Unlimited",
        "price_dkk": 299,
        "data_eu_gb": 999,
        "total_countries": 100,
        "roam_zone": "3Like Home (100 lande)",
        "extra_countries": ["USA", "Australien", "Hongkong", "Singapore",
                            "Sri Lanka", "Macau", "Indonesien", "Israel",
                            "Sverige", "Norge", "Finland", "Schweiz",
                            "Albanien", "Serbien", "Nordmakedonien"],
        "notes": "Ubegrænset data. 3Like Home i 100 lande.",
    },

    # ── YouSee (51 destinationer) ─────────────────────────────────────────────
    {
        "operator": "YouSee",
        "subscription": "Mobil S",
        "price_dkk": 149,
        "data_eu_gb": 5,
        "total_countries": 51,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "Standardroaming i EU/EØS.",
    },
    {
        "operator": "YouSee",
        "subscription": "Mobil M",
        "price_dkk": 199,
        "data_eu_gb": 15,
        "total_countries": 51,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "Standardroaming i EU/EØS.",
    },
    {
        "operator": "YouSee",
        "subscription": "Mobil L",
        "price_dkk": 249,
        "data_eu_gb": 30,
        "total_countries": 51,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "Standardroaming i EU/EØS.",
    },
    {
        "operator": "YouSee",
        "subscription": "Mobil XL",
        "price_dkk": 299,
        "data_eu_gb": 50,
        "total_countries": 51,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "Standardroaming i EU/EØS.",
    },

    # ── Norlys (80 destinationer) ─────────────────────────────────────────────
    {
        "operator": "Norlys",
        "subscription": "Mobil S",
        "price_dkk": 139,
        "data_eu_gb": 5,
        "total_countries": 80,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "EU/EØS roaming inkluderet.",
    },
    {
        "operator": "Norlys",
        "subscription": "Mobil M",
        "price_dkk": 189,
        "data_eu_gb": 15,
        "total_countries": 80,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "EU/EØS roaming inkluderet.",
    },
    {
        "operator": "Norlys",
        "subscription": "Mobil L",
        "price_dkk": 239,
        "data_eu_gb": 30,
        "total_countries": 80,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "EU/EØS roaming inkluderet.",
    },
    {
        "operator": "Norlys",
        "subscription": "Mobil XL",
        "price_dkk": 289,
        "data_eu_gb": 50,
        "total_countries": 80,
        "roam_zone": "EU/EØS",
        "extra_countries": [],
        "notes": "EU/EØS roaming inkluderet.",
    },
]


def fetch_roaming_data() -> list[dict]:
    """
    Forsøger at hente opdaterede roaming-data via Playwright.
    Returnerer baseline-data ved fejl.
    """
    log.info("Henter roaming-data…")
    try:
        live = _scrape_all()
        if live:
            log.info(f"  Roaming: {len(live)} abonnementer hentet live")
            return live
    except Exception as e:
        log.warning(f"  Roaming-scraping fejlede, bruger baseline: {e}")

    log.info(f"  Roaming: bruger baseline ({len(ROAMING_BASELINE)} abonnementer)")
    return ROAMING_BASELINE


def _scrape_all() -> list[dict]:
    """Kør Playwright og hent roaming-data fra alle operatører."""
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for operator, url in ROAMING_URLS.items():
            try:
                page = browser.new_page()
                page.set_extra_http_headers({"User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"})
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                # Hent al tekst fra siden og find lande
                text = page.inner_text("body")
                countries = _extract_countries(text)
                log.info(f"  {operator}: {len(countries)} lande fundet på siden")

                # Brug baseline for abonnementsstruktur men opdater lande
                for plan in ROAMING_BASELINE:
                    if plan["operator"] == operator:
                        updated = dict(plan)
                        if countries:
                            # Opdater extra_countries hvis vi fandt lande på siden
                            extra = [c for c in countries if c not in EU_EEA_COUNTRIES]
                            if extra:
                                updated["extra_countries"] = extra
                        results.append(updated)

                page.close()
            except Exception as e:
                log.warning(f"  Roaming-fejl for {operator}: {e}")
                # Brug baseline for denne operatør
                results.extend([p for p in ROAMING_BASELINE if p["operator"] == operator])

        browser.close()

    return results if results else []


# Alle kendte landenavne vi søger efter i teksten
_ALL_COUNTRIES = EU_EEA_COUNTRIES + [
    "USA", "Canada", "Australien", "New Zealand", "Hongkong", "Singapore",
    "Sri Lanka", "Macau", "Indonesien", "Israël", "Israel", "Japan", "Sydkorea",
    "Albanien", "Bosnien", "Serbien", "Nordmakedonien", "Makedonien", "Ukraine",
    "Montenegro", "Georgien", "Armenien", "Moldavien", "Kosovo",
    "Marokko", "Tunesien", "Egypten", "Sydafrika", "Kenya",
    "Thailand", "Malaysia", "Vietnam", "Filippinerne", "Indien",
    "Tyrkiet", "Jordan", "De Forenede Arabiske Emirater", "UAE",
    "Mexico", "Brasilien", "Argentina", "Chile", "Colombia",
]

def _extract_countries(text: str) -> list[str]:
    """Find landenavne i fri tekst."""
    found = []
    text_lower = text.lower()
    for country in _ALL_COUNTRIES:
        if country.lower() in text_lower:
            found.append(country)
    return list(dict.fromkeys(found))  # bevar rækkefølge, fjern dubletter

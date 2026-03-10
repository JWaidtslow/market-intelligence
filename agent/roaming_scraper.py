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
    # Kilde: telenor.dk/shop/abonnementer + modal-brug-los-paa-ferien, marts 2026
    # Alle 4 abonnementer inkluderer samme 75 lande (Roam Away)
    # data_eu_gb = GB inkluderet i roaming-zone (ikke totalt data)
    {
        "operator": "Telenor",
        "subscription": "Fri Tale 30 GB",
        "price_dkk": 169,
        "data_eu_gb": 30,
        "total_countries": 75,
        "roam_zone": "Roam Away (75 lande)",
        "extra_countries": [
            "Filippinerne", "Færøerne", "Hongkong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mexico",
            "Moldova", "Monaco", "Montenegro", "Myanmar", "Nordmakedonien",
            "Pakistan", "Saint-Martin", "Serbien", "Singapore", "Sydkorea",
            "Taiwan", "Thailand", "Tyrkiet", "Ukraine", "USA",
            "Vatikanstaten", "Vietnam",
        ],
        "notes": "Roam Away: 75 lande inkl. USA, Asien, Balkan m.fl.",
    },
    {
        "operator": "Telenor",
        "subscription": "Fri Tale 80 GB",
        "price_dkk": 209,
        "data_eu_gb": 45,
        "total_countries": 75,
        "roam_zone": "Roam Away (75 lande)",
        "extra_countries": [
            "Filippinerne", "Færøerne", "Hongkong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mexico",
            "Moldova", "Monaco", "Montenegro", "Myanmar", "Nordmakedonien",
            "Pakistan", "Saint-Martin", "Serbien", "Singapore", "Sydkorea",
            "Taiwan", "Thailand", "Tyrkiet", "Ukraine", "USA",
            "Vatikanstaten", "Vietnam",
        ],
        "notes": "Roam Away: 75 lande. 45 GB i roaming-zone.",
    },
    {
        "operator": "Telenor",
        "subscription": "Fri Tale 120 GB",
        "price_dkk": 239,
        "data_eu_gb": 55,
        "total_countries": 75,
        "roam_zone": "Roam Away (75 lande)",
        "extra_countries": [
            "Filippinerne", "Færøerne", "Hongkong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mexico",
            "Moldova", "Monaco", "Montenegro", "Myanmar", "Nordmakedonien",
            "Pakistan", "Saint-Martin", "Serbien", "Singapore", "Sydkorea",
            "Taiwan", "Thailand", "Tyrkiet", "Ukraine", "USA",
            "Vatikanstaten", "Vietnam",
        ],
        "notes": "Roam Away: 75 lande. 55 GB i roaming-zone.",
    },
    {
        "operator": "Telenor",
        "subscription": "Fri Tale Fri Data",
        "price_dkk": 289,
        "data_eu_gb": 65,
        "total_countries": 75,
        "roam_zone": "Roam Away (75 lande)",
        "extra_countries": [
            "Filippinerne", "Færøerne", "Hongkong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mexico",
            "Moldova", "Monaco", "Montenegro", "Myanmar", "Nordmakedonien",
            "Pakistan", "Saint-Martin", "Serbien", "Singapore", "Sydkorea",
            "Taiwan", "Thailand", "Tyrkiet", "Ukraine", "USA",
            "Vatikanstaten", "Vietnam",
        ],
        "notes": "Roam Away: 75 lande. 65 GB i roaming-zone.",
    },

    # ── 3 (100 destinationer med 3LikeHome) ───────────────────────────────────
    # Kilde: 3.dk/shop/mobilabonnementer + 3.dk/udland, verificeret marts 2026
    # Alle 4 abonnementer inkluderer 3LikeHome i 100 lande
    {
        "operator": "3",
        "subscription": "Fri Tale 10 GB",
        "price_dkk": 125,
        "data_eu_gb": 10,
        "total_countries": 100,
        "roam_zone": "3LikeHome (100 lande)",
        "extra_countries": [
            "Albanien", "Amerikanske Jomfruøer", "Andorra", "Argentina",
            "Australien", "Bolivia", "Bosnien-Hercegovina", "Brasilien",
            "Brunei", "Cambodja", "Cameroun", "Canada", "Chile", "Costa Rica",
            "Dubai", "Egypten", "Elfenbenskysten", "Færøerne",
            "Forenede Arabiske Emirater", "Fransk Guyana", "Georgien",
            "Hongkong", "Indonesien", "Isle of Man", "Israel", "Japan",
            "Kina", "Kiribati", "Kosovo", "Macao", "Malaysia", "Mali",
            "Mayotte", "Mexico", "Moldova", "Montenegro", "New Zealand",
            "Nigeria", "Nordmakedonien", "Pakistan", "Puerto Rico",
            "Rusland", "S. Barthèlemy", "S. Martin", "San Marino",
            "Senegal", "Seychellerne", "Singapore", "Sri Lanka", "Sydafrika",
            "Sydkorea", "Taiwan", "Tanzania", "Thailand", "Tyrkiet",
            "Uganda", "Ukraine", "USA", "Usbekistan", "Vatikanstaten",
            "Vietnam", "Wales", "Zambia",
        ],
        "notes": "3LikeHome: brug abonnementet som derhjemme i 100 lande.",
    },
    {
        "operator": "3",
        "subscription": "Fri Tale 50 GB",
        "price_dkk": 170,
        "data_eu_gb": 50,
        "total_countries": 100,
        "roam_zone": "3LikeHome (100 lande)",
        "extra_countries": [
            "Albanien", "Amerikanske Jomfruøer", "Andorra", "Argentina",
            "Australien", "Bolivia", "Bosnien-Hercegovina", "Brasilien",
            "Brunei", "Cambodja", "Cameroun", "Canada", "Chile", "Costa Rica",
            "Dubai", "Egypten", "Elfenbenskysten", "Færøerne",
            "Forenede Arabiske Emirater", "Fransk Guyana", "Georgien",
            "Hongkong", "Indonesien", "Isle of Man", "Israel", "Japan",
            "Kina", "Kiribati", "Kosovo", "Macao", "Malaysia", "Mali",
            "Mayotte", "Mexico", "Moldova", "Montenegro", "New Zealand",
            "Nigeria", "Nordmakedonien", "Pakistan", "Puerto Rico",
            "Rusland", "S. Barthèlemy", "S. Martin", "San Marino",
            "Senegal", "Seychellerne", "Singapore", "Sri Lanka", "Sydafrika",
            "Sydkorea", "Taiwan", "Tanzania", "Thailand", "Tyrkiet",
            "Uganda", "Ukraine", "USA", "Usbekistan", "Vatikanstaten",
            "Vietnam", "Wales", "Zambia",
        ],
        "notes": "3LikeHome i 100 lande.",
    },
    {
        "operator": "3",
        "subscription": "Fri Tale 100 GB",
        "price_dkk": 210,
        "data_eu_gb": 100,
        "total_countries": 100,
        "roam_zone": "3LikeHome (100 lande)",
        "extra_countries": [
            "Albanien", "Amerikanske Jomfruøer", "Andorra", "Argentina",
            "Australien", "Bolivia", "Bosnien-Hercegovina", "Brasilien",
            "Brunei", "Cambodja", "Cameroun", "Canada", "Chile", "Costa Rica",
            "Dubai", "Egypten", "Elfenbenskysten", "Færøerne",
            "Forenede Arabiske Emirater", "Fransk Guyana", "Georgien",
            "Hongkong", "Indonesien", "Isle of Man", "Israel", "Japan",
            "Kina", "Kiribati", "Kosovo", "Macao", "Malaysia", "Mali",
            "Mayotte", "Mexico", "Moldova", "Montenegro", "New Zealand",
            "Nigeria", "Nordmakedonien", "Pakistan", "Puerto Rico",
            "Rusland", "S. Barthèlemy", "S. Martin", "San Marino",
            "Senegal", "Seychellerne", "Singapore", "Sri Lanka", "Sydafrika",
            "Sydkorea", "Taiwan", "Tanzania", "Thailand", "Tyrkiet",
            "Uganda", "Ukraine", "USA", "Usbekistan", "Vatikanstaten",
            "Vietnam", "Wales", "Zambia",
        ],
        "notes": "3LikeHome i 100 lande. Op til 75 GB uden for EU/UK.",
    },
    {
        "operator": "3",
        "subscription": "Fri Tale Fri Data",
        "price_dkk": 270,
        "data_eu_gb": 999,
        "total_countries": 100,
        "roam_zone": "3LikeHome (100 lande)",
        "extra_countries": [
            "Albanien", "Amerikanske Jomfruøer", "Andorra", "Argentina",
            "Australien", "Bolivia", "Bosnien-Hercegovina", "Brasilien",
            "Brunei", "Cambodja", "Cameroun", "Canada", "Chile", "Costa Rica",
            "Dubai", "Egypten", "Elfenbenskysten", "Færøerne",
            "Forenede Arabiske Emirater", "Fransk Guyana", "Georgien",
            "Hongkong", "Indonesien", "Isle of Man", "Israel", "Japan",
            "Kina", "Kiribati", "Kosovo", "Macao", "Malaysia", "Mali",
            "Mayotte", "Mexico", "Moldova", "Montenegro", "New Zealand",
            "Nigeria", "Nordmakedonien", "Pakistan", "Puerto Rico",
            "Rusland", "S. Barthèlemy", "S. Martin", "San Marino",
            "Senegal", "Seychellerne", "Singapore", "Sri Lanka", "Sydafrika",
            "Sydkorea", "Taiwan", "Tanzania", "Thailand", "Tyrkiet",
            "Uganda", "Ukraine", "USA", "Usbekistan", "Vatikanstaten",
            "Vietnam", "Wales", "Zambia",
        ],
        "notes": "Fri Data. 3LikeHome i 100 lande. Op til 75 GB uden for EU/UK.",
    },

    # ── YouSee (51 destinationer) — Roaming World ─────────────────────────────
    # Kilde: yousee.dk/roaming, verificeret marts 2026
    # 39 europæiske lande + 12 ekstra: USA, Thailand, Tyrkiet, Australien,
    # Canada, Færøerne, New Zealand, Hong Kong, Japan, Kina, Malaysia, Singapore
    {
        "operator": "YouSee",
        "subscription": "Mobil S",
        "price_dkk": 179,
        "data_eu_gb": 25,
        "total_countries": 51,
        "roam_zone": "Roaming World",
        "extra_countries": [
            "USA", "Thailand", "Tyrkiet", "Australien", "Canada",
            "Færøerne", "New Zealand", "Hong Kong", "Japan", "Kina",
            "Malaysia", "Singapore",
        ],
        "notes": "Roaming World: 51 lande inkl. USA, Asien m.fl.",
    },
    {
        "operator": "YouSee",
        "subscription": "Mobil M",
        "price_dkk": 219,
        "data_eu_gb": 50,
        "total_countries": 51,
        "roam_zone": "Roaming World",
        "extra_countries": [
            "USA", "Thailand", "Tyrkiet", "Australien", "Canada",
            "Færøerne", "New Zealand", "Hong Kong", "Japan", "Kina",
            "Malaysia", "Singapore",
        ],
        "notes": "Roaming World: 51 lande inkl. USA, Asien m.fl.",
    },
    {
        "operator": "YouSee",
        "subscription": "Mobil L",
        "price_dkk": 249,
        "data_eu_gb": 60,
        "total_countries": 51,
        "roam_zone": "Roaming World",
        "extra_countries": [
            "USA", "Thailand", "Tyrkiet", "Australien", "Canada",
            "Færøerne", "New Zealand", "Hong Kong", "Japan", "Kina",
            "Malaysia", "Singapore",
        ],
        "notes": "Roaming World: 51 lande inkl. USA, Asien m.fl.",
    },
    {
        "operator": "YouSee",
        "subscription": "Fri Data",
        "price_dkk": 299,
        "data_eu_gb": 70,
        "total_countries": 51,
        "roam_zone": "Roaming World",
        "extra_countries": [
            "USA", "Thailand", "Tyrkiet", "Australien", "Canada",
            "Færøerne", "New Zealand", "Hong Kong", "Japan", "Kina",
            "Malaysia", "Singapore",
        ],
        "notes": "Roaming World: 51 lande inkl. USA, Asien m.fl.",
    },

    # ── Norlys (80 destinationer) ─────────────────────────────────────────────
    # Kilde: shop.norlys.dk/kundeservice/mobil/udland/, verificeret marts 2026
    # EU/EØS + 40 ekstra lande inkl. Japan, USA, Asien, Balkan m.fl.
    {
        "operator": "Norlys",
        "subscription": "Mobil S",
        "price_dkk": 139,
        "data_eu_gb": 5,
        "total_countries": 80,
        "roam_zone": "EU/EØS + ekstra",
        "extra_countries": [
            "Albanien", "Andorra", "Australien", "Bangladesh", "Bosnien-Hercegovina",
            "Canada", "Costa Rica", "Egypten", "Fiji", "Filippinerne",
            "Fransk Guyana", "Færøerne", "Hong Kong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mayotte",
            "Mexico", "Moldova", "Montenegro", "Myanmar", "New Zealand",
            "Nordmakedonien", "Pakistan", "Puerto Rico", "Saint-Martin", "San Marino",
            "Serbien", "Singapore", "Sydkorea", "Taiwan", "Thailand",
            "Tyrkiet", "Ukraine", "USA", "Vatikanstaten", "Vietnam",
        ],
        "notes": "80 lande inkluderet i alle abonnementer.",
    },
    {
        "operator": "Norlys",
        "subscription": "Mobil M",
        "price_dkk": 189,
        "data_eu_gb": 15,
        "total_countries": 80,
        "roam_zone": "EU/EØS + ekstra",
        "extra_countries": [
            "Albanien", "Andorra", "Australien", "Bangladesh", "Bosnien-Hercegovina",
            "Canada", "Costa Rica", "Egypten", "Fiji", "Filippinerne",
            "Fransk Guyana", "Færøerne", "Hong Kong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mayotte",
            "Mexico", "Moldova", "Montenegro", "Myanmar", "New Zealand",
            "Nordmakedonien", "Pakistan", "Puerto Rico", "Saint-Martin", "San Marino",
            "Serbien", "Singapore", "Sydkorea", "Taiwan", "Thailand",
            "Tyrkiet", "Ukraine", "USA", "Vatikanstaten", "Vietnam",
        ],
        "notes": "80 lande inkluderet i alle abonnementer.",
    },
    {
        "operator": "Norlys",
        "subscription": "Mobil L",
        "price_dkk": 239,
        "data_eu_gb": 30,
        "total_countries": 80,
        "roam_zone": "EU/EØS + ekstra",
        "extra_countries": [
            "Albanien", "Andorra", "Australien", "Bangladesh", "Bosnien-Hercegovina",
            "Canada", "Costa Rica", "Egypten", "Fiji", "Filippinerne",
            "Fransk Guyana", "Færøerne", "Hong Kong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mayotte",
            "Mexico", "Moldova", "Montenegro", "Myanmar", "New Zealand",
            "Nordmakedonien", "Pakistan", "Puerto Rico", "Saint-Martin", "San Marino",
            "Serbien", "Singapore", "Sydkorea", "Taiwan", "Thailand",
            "Tyrkiet", "Ukraine", "USA", "Vatikanstaten", "Vietnam",
        ],
        "notes": "80 lande inkluderet i alle abonnementer.",
    },
    {
        "operator": "Norlys",
        "subscription": "Mobil XL",
        "price_dkk": 289,
        "data_eu_gb": 50,
        "total_countries": 80,
        "roam_zone": "EU/EØS + ekstra",
        "extra_countries": [
            "Albanien", "Andorra", "Australien", "Bangladesh", "Bosnien-Hercegovina",
            "Canada", "Costa Rica", "Egypten", "Fiji", "Filippinerne",
            "Fransk Guyana", "Færøerne", "Hong Kong", "Indonesien", "Japan",
            "Kina", "Kosovo", "Macao", "Malaysia", "Mayotte",
            "Mexico", "Moldova", "Montenegro", "Myanmar", "New Zealand",
            "Nordmakedonien", "Pakistan", "Puerto Rico", "Saint-Martin", "San Marino",
            "Serbien", "Singapore", "Sydkorea", "Taiwan", "Thailand",
            "Tyrkiet", "Ukraine", "USA", "Vatikanstaten", "Vietnam",
        ],
        "notes": "80 lande inkluderet i alle abonnementer.",
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
    """
    Kør Playwright og hent roaming-data fra alle operatører.
    Bruger operatørspecifikke scrapers for bedre pålidelighed.
    """
    results = []
    _UA = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": _UA})

        scrapers = {
            "Telenor": _scrape_telenor,
            "3":       _scrape_3,
            "Norlys":  _scrape_norlys,
            "YouSee":  _scrape_yousee,
        }

        for operator, scraper_fn in scrapers.items():
            try:
                extra_countries, total_countries = scraper_fn(page)
                log.info(f"  {operator}: {len(extra_countries)} ekstra lande, {total_countries} total")

                for plan in ROAMING_BASELINE:
                    if plan["operator"] == operator:
                        updated = dict(plan)
                        if extra_countries:
                            updated["extra_countries"] = extra_countries
                        if total_countries:
                            updated["total_countries"] = total_countries
                        results.append(updated)

            except Exception as e:
                log.warning(f"  Roaming-fejl for {operator}: {e}")
                results.extend([p for p in ROAMING_BASELINE if p["operator"] == operator])

        browser.close()

    return results if results else []


# ── Operatørspecifikke scrapers ───────────────────────────────────────────────

def _scrape_telenor(page) -> tuple[list[str], int]:
    """
    Henter Telenors landsliste fra modal-siden.
    Kilde: telenor.dk/shop/abonnementer/andet/modal-brug-los-paa-ferien/
    """
    page.goto(ROAMING_URLS["Telenor"], timeout=30000, wait_until="networkidle")
    page.wait_for_timeout(2000)
    text = page.inner_text("body")

    # Find antal lande fra tekst, fx "75 inkluderede lande"
    count_match = re.search(r'(\d{2,3})\s*(?:inkluderede\s*)?lande', text)
    total = int(count_match.group(1)) if count_match else 75

    # Hent listeelementer — landslisten er en <ul>/<ol> på denne side
    raw = page.evaluate("""() => {
        const items = document.querySelectorAll('li');
        return Array.from(items)
            .map(el => el.textContent.trim())
            .filter(t => t.length > 2 && t.length < 50 && !t.includes('\\n'));
    }""")
    all_found = _extract_countries(" ".join(raw) + " " + text)
    extra = [c for c in all_found if c not in EU_EEA_COUNTRIES]
    return extra, total


def _scrape_3(page) -> tuple[list[str], int]:
    """
    Henter 3's landsliste fra udlandssiden.
    Kilde: 3.dk/udland/#landeliste (React-renderet)
    """
    page.goto(ROAMING_URLS["3"], timeout=30000, wait_until="networkidle")
    # Vent på at React har renderet landelisten
    try:
        page.wait_for_selector("#landeliste", timeout=10000)
    except Exception:
        pass
    page.wait_for_timeout(3000)

    # Forsøg at hente tekst fra landelistens sektion
    section_text = page.evaluate("""() => {
        const section = document.querySelector('#landeliste');
        return section ? section.innerText : document.body.innerText;
    }""")
    all_found = _extract_countries(section_text)
    extra = [c for c in all_found if c not in EU_EEA_COUNTRIES]
    return extra, 100


def _scrape_norlys(page) -> tuple[list[str], int]:
    """
    Henter Norlys' landsliste.
    Kilde: shop.norlys.dk/kundeservice/mobil/udland/
    Landene listes efter "Her kan du trygt bruge mobilen".
    """
    page.goto(ROAMING_URLS["Norlys"], timeout=30000, wait_until="networkidle")
    page.wait_for_timeout(2000)
    text = page.inner_text("body")

    # Find afsnittet der indeholder landslisten
    marker = "Her kan du trygt bruge mobilen"
    section = text[text.index(marker):] if marker in text else text

    # Find antal lande fra tekst, fx "80 lande"
    count_match = re.search(r'(\d{2,3})\s*lande', text)
    total = int(count_match.group(1)) if count_match else 80

    all_found = _extract_countries(section)
    extra = [c for c in all_found if c not in EU_EEA_COUNTRIES]
    return extra, total


def _scrape_yousee(page) -> tuple[list[str], int]:
    """
    Henter YouSees landsliste.
    Kilde: yousee.dk/roaming
    Ekstra lande fremgår af FAQ-teksten (30-dages politik).
    """
    page.goto(ROAMING_URLS["YouSee"], timeout=30000, wait_until="networkidle")
    page.wait_for_timeout(2000)
    text = page.inner_text("body")

    # Find antal lande fra tekst, fx "51 lande"
    count_match = re.search(r'(\d{2,3})\s*lande', text)
    total = int(count_match.group(1)) if count_match else 51

    all_found = _extract_countries(text)
    extra = [c for c in all_found if c not in EU_EEA_COUNTRIES]
    return extra, total


# ── Hjælpefunktion: find landenavne i fri tekst ───────────────────────────────

# Alle kendte landenavne vi søger efter i teksten
_ALL_COUNTRIES = EU_EEA_COUNTRIES + [
    "USA", "Canada", "Australien", "New Zealand", "Hongkong", "Hong Kong",
    "Singapore", "Sri Lanka", "Macao", "Macau", "Indonesien", "Israel",
    "Japan", "Sydkorea", "Taiwan", "Filippinerne", "Malaysia", "Vietnam",
    "Thailand", "Kina", "Myanmar", "Cambodja", "Brunei",
    "Albanien", "Bosnien-Hercegovina", "Serbien", "Nordmakedonien",
    "Montenegro", "Kosovo", "Moldova", "Monaco", "San Marino", "Vatikanstaten",
    "Georgien", "Armenien", "Andorra", "Ukraine", "Rusland",
    "Tyrkiet", "Egypten", "Marokko", "Tunesien", "Sydafrika", "Kenya",
    "Nigeria", "Senegal", "Tanzania", "Uganda", "Zambia", "Cameroun",
    "Elfenbenskysten", "Mali", "Seychellerne",
    "Mexico", "Brasilien", "Argentina", "Chile", "Colombia", "Peru",
    "Costa Rica", "Puerto Rico", "Amerikanske Jomfruøer",
    "De Forenede Arabiske Emirater", "Forenede Arabiske Emirater", "Dubai",
    "Israel", "Jordan", "Pakistan", "Indien", "Bangladesh",
    "Færøerne", "Isle of Man", "Kiribati", "Fiji",
    "Fransk Guyana", "Mayotte", "Saint-Martin", "S. Martin", "S. Barthèlemy",
    "Usbekistan",
]


def _extract_countries(text: str) -> list[str]:
    """Find landenavne i fri tekst."""
    found = []
    text_lower = text.lower()
    for country in _ALL_COUNTRIES:
        if country.lower() in text_lower:
            # Normaliser: Hong Kong → Hongkong, Macau → Macao
            normalized = country.replace("Hong Kong", "Hongkong").replace("Macau", "Macao")
            found.append(normalized)
    return list(dict.fromkeys(found))  # bevar rækkefølge, fjern dubletter

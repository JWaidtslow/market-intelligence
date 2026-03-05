"""
Market Intelligence Agent — Data Extractor
Converts raw scraped text into structured subscription/internet/hardware records.
"""

import re
import logging
from typing import Optional

log = logging.getLogger(__name__)

RE_PRICE = re.compile(r"(\d[\d\.\,]+)\s*kr", re.IGNORECASE)
RE_DATA  = re.compile(r"(\d+)\s*(?:GB|gb)", re.IGNORECASE)

PLAN_KEYWORDS = ["fri tale", "abonnement", "pakke", "plan", "timer"]
INTERNET_KEYWORDS = ["internet", "bredbaand", "bredbånd", "wifi", "router", "5g internet", "4g internet"]
DEVICE_BRANDS = ["iphone", "samsung", "galaxy", "pixel", "oneplus"]
STREAMING_SERVICES = [
    "viaplay", "disney+", "disney plus", "netflix", "tv2 play",
    "hbo max", " max ", "deezer", "podimo", "telmore musik", "yousee musik",
    "nordisk film", "sky showtime", "saxo", "wype", "tv 2 play",
]


def extract_subscriptions(text: str, operator_name: str) -> list[dict]:
    """Extract voice subscription plans from raw page text."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    plans = []
    seen_prices = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        prices = RE_PRICE.findall(line)

        if prices and _is_subscription_context(line, lines, i):
            price = _parse_price(prices[0])
            if price and 49 <= price <= 800 and price not in seen_prices:
                seen_prices.add(price)
                ctx_lines = lines[max(0, i-4):i+4]
                ctx = " ".join(ctx_lines)

                plan = _build_subscription_record(ctx, price, operator_name)
                if plan:
                    plans.append(plan)
        i += 1

    return _deduplicate(plans, "price")


def extract_internet(text: str, operator_name: str) -> list[dict]:
    """Extract internet/broadband plans from raw page text."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    plans = []
    seen_prices = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        prices = RE_PRICE.findall(line)

        if prices and _is_internet_context(line, lines, i):
            price = _parse_price(prices[0])
            if price and 49 <= price <= 600 and price not in seen_prices:
                seen_prices.add(price)
                ctx_lines = lines[max(0, i-4):i+4]
                ctx = " ".join(ctx_lines)

                plan = _build_internet_record(ctx, price, operator_name)
                if plan:
                    plans.append(plan)
        i += 1

    return _deduplicate(plans, "price")


def extract_hardware(text: str, operator_name: str) -> list[dict]:
    """Brand-pattern hardware extraction.

    Detects any device by spotting a known brand name on its own line (or at
    the start of a line) and treating the adjacent text as the model name.
    This picks up the full current catalogue without relying on a fixed device
    list that would go stale as new models are released.

    Handles two common layouts used by Danish operators:
      Layout A — brand on its own line, model on the next line:
                   Samsung
                   Galaxy S26 Ultra
                   8.499 kr.
      Layout B — "Brand Model" on a single line:
                   Samsung Galaxy S26 Ultra
                   8.499 kr.
    """
    PHONE_BRANDS = [
        "Apple", "Samsung", "Google", "OnePlus", "Motorola",
        "Nokia", "Xiaomi", "Sony", "Oppo", "Nothing", "Doro",
    ]

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    devices = []
    seen = set()

    for i, line in enumerate(lines):
        brand = None
        model = None
        ctx_start = i

        # Layout A: brand alone on this line, model on the next
        for b in PHONE_BRANDS:
            if line.lower() == b.lower() and i + 1 < len(lines):
                candidate = lines[i + 1]
                # Must not be a price/button line and must be a plausible length
                if not RE_PRICE.search(candidate) and 3 <= len(candidate) <= 60:
                    brand, model, ctx_start = b, candidate, i
                    break

        # Layout B: "Brand Model…" on the same line
        if not brand:
            for b in PHONE_BRANDS:
                if line.lower().startswith(b.lower() + " ") and len(line) > len(b) + 3:
                    brand, model, ctx_start = b, line[len(b):].strip(), i
                    break

        if not brand or not model:
            continue

        # Extract price from the next several lines
        ctx_lines = lines[ctx_start: ctx_start + 8]
        ctx = " ".join(ctx_lines)
        raw_prices = RE_PRICE.findall(ctx)
        device_prices = sorted(set(
            p for p in (_parse_price(x) for x in raw_prices)
            if p and 500 < p < 25_000
        ))

        if not device_prices:
            continue

        full_model = f"{brand} {model}"
        key = (operator_name.lower(), full_model.lower())
        if key in seen:
            continue
        seen.add(key)

        stor_match = re.search(r'(\d+)\s*GB', ctx, re.IGNORECASE)
        stor = f"{stor_match.group(1)}GB" if stor_match else ""

        devices.append({
            "operator": operator_name,
            "model": full_model,
            "storage": stor,
            "price_min": device_prices[0],
            "price_max": device_prices[-1],
            "notes": "",
        })

    return devices


def extract_vas(text: str, operator_name: str) -> list[dict]:
    """Extract value-added services (streaming, insurance, etc.) from page text."""
    text_lower = text.lower()
    services = []

    for service in STREAMING_SERVICES:
        if service in text_lower:
            idx = text_lower.find(service)
            ctx = text[max(0, idx-100):idx+200]
            prices = RE_PRICE.findall(ctx)
            price = _parse_price(prices[0]) if prices else None

            category = _categorise_service(service)
            services.append({
                "operator": operator_name,
                "service": service.title().replace("Tv2", "TV2").replace("Disney+", "Disney+"),
                "category": category,
                "price": price,
                "included": price is None or "inkl" in ctx.lower() or "gratis" in ctx.lower(),
            })

    return services


# ── Record builders ──────────────────────────────────────────────────────────

def _build_subscription_record(ctx: str, price: float, operator: str) -> Optional[dict]:
    ctx_lower = ctx.lower()

    data_match = RE_DATA.search(ctx)
    data_gb = int(data_match.group(1)) if data_match else None
    is_free_data = bool(re.search(r"\bfri\s*(data|gb)\b", ctx_lower))

    talk = "Fri" if "fri tale" in ctx_lower else ("Begrænset" if "timer" in ctx_lower else "Fri")

    coverage = "Verden"
    if "verden" in ctx_lower:
        coverage = "Verden"
    elif "eu" in ctx_lower and "verden" not in ctx_lower:
        coverage = "EU"
    elif "dk" in ctx_lower and "eu" not in ctx_lower:
        coverage = "DK"

    campaign = _extract_campaign(ctx)
    entertainment = _extract_entertainment(ctx_lower)

    # Try to extract a plan name from nearby text
    name = _guess_plan_name(ctx, price, data_gb, is_free_data)

    return {
        "operator": operator,
        "name": name,
        "talk": talk,
        "data_gb": "Fri" if is_free_data else (data_gb or "?"),
        "coverage": coverage,
        "price": price,
        "campaign_price": campaign.get("price"),
        "campaign_duration": campaign.get("duration"),
        "entertainment": entertainment,
        "notes": "",
    }


def _build_internet_record(ctx: str, price: float, operator: str) -> Optional[dict]:
    ctx_lower = ctx.lower()

    data_match = RE_DATA.search(ctx)
    data_gb = int(data_match.group(1)) if data_match else None
    is_unlimited = bool(re.search(r"\b(fri|ubegrænset|∞)\b", ctx_lower))

    internet_type = "Fast trådløs"
    if any(k in ctx_lower for k in ["mobilt", "on the go", "på farten"]):
        internet_type = "Mobilt bredbånd"

    tech = "5G" if "5g" in ctx_lower else ("4G" if "4g" in ctx_lower else "4G")

    campaign = _extract_campaign(ctx)

    return {
        "operator": operator,
        "name": _guess_internet_name(ctx, data_gb, is_unlimited),
        "type": internet_type,
        "tech": tech,
        "data_gb": "Fri" if is_unlimited else (data_gb or "?"),
        "price": price,
        "campaign_price": campaign.get("price"),
        "campaign_duration": campaign.get("duration"),
        "notes": "",
    }



# ── Context classifiers ──────────────────────────────────────────────────────

def _is_subscription_context(line: str, lines: list, idx: int) -> bool:
    ctx = " ".join(lines[max(0, idx-3):idx+3]).lower()
    has_plan = any(k in ctx for k in PLAN_KEYWORDS)
    has_internet = any(k in ctx for k in INTERNET_KEYWORDS)
    has_device = any(b in ctx for b in DEVICE_BRANDS)
    return has_plan and not has_internet and not has_device


def _is_internet_context(line: str, lines: list, idx: int) -> bool:
    ctx = " ".join(lines[max(0, idx-3):idx+3]).lower()
    return any(k in ctx for k in INTERNET_KEYWORDS)


# ── Helper functions ─────────────────────────────────────────────────────────

def _parse_price(raw: str) -> Optional[float]:
    try:
        cleaned = raw.replace(".", "").replace(",", ".")
        val = float(cleaned)
        return val if 10 <= val <= 25_000 else None
    except (ValueError, TypeError):
        return None


def _extract_campaign(ctx: str) -> dict:
    match = re.search(
        r"(\d[\d\.\,]+)\s*kr\.?\s*/?\s*(\d+)\s*(mdr|md|måneder)", ctx, re.IGNORECASE
    )
    if match:
        return {
            "price": _parse_price(match.group(1)),
            "duration": f"{match.group(2)} mdr.",
        }
    return {}


def _extract_entertainment(ctx_lower: str) -> list[str]:
    found = []
    for s in STREAMING_SERVICES:
        if s in ctx_lower:
            found.append(s.title().replace("Tv2", "TV2").replace("Disney+", "Disney+"))
    return list(dict.fromkeys(found))


def _guess_plan_name(ctx: str, price: float, data_gb, is_free_data: bool) -> str:
    # Look for common name patterns
    match = re.search(r"(fri tale\s*[\w\s\+]+)", ctx, re.IGNORECASE)
    if match:
        return match.group(1).strip()[:50]
    data_str = "Fri GB" if is_free_data else (f"{data_gb}GB" if data_gb else "?")
    return f"Fri Tale {data_str}"


def _guess_internet_name(ctx: str, data_gb, is_unlimited: bool) -> str:
    match = re.search(r"((?:5G|4G)\s*internet[\w\s]*)", ctx, re.IGNORECASE)
    if match:
        return match.group(1).strip()[:50]
    data_str = "Fri" if is_unlimited else (f"{data_gb}GB" if data_gb else "?")
    return f"Internet {data_str}"


def _categorise_service(service: str) -> str:
    music = ["deezer", "musik", "spotify"]
    books = ["saxo", "wype", "mofibo"]
    if any(m in service for m in music):
        return "Musik"
    if any(b in service for b in books):
        return "Bøger/magasiner"
    return "Streaming"


def _deduplicate(records: list, key: str) -> list:
    seen = set()
    out = []
    for r in records:
        val = r.get(key)
        if val not in seen:
            seen.add(val)
            out.append(r)
    return out

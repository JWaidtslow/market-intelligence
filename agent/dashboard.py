"""
Market Intelligence Agent — HTML Dashboard Generator
Produces a single self-contained HTML file with Chart.js visualisations,
filterable tables, and campaign highlights.
"""

import json
import re
import sys
import os
from datetime import datetime

# EU/EØS-antal til roaming-total (importeres fra roaming_scraper hvis muligt)
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from roaming_scraper import EU_EEA_COUNTRIES as _EU_EEA
    _EU_EEA_COUNT = len(_EU_EEA)
except Exception:
    _EU_EEA_COUNT = 40  # fallback


OWN_BRANDS = {"3", "OiSTER", "Flexii"}
OPERATOR_COLORS = {
    "3":       "#FF6200",   # Orange
    "OiSTER":  "#7C3AED",   # Lilla
    "Flexii":  "#60A5FA",   # Baby blå
    "Telenor": "#1D4ED8",   # Blå
    "YouSee":  "#16A34A",   # Grøn
    "Norlys":  "#DC2626",   # Rød
    "CBB":     "#D97706",   # Gul
    "Telmore": "#EC4899",   # Pink
    "Eesy":    "#0891B2",   # Turkis
    "CallMe":  "#9F1239",   # Ruby rød
}
OPERATOR_DOMAINS = {
    "3":       "3.dk",
    "OiSTER":  "oister.dk",
    "Flexii":  "flexii.dk",
    "Telenor": "telenor.dk",
    "YouSee":  "yousee.dk",
    "Norlys":  "norlys.dk",
    "CBB":     "cbb.dk",
    "Telmore": "telmore.dk",
    "Eesy":    "eesy.dk",
    "CallMe":  "callme.dk",
}


def generate_dashboard(data: dict, output_path: str, trends: dict = None):
    """Render and write the interactive HTML dashboard."""
    html = _build_html(data, trends or {})
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard saved: {output_path}")


def _build_html(data: dict, trends: dict = None) -> str:
    trends = trends or {}
    scraped_at = data.get("scraped_at", datetime.now().isoformat())
    week = data.get("week", "?")
    year = data.get("year", datetime.now().year)
    operators = data.get("operators", {})

    # Flatten data into lists per category
    all_subs     = [s for op in operators.values() for s in op.get("subscriptions", [])]
    all_internet = [s for op in operators.values() for s in op.get("internet", [])]
    all_vas      = [s for op in operators.values() for s in op.get("vas", [])]
    all_hardware = [s for op in operators.values() for s in op.get("hardware", [])]
    all_news     = data.get("news", [])
    all_roaming  = data.get("roaming", [])

    op_names = sorted(operators.keys(), key=lambda k: (operators[k].get("name", k) not in OWN_BRANDS, operators[k].get("name", k)))
    op_display_names = [operators[k].get("name", k) for k in op_names]

    # Segment plan keywords (Børn/Ung)
    _segment_keywords = ("børn", "ung", "barn", "junior", "child", "kids")
    def _is_segment(name): return any(k in name.lower() for k in _segment_keywords)

    # Chart data: cheapest subscription — ALL plans (incl. Børn/Ung)
    cheapest_subs_all   = {}
    cheapest_subs_all_names = {}
    # Chart data: cheapest subscription — standard plans only (excl. Børn/Ung)
    cheapest_subs_std   = {}
    cheapest_subs_std_names = {}
    for s in all_subs:
        op   = s.get("operator", "")
        p    = s.get("price", 9999)
        name = s.get("name", "")
        if not isinstance(p, (int, float)):
            continue
        # All plans
        if op not in cheapest_subs_all or p < cheapest_subs_all[op]:
            cheapest_subs_all[op]       = p
            cheapest_subs_all_names[op] = name
        # Standard plans only
        if not _is_segment(name):
            if op not in cheapest_subs_std or p < cheapest_subs_std[op]:
                cheapest_subs_std[op]       = p
                cheapest_subs_std_names[op] = name

    # Use std as default (same key set, fall back to all if no std plan exists)
    cheapest_subs = cheapest_subs_std or cheapest_subs_all

    # Embed both datasets
    def _chart_json(d, names):
        ops = list(d.keys())
        return (json.dumps(ops),
                json.dumps(list(d.values())),
                json.dumps([OPERATOR_COLORS.get(k, "#888") for k in ops]),
                json.dumps([names.get(k, "") for k in ops]))

    chart_labels, chart_values, chart_colors, chart_names = _chart_json(cheapest_subs_std or cheapest_subs_all, cheapest_subs_std_names or cheapest_subs_all_names)
    chart_labels_all, chart_values_all, chart_colors_all, chart_names_all = _chart_json(cheapest_subs_all, cheapest_subs_all_names)

    # Chart data: cheapest internet plan per operator (track name for tooltip)
    cheapest_int = {}
    cheapest_int_names = {}
    for s in all_internet:
        op   = s.get("operator", "")
        p    = s.get("price", 9999)
        name = s.get("name", "")
        if isinstance(p, (int, float)) and (op not in cheapest_int or p < cheapest_int[op]):
            cheapest_int[op]       = p
            cheapest_int_names[op] = name

    int_chart_labels = json.dumps(list(cheapest_int.keys()))
    int_chart_values = json.dumps(list(cheapest_int.values()))
    int_chart_colors = json.dumps([OPERATOR_COLORS.get(k, "#888") for k in cheapest_int.keys()])
    int_chart_names  = json.dumps([cheapest_int_names.get(k, "") for k in cheapest_int.keys()])

    # Summary counters
    active_campaigns = sum(1 for s in all_subs if s.get("campaign_price") is not None)
    operators_count  = len([op for op in operators if operators[op].get("subscriptions")])

    def op_badge(op_name):
        own = op_name in OWN_BRANDS
        color = OPERATOR_COLORS.get(op_name, "#666")
        domain = OPERATOR_DOMAINS.get(op_name, "")
        logo = (f'<img src="https://www.google.com/s2/favicons?domain={domain}&sz=32" '
                f'style="width:16px;height:16px;vertical-align:middle;margin-right:5px;'
                f'border-radius:3px;" onerror="this.style.display=\'none\'">'
                if domain else "")
        ring = ' style="outline: 2px solid gold; outline-offset:2px;"' if own else ""
        return f'<span class="op-badge"{ring} style="background:{color}20;color:{color};border:1px solid {color}40;">{logo}{op_name}{"★" if own else ""}</span>'

    def _six_month_cost(price, camp_p, camp_d):
        """Minimum total cost over 6-month binding period."""
        if not isinstance(price, (int, float)):
            return None
        if isinstance(camp_p, (int, float)):
            m = re.search(r'(\d+)', str(camp_d)) if camp_d else None
            intro = min(int(m.group(1)) if m else 0, 6)
            return int(intro * camp_p + (6 - intro) * price)
        return int(6 * price)

    def change_indicator(delta):
        """Render a price change arrow. delta > 0 = increase (bad/red), < 0 = decrease (good/green)."""
        if delta is None or delta == 0:
            return ""
        if delta > 0:
            return f'<span class="price-up">↑ +{int(delta)} kr.</span>'
        return f'<span class="price-down">↓ {int(abs(delta))} kr.</span>'

    def campaign_badge(price, duration):
        if price is None:
            return ""
        dur = f" / {duration}" if duration else ""
        return f'<span class="camp-badge">🏷 {int(price) if isinstance(price, float) and price == int(price) else price} kr{dur}</span>'

    def entertainment_badges(ent_list):
        if not ent_list:
            return '<span style="color:#aaa">—</span>'
        return " ".join(f'<span class="ent-badge">{e}</span>' for e in ent_list)

    def price_cell(p, delta=None):
        if p is None or p == "":
            return '<td class="price-cell">—</td>'
        fmt = int(p) if isinstance(p, float) and p == int(p) else p
        chg = f' {change_indicator(delta)}' if delta is not None and delta != 0 else ""
        return f'<td class="price-cell"><strong>{fmt} kr.</strong>{chg}</td>'

    # ── Subscriptions table rows ─────────────────────────────────────────────
    sub_rows = ""
    for s in sorted(all_subs, key=lambda x: (x.get("operator",""), x.get("price", 9999))):
        op   = s.get("operator", "")
        name = s.get("name", "")
        data_gb = s.get("data_gb", "?")
        data_str = "Fri" if data_gb == "Fri" else (f"{data_gb} GB" if isinstance(data_gb, (int, float)) else str(data_gb))
        talk = s.get("talk", "Fri")
        cov  = s.get("coverage", "")
        price= s.get("price", "")
        camp_p = s.get("campaign_price")
        camp_d = s.get("campaign_duration")
        ent    = s.get("entertainment", [])
        notes  = s.get("notes", "")
        delta  = s.get("price_change")
        is_new = s.get("price_new", False)
        own    = op in OWN_BRANDS

        new_tag = ' <span class="new-badge">NY</span>' if is_new else ""
        sub_rows += f"""
        <tr class="data-row" data-operator="{op}" {"data-own='1'" if own else ""}>
          <td>{op_badge(op)}</td>
          <td>{name}{new_tag}</td>
          <td class="center">{talk}</td>
          <td class="center">{data_str}</td>
          <td class="center">{cov}</td>
          {price_cell(price, delta)}
          <td>{campaign_badge(camp_p, camp_d)}</td>
          <td>{entertainment_badges(ent)}</td>
          <td class="notes">{notes}</td>
        </tr>"""

    # ── Internet table rows ──────────────────────────────────────────────────
    int_rows = ""
    for s in sorted(all_internet, key=lambda x: (x.get("operator",""), x.get("price", 9999))):
        op   = s.get("operator", "")
        name = s.get("name", "")
        itype= s.get("type", "")
        tech = s.get("tech", "")
        data_gb = s.get("data_gb", "?")
        data_str = "Fri" if data_gb == "Fri" else (f"{data_gb} GB" if isinstance(data_gb, (int, float)) else str(data_gb))
        price= s.get("price", "")
        camp_p = s.get("campaign_price")
        camp_d = s.get("campaign_duration")
        notes  = s.get("notes", "")
        delta  = s.get("price_change")
        is_new = s.get("price_new", False)
        own    = op in OWN_BRANDS

        new_tag = ' <span class="new-badge">NY</span>' if is_new else ""
        scraped_min = s.get("min_price")
        six_mo = scraped_min if scraped_min else _six_month_cost(price, camp_p, camp_d)
        src_note = '' if scraped_min else '<span title="Beregnet: intro × kampagnepris + rest × standardpris" style="font-size:0.7rem;color:var(--text-muted);margin-left:3px">~</span>'
        min_price_cell = f'<td class="price-cell"><strong>{int(six_mo)} kr.</strong>{src_note}</td>' if six_mo is not None else '<td class="price-cell">—</td>'
        dur_str = f'<span style="font-size:0.75rem;color:var(--text-muted)">{camp_d}</span>' if camp_d else ''
        int_rows += f"""
        <tr class="data-row" data-operator="{op}" {"data-own='1'" if own else ""}>
          <td>{op_badge(op)}</td>
          <td>{name}{new_tag}</td>
          <td class="center">{itype}</td>
          <td class="center"><span class="tech-badge tech-{tech.lower()}">{tech}</span></td>
          <td class="center">{data_str}</td>
          {min_price_cell}
          {price_cell(price, delta)}
          <td class="center">{dur_str}</td>
          <td class="notes">{notes}</td>
        </tr>"""

    # ── VAS table rows ───────────────────────────────────────────────────────
    vas_rows = ""
    for s in sorted(all_vas, key=lambda x: (x.get("category",""), x.get("service",""))):
        op   = s.get("operator", "")
        svc  = s.get("service", "")
        cat  = s.get("category", "")
        incl = s.get("included", False)
        own  = op in OWN_BRANDS
        incl_badge = '<span class="incl-badge">Inkluderet</span>' if incl else '<span class="avail-badge">Tilgængelig</span>'

        vas_rows += f"""
        <tr class="data-row" data-operator="{op}">
          <td>{op_badge(op)}</td>
          <td>{svc}</td>
          <td class="center">{cat}</td>
          <td class="center">{incl_badge}</td>
        </tr>"""

    # ── Hardware table rows ──────────────────────────────────────────────────
    hw_rows = ""
    for s in sorted(all_hardware, key=lambda x: (x.get("operator",""), x.get("model",""))):
        op   = s.get("operator", "")
        model= s.get("model", "")
        stor = s.get("storage", "")
        pmin = s.get("price_min")
        pmax = s.get("price_max")
        notes= s.get("notes", "")
        own  = op in OWN_BRANDS

        hw_rows += f"""
        <tr class="data-row" data-operator="{op}">
          <td>{op_badge(op)}</td>
          <td>{model}</td>
          <td class="center">{stor}</td>
          {price_cell(pmin)}
          {price_cell(pmax)}
          <td class="notes">{notes}</td>
        </tr>"""

    if not hw_rows:
        hw_rows = '<tr><td colspan="6" style="text-align:center;color:#888;padding:2rem;">Hardware-data scraped ved næste kørsel</td></tr>'

    # ── Roaming section ──────────────────────────────────────────────────────
    # Find alle unikke ekstra-lande og tæl hvor mange operatører der har dem
    from collections import Counter
    extra_country_ops: dict[str, list] = {}
    for plan in all_roaming:
        op = plan.get("operator", "")
        for country in plan.get("extra_countries", []):
            extra_country_ops.setdefault(country, [])
            if op not in extra_country_ops[country]:
                extra_country_ops[country].append(op)

    # Et land er "unikt" hvis kun én operatør tilbyder det
    unique_countries = {c for c, ops in extra_country_ops.items() if len(ops) == 1}

    def roaming_country_badge(country: str, operator: str) -> str:
        color = OPERATOR_COLORS.get(operator, "#888")
        if country in unique_countries:
            return (f'<span class="roam-country unique" '
                    f'style="background:{color}22;border-color:{color};color:{color}" '
                    f'title="Kun {operator}">{country}</span>')
        return f'<span class="roam-country">{country}</span>'

    roaming_rows = ""
    roaming_filter_ops = sorted({p["operator"] for p in all_roaming})
    for plan in all_roaming:
        op       = plan.get("operator", "")
        sub      = plan.get("subscription", "")
        price    = plan.get("price_dkk", "")
        data_gb  = plan.get("data_eu_gb", "")
        zone     = plan.get("roam_zone", "EU/EØS")
        extras   = plan.get("extra_countries", [])
        notes    = plan.get("notes", "")
        color    = OPERATOR_COLORS.get(op, "#888")

        data_str  = "Ubegrænset" if data_gb == 999 else (f"{data_gb} GB" if data_gb else "—")
        price_str = f"{price} kr/md" if price else "—"
        total_countries = plan.get("total_countries", _EU_EEA_COUNT + len(extras))

        extra_html = " ".join(roaming_country_badge(c, op) for c in extras) if extras else '<span style="color:var(--text-muted);font-size:0.8rem">Kun EU/EØS</span>'

        roaming_rows += f"""
        <tr class="data-row" data-operator="{op}">
          <td>{op_badge(op)}</td>
          <td style="font-weight:600">{sub}</td>
          <td style="color:{color};font-weight:700">{price_str}</td>
          <td style="text-align:center">{data_str}</td>
          <td style="text-align:center;font-weight:700;font-size:1rem">{total_countries}</td>
          <td><span class="roam-zone-badge">{zone}</span></td>
          <td class="roam-countries-cell">{extra_html}</td>
        </tr>"""

    if not roaming_rows:
        roaming_rows = '<tr><td colspan="7" style="text-align:center;color:#888;padding:2rem">Roaming-data hentes ved næste kørsel</td></tr>'

    # Filter-knapper til roaming (kun de 4 operatører)
    roaming_filter_btns = '<button class="filter-btn active" data-filter="all">Alle</button>'
    for op in roaming_filter_ops:
        color = OPERATOR_COLORS.get(op, "#888")
        roaming_filter_btns += f'<button class="filter-btn" data-filter="{op}" style="--op-color:{color}">{op}</button>'

    # ── Newsroom cards ───────────────────────────────────────────────────────
    news_cards = ""
    for article in all_news:
        op      = article.get("operator", "")
        headline = article.get("headline", "").replace('"', '&quot;')
        url     = article.get("url", "#")
        pub     = article.get("published", "")
        source  = article.get("source", "")
        color   = OPERATOR_COLORS.get(op, "#888")
        news_cards += f"""
        <div class="news-card" data-operator="{op}">
          <div class="news-meta">
            {op_badge(op)}
            <span class="news-date">{pub}</span>
            <span class="news-source">{source}</span>
          </div>
          <a href="{url}" target="_blank" rel="noopener">{headline}</a>
        </div>"""

    if not news_cards:
        news_cards = '<p style="color:var(--text-muted);padding:2rem 0;text-align:center;">Nyheder hentes ved næste kørsel</p>'

    # ── News pill badges (top 5, for header bar) ─────────────────────────────
    news_pills_html = ""
    for article in all_news[:5]:
        op       = article.get("operator", "")
        headline = article.get("headline", "")
        color    = OPERATOR_COLORS.get(op, "#888")
        label    = f"{op}: {headline}"
        if len(label) > 50:
            label = label[:47] + "…"
        op_esc = op.replace("'", "\\'")
        hl_esc = headline.replace('"', '&quot;')
        news_pills_html += (
            f'<button class="news-pill" style="--pill-color:{color}" '
            f'onclick="goToNewsroom(\'{op_esc}\')" title="{hl_esc}">{label}</button>'
        )
    if not news_pills_html:
        news_pills_html = '<span style="color:var(--text-muted);font-size:0.8rem">Nyheder hentes ved næste kørsel</span>'

    # ── Internet KPI data (4 charts) ─────────────────────────────────────────
    def _months(dur):
        m = re.search(r'(\d+)', str(dur)) if dur else None
        return int(m.group(1)) if m else 0

    int_kpi = {}
    for s in all_internet:
        op = s.get("operator", "")
        p  = s.get("price")
        cp = s.get("campaign_price")
        cd = s.get("campaign_duration", "")
        if op not in int_kpi:
            int_kpi[op] = {"min_price": None, "min_camp": None, "max_months": 0, "min_after_intro": None}
        if isinstance(p, (int, float)):
            int_kpi[op]["min_price"] = min(filter(None, [int_kpi[op]["min_price"], p]))
        if isinstance(cp, (int, float)):
            int_kpi[op]["min_camp"] = min(filter(None, [int_kpi[op]["min_camp"], cp]))
            # min_after_intro = normal price of plans that also have a campaign price
            if isinstance(p, (int, float)):
                int_kpi[op]["min_after_intro"] = min(filter(None, [int_kpi[op]["min_after_intro"], p]))
        mo = _months(cd)
        if mo > int_kpi[op]["max_months"]:
            int_kpi[op]["max_months"] = mo

    kpi_ops    = list(int_kpi.keys())
    kpi_colors = json.dumps([OPERATOR_COLORS.get(k, "#888") for k in kpi_ops])
    kpi_labels = json.dumps(kpi_ops)
    kpi_min_price      = json.dumps([int_kpi[k]["min_price"]      or 0 for k in kpi_ops])
    kpi_min_camp       = json.dumps([int_kpi[k]["min_camp"]       or 0 for k in kpi_ops])
    kpi_max_months     = json.dumps([int_kpi[k]["max_months"]         for k in kpi_ops])
    kpi_min_after      = json.dumps([int_kpi[k]["min_after_intro"] or 0 for k in kpi_ops])

    # ── Trend JSON (embedded in HTML) ────────────────────────────────────────
    trend_json = json.dumps(trends)

    # ── Subscription trend quick-data (cheapest normal price per operator/week)
    sub_trend = trends.get("subscriptions", {"dates": [], "operators": {}})
    int_trend = trends.get("internet",      {"dates": [], "operators": {}})
    has_trend = len(sub_trend.get("dates", [])) >= 2

    # ── Operator filter buttons ──────────────────────────────────────────────
    filter_btns = '<button class="filter-btn active" data-filter="all">Alle</button>'
    for op_key in op_names:
        name = operators[op_key].get("name", op_key)
        color = OPERATOR_COLORS.get(name, "#666")
        own = name in OWN_BRANDS
        star = "★ " if own else ""
        filter_btns += f'<button class="filter-btn" data-filter="{name}" style="--op-color:{color}">{star}{name}</button>'

    return f"""<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Konkurrentovervågning — Uge {week} {year}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: #F4F5F9;
      --surface: #FFFFFF;
      --surface2: #EEF0F8;
      --border: #DDE0EC;
      --text: #1A1D2E;
      --text-muted: #6B7285;
      --accent: #FF5400;
      --accent2: #E1001A;
      --own: #E1001A;
      --camp: #FF5400;
      --radius: 10px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; }}

    /* Layout */
    .layout {{ display: flex; min-height: 100vh; }}
    .sidebar {{ width: 220px; background: var(--surface); border-right: 1px solid var(--border); border-top: 3px solid var(--accent); padding: 1.5rem 1rem; display: flex; flex-direction: column; gap: 1.5rem; position: sticky; top: 0; height: 100vh; overflow-y: auto; box-shadow: 2px 0 8px rgba(0,0,0,0.06); }}
    .main {{ flex: 1; padding: 2rem; overflow-x: hidden; }}

    /* Sidebar */
    .brand {{ font-size: 1.1rem; font-weight: 700; color: var(--text); }}
    .brand span {{ color: var(--accent); }}
    .week-badge {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 0.4rem 0.7rem; font-size: 0.75rem; color: var(--text-muted); }}
    .nav-section label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 0.5rem; display: block; }}
    .nav-btn {{ display: block; width: 100%; text-align: left; background: none; border: none; color: var(--text-muted); padding: 0.5rem 0.7rem; border-radius: 6px; cursor: pointer; font-size: 0.875rem; transition: all 0.15s; }}
    .nav-btn:hover {{ background: var(--surface2); color: var(--text); }}
    .nav-btn.active {{ background: var(--accent)20; color: var(--accent); border-left: 3px solid var(--accent); }}
    .own-note {{ background: var(--own)15; border: 1px solid var(--own)40; border-radius: 6px; padding: 0.6rem; font-size: 0.75rem; color: var(--own); }}

    /* Tabs / Sections */
    .section {{ display: none; }}
    .section.active {{ display: block; }}

    /* Page header */
    .page-header {{ margin-bottom: 1.5rem; }}
    .page-header h1 {{ font-size: 1.5rem; font-weight: 700; }}
    .page-header p {{ color: var(--text-muted); margin-top: 0.25rem; font-size: 0.85rem; }}

    /* Summary cards */
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .card-value {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
    .card-label {{ font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.05em; }}

    /* Chart */
    .chart-wrap {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .chart-wrap h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: var(--text); }}
    .chart-container {{ position: relative; height: 260px; }}

    /* Filters */
    .filters {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem; align-items: center; }}
    .filter-btn {{ background: var(--surface); border: 1px solid var(--border); color: var(--text-muted); padding: 0.35rem 0.8rem; border-radius: 20px; cursor: pointer; font-size: 0.8rem; transition: all 0.15s; }}
    .filter-btn:hover {{ border-color: var(--op-color, var(--accent)); color: var(--text); }}
    .filter-btn.active {{ background: var(--op-color, var(--accent))25; border-color: var(--op-color, var(--accent)); color: var(--op-color, var(--accent)); font-weight: 600; }}
    .search-input {{ margin-left: auto; background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.8rem; outline: none; }}
    .search-input:focus {{ border-color: var(--accent); }}

    /* Table */
    .table-wrap {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: var(--surface2); color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; padding: 0.75rem 1rem; text-align: left; font-weight: 600; cursor: pointer; user-select: none; white-space: nowrap; }}
    th:hover {{ color: var(--text); }}
    td {{ padding: 0.65rem 1rem; border-top: 1px solid var(--border); vertical-align: middle; }}
    tr.data-row:hover td {{ background: var(--surface2); }}
    tr[data-own="1"] td:first-child {{ border-left: 3px solid var(--own); }}
    .center {{ text-align: center; }}
    .price-cell {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .notes {{ color: var(--text-muted); font-size: 0.8rem; max-width: 200px; }}

    /* Badges */
    .op-badge {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.78rem; font-weight: 600; white-space: nowrap; }}
    .camp-badge {{ display: inline-block; background: var(--camp)20; color: var(--camp); border: 1px solid var(--camp)40; border-radius: 4px; padding: 0.2rem 0.5rem; font-size: 0.75rem; white-space: nowrap; }}
    .ent-badge {{ display: inline-block; background: #FF540015; color: #CC4400; border-radius: 3px; padding: 0.15rem 0.4rem; font-size: 0.7rem; margin: 0.1rem; white-space: nowrap; }}
    .incl-badge {{ background: #00a65025; color: #00a650; border: 1px solid #00a65040; border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; }}
    .avail-badge {{ background: #6B728520; color: #6B7285; border: 1px solid #6B728540; border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; }}
    .tech-badge {{ display: inline-block; border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; font-weight: 600; }}
    .tech-5g {{ background: #00a65020; color: #00a650; }}
    .tech-4g {{ background: #0072c620; color: #0072c6; }}
    .tech-fiber {{ background: #7c3aed20; color: #a78bfa; }}

    /* Price change indicators */
    .price-up   {{ color: #ff4c4c; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }}
    .price-down {{ color: #2ecc71; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }}
    .new-badge  {{ background: #FF540018; color: #FF5400; border: 1px solid #FF540040; border-radius: 3px; padding: 0.1rem 0.35rem; font-size: 0.65rem; font-weight: 700; vertical-align: middle; }}

    /* Hidden rows */
    tr.hidden {{ display: none; }}

    /* Global search */
    .global-search-wrap {{ display: flex; align-items: center; gap: 0.6rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.6rem 1rem; margin-bottom: 1.5rem; transition: border-color 0.15s; }}
    .global-search-wrap:focus-within {{ border-color: var(--accent); }}
    .search-icon {{ font-size: 1.2rem; color: var(--text-muted); }}
    .global-search {{ flex: 1; background: none; border: none; color: var(--text); font-size: 0.9rem; outline: none; }}
    .global-search::placeholder {{ color: var(--text-muted); }}
    .search-kbd {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 4px; padding: 0.1rem 0.4rem; font-size: 0.7rem; color: var(--text-muted); white-space: nowrap; }}

    /* KPI 2×2 grid */
    .kpi-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }}
    .kpi-grid .chart-container {{ height: 200px; }}

    /* Trend note */
    .trend-note {{ font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem; text-align: center; }}

    /* Window selector */
    .window-select {{ display: flex; gap: 0.5rem; align-items: center; margin-left: auto; }}
    .window-select span {{ font-size: 0.75rem; color: var(--text-muted); }}
    .window-select select {{ background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 0.3rem 0.6rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; outline: none; transition: border-color 0.15s; }}
    .window-select select:hover, .window-select select:focus {{ border-color: var(--accent); }}

    /* Chart toggle */
    .chart-toggle {{ display: flex; gap: 0.4rem; flex-shrink: 0; }}
    .toggle-btn {{ background: var(--surface2); border: 1px solid var(--border); color: var(--text-muted); padding: 0.35rem 0.8rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: all 0.15s; white-space: nowrap; }}
    .toggle-btn:hover {{ color: var(--text); border-color: var(--accent); }}
    .toggle-btn.active {{ background: var(--accent)25; border-color: var(--accent); color: var(--accent); font-weight: 600; }}

    /* Newsroom */
    .news-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; margin-top: 1.25rem; }}
    .news-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.1rem 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 0.5rem; transition: box-shadow 0.15s, border-color 0.15s; }}
    .news-card:hover {{ box-shadow: 0 3px 12px rgba(0,0,0,0.1); border-color: var(--accent); }}
    .news-card a {{ text-decoration: none; color: var(--text); font-weight: 600; font-size: 0.9rem; line-height: 1.4; }}
    .news-card a:hover {{ color: var(--accent); }}
    .news-meta {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
    .news-date {{ font-size: 0.72rem; color: var(--text-muted); }}
    .news-source {{ font-size: 0.72rem; color: var(--text-muted); background: var(--surface2); border-radius: 3px; padding: 0.1rem 0.4rem; }}
    .news-card.hidden {{ display: none; }}

    /* Roaming */
    .roam-countries-cell {{ max-width: 520px; }}
    .roam-country {{ display: inline-block; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 4px; margin: 0.15rem 0.2rem 0.15rem 0; background: var(--surface2); border: 1px solid var(--border); color: var(--text-muted); white-space: nowrap; }}
    .roam-country.unique {{ font-weight: 700; border-width: 1.5px; }}
    .roam-zone-badge {{ display: inline-block; font-size: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 20px; background: var(--surface2); border: 1px solid var(--border); color: var(--text); white-space: nowrap; }}
    .roam-legend {{ display: flex; align-items: center; gap: 0.4rem; font-size: 0.78rem; color: var(--text-muted); margin-bottom: 1rem; }}
    .roam-legend-dot {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; }}

    /* News pills bar */
    .news-pills-bar {{ display: flex; align-items: center; gap: 0.75rem; padding: 0.55rem 1.25rem; background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 50; }}
    .news-pills-label {{ font-size: 0.68rem; font-weight: 700; color: var(--accent); letter-spacing: 0.07em; white-space: nowrap; text-transform: uppercase; }}
    .news-pills-scroll {{ display: flex; gap: 0.45rem; overflow-x: auto; scrollbar-width: none; -ms-overflow-style: none; flex: 1; }}
    .news-pills-scroll::-webkit-scrollbar {{ display: none; }}
    .news-pill {{ background: var(--pill-color, #888)18; border: 1px solid var(--pill-color, #888)45; color: var(--pill-color, #444); padding: 0.28rem 0.7rem; border-radius: 20px; font-size: 0.77rem; white-space: nowrap; cursor: pointer; transition: all 0.15s; font-family: inherit; }}
    .news-pill:hover {{ background: var(--pill-color, #888)30; transform: translateY(-1px); box-shadow: 0 2px 8px var(--pill-color, #888)30; }}

    /* Responsive */
    @media (max-width: 768px) {{
      .sidebar {{ display: none; }}
      .main {{ padding: 1rem; }}
      .kpi-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<div class="layout">

  <!-- Sidebar -->
  <nav class="sidebar">
    <div>
      <div class="brand">Market<span>Intel</span></div>
      <div class="week-badge" style="margin-top:.5rem">Uge {week} · {year}</div>
    </div>

    <div class="nav-section">
      <label>Sektioner</label>
      <button class="nav-btn active" onclick="showSection('overview')">📊 Overblik</button>
      <button class="nav-btn" onclick="showSection('subscriptions')">📱 Abonnementer</button>
      <button class="nav-btn" onclick="showSection('internet')">🌐 Internet</button>
      <button class="nav-btn" onclick="showSection('hardware')">📲 Hardware</button>
      <button class="nav-btn" onclick="showSection('vas')">🎬 VAS</button>
      <button class="nav-btn" onclick="showSection('roaming')">🌍 Roaming</button>
      <button class="nav-btn" onclick="showSection('newsroom')">📰 Newsroom</button>
    </div>

    <div class="own-note">★ Markeret = egne brands<br>(3, OiSTER, Flexii)</div>

    <div style="margin-top:auto;color:var(--text-muted);font-size:0.7rem">
      Opdateret:<br>{scraped_at[:16].replace("T", " ")}
    </div>
  </nav>

  <!-- Main content -->
  <main class="main">

    <!-- ══ NEWS PILLS BAR ════════════════════════════════════════════════════ -->
    <div class="news-pills-bar">
      <span class="news-pills-label">📰 Nyheder</span>
      <div class="news-pills-scroll">
        {news_pills_html}
      </div>
    </div>

    <!-- ══ GLOBAL SEARCH ══════════════════════════════════════════════════════ -->
    <div class="global-search-wrap">
      <span class="search-icon">⌕</span>
      <input id="global-search" class="global-search" type="text"
             placeholder="Søg på tværs af alle data… (Ctrl+K)"
             oninput="globalSearch(this.value)">
      <kbd class="search-kbd">Ctrl K</kbd>
    </div>

    <!-- ══ OVERVIEW ══════════════════════════════════════════════════════════ -->
    <div id="section-overview" class="section active">
      <div class="page-header">
        <h1>Konkurrentovervågning — Uge {week} {year}</h1>
        <p>Dansk telco-marked · {len(operators)} operatører overvåget · {active_campaigns} aktive kampagner</p>
      </div>

      <div class="cards">
        <div class="card">
          <div class="card-value">{operators_count}</div>
          <div class="card-label">Operatører</div>
        </div>
        <div class="card">
          <div class="card-value">{len(all_subs)}</div>
          <div class="card-label">Abonnementer</div>
        </div>
        <div class="card">
          <div class="card-value">{active_campaigns}</div>
          <div class="card-label">Aktive kampagner</div>
        </div>
        <div class="card">
          <div class="card-value">{len(all_internet)}</div>
          <div class="card-label">Internetprodukter</div>
        </div>
      </div>

      <div class="chart-wrap">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;gap:1rem;flex-wrap:wrap">
          <h2 id="cheapest-title" style="margin-bottom:0">Billigste abonnement pr. operatør (kr./md.)</h2>
          <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap">
            <div class="chart-toggle" id="type-toggle">
              <button class="toggle-btn active" onclick="switchCheapestChart('subs',this)">📱 Mobilabonnement</button>
              <button class="toggle-btn" onclick="switchCheapestChart('internet',this)">🌐 Internet</button>
            </div>
            <div class="chart-toggle" id="segment-toggle" style="border-left:1px solid var(--border);padding-left:0.5rem">
              <button class="toggle-btn active" id="seg-off-btn" onclick="setSegment(false,this)">Ekskl. Børn/Ung</button>
              <button class="toggle-btn" id="seg-on-btn" onclick="setSegment(true,this)">Inkl. Børn/Ung</button>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="cheapestChart"></canvas>
        </div>
      </div>

      <div class="chart-wrap">
        <h2>Kampagneoverblik — abonnementspriser</h2>
        <div class="chart-container">
          <canvas id="campaignChart"></canvas>
        </div>
      </div>
    </div>

    <!-- ══ SUBSCRIPTIONS ═════════════════════════════════════════════════════ -->
    <div id="section-subscriptions" class="section">
      <div class="page-header">
        <h1>Abonnementer</h1>
        <p>Voice-abonnementer på tværs af operatører</p>
      </div>
      <div class="chart-wrap" id="sub-trend-wrap">
        <div style="display:flex;align-items:center;margin-bottom:1rem">
          <h2 style="margin-bottom:0">Prisudvikling — billigste abonnement pr. operatør</h2>
          <div class="window-select">
            <span>Periode:</span>
            <select onchange="setTrendWindow(+this.value,'sub')">
              <option value="1">Seneste uge</option>
              <option value="4">Seneste måned</option>
              <option value="13">Seneste kvartal</option>
              <option value="26" selected>Seneste 6 mdr.</option>
              <option value="52">Seneste 12 mdr.</option>
            </select>
          </div>
        </div>
        <div class="chart-container" style="height:300px">
          <canvas id="subTrendChart"></canvas>
        </div>
        <p class="trend-note" id="sub-trend-note"></p>
      </div>
      <div class="filters" id="sub-filters">
        {filter_btns}
        <input type="text" class="search-input" placeholder="Søg…" oninput="filterSearch(this,'sub-table')">
      </div>
      <div class="table-wrap">
        <table id="sub-table">
          <thead><tr>
            <th onclick="sortTable(this)">Operatør</th>
            <th onclick="sortTable(this)">Abonnement</th>
            <th onclick="sortTable(this)" class="center">Tale</th>
            <th onclick="sortTable(this)" class="center">Data</th>
            <th onclick="sortTable(this)" class="center">Dækning</th>
            <th onclick="sortTable(this)" class="center">Pris</th>
            <th>Kampagne</th>
            <th>Underholdning</th>
            <th>Noter</th>
          </tr></thead>
          <tbody>{sub_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- ══ INTERNET ══════════════════════════════════════════════════════════ -->
    <div id="section-internet" class="section">
      <div class="page-header" style="display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:1rem">
        <div>
          <h1>Internet</h1>
          <p>Mobilt bredbånd og fast trådløs adgang</p>
        </div>
        <div class="chart-toggle" id="int-subtab-toggle">
          <button class="toggle-btn active" onclick="showIntTab('overview',this)">📊 Overblik</button>
          <button class="toggle-btn" onclick="showIntTab('trends',this)">📈 Tendenser</button>
        </div>
      </div>

      <!-- ── Overblik sub-tab ───────────────────────────────────────────── -->
      <div id="int-tab-overview">
        <div class="kpi-grid">
          <div class="chart-wrap"><h2>📉 Lavest intropris</h2>
            <div class="chart-container"><canvas id="intKpiCampChart"></canvas></div></div>
          <div class="chart-wrap"><h2>💰 Lavest standardpris</h2>
            <div class="chart-container"><canvas id="intKpiPriceChart"></canvas></div></div>
          <div class="chart-wrap"><h2>📅 Længste introperiode (mdr.)</h2>
            <div class="chart-container"><canvas id="intKpiMonthsChart"></canvas></div></div>
          <div class="chart-wrap"><h2>🔒 Min. pris (6 mdr. binding)</h2>
            <div class="chart-container"><canvas id="intKpiAfterChart"></canvas></div></div>
        </div>
        <div class="filters" id="int-filters">
          {filter_btns}
          <input type="text" class="search-input" placeholder="Søg…" oninput="filterSearch(this,'int-table')">
        </div>
        <div class="table-wrap">
          <table id="int-table">
            <thead><tr>
              <th onclick="sortTable(this)">Operatør</th>
              <th onclick="sortTable(this)">Produkt</th>
              <th onclick="sortTable(this)" class="center">Type</th>
              <th onclick="sortTable(this)" class="center">Teknologi</th>
              <th onclick="sortTable(this)" class="center">Data</th>
              <th onclick="sortTable(this)" class="center" title="Samlede omkostninger over 6 mdr. inkl. evt. introrabat">Min. pris (6 mdr.)</th>
              <th onclick="sortTable(this)" class="center" title="Normal månedspris efter introperiode">Standard pris</th>
              <th onclick="sortTable(this)" class="center">Intro periode</th>
              <th>Noter</th>
            </tr></thead>
            <tbody>{int_rows}</tbody>
          </table>
        </div>
      </div>

      <!-- ── Tendenser sub-tab ──────────────────────────────────────────── -->
      <div id="int-tab-trends" style="display:none">
        <div style="display:flex;justify-content:flex-end;margin-bottom:1rem">
          <div class="window-select">
            <span>Periode:</span>
            <select onchange="setTrendWindow(+this.value,'int')">
              <option value="1">Seneste uge</option>
              <option value="4">Seneste måned</option>
              <option value="13">Seneste kvartal</option>
              <option value="26" selected>Seneste 6 mdr.</option>
              <option value="52">Seneste 12 mdr.</option>
            </select>
          </div>
        </div>
        <div class="kpi-grid">
          <div class="chart-wrap">
            <h2>Intropris — udvikling pr. operatør</h2>
            <div class="chart-container" style="height:280px"><canvas id="intTrendCamp"></canvas></div>
            <p class="trend-note" id="int-trend-camp-note"></p>
          </div>
          <div class="chart-wrap">
            <h2>Standardpris — udvikling pr. operatør</h2>
            <div class="chart-container" style="height:280px"><canvas id="intTrendStd"></canvas></div>
            <p class="trend-note" id="int-trend-std-note"></p>
          </div>
          <div class="chart-wrap">
            <h2>Min. pris (6 mdr.) — udvikling pr. operatør</h2>
            <div class="chart-container" style="height:280px"><canvas id="intTrendMin"></canvas></div>
            <p class="trend-note" id="int-trend-min-note"></p>
          </div>
          <div class="chart-wrap">
            <h2>Introperiode (mdr.) — udvikling pr. operatør</h2>
            <div class="chart-container" style="height:280px"><canvas id="intTrendPeriod"></canvas></div>
            <p class="trend-note" id="int-trend-period-note"></p>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ HARDWARE ══════════════════════════════════════════════════════════ -->
    <div id="section-hardware" class="section">
      <div class="page-header">
        <h1>Hardware</h1>
        <p>Device-priser på tværs af operatører</p>
      </div>
      <div class="filters" id="hw-filters">
        {filter_btns}
        <input type="text" class="search-input" placeholder="Søg model…" oninput="filterSearch(this,'hw-table')">
      </div>
      <div class="table-wrap">
        <table id="hw-table">
          <thead><tr>
            <th onclick="sortTable(this)">Operatør</th>
            <th onclick="sortTable(this)">Model</th>
            <th onclick="sortTable(this)" class="center">Lager</th>
            <th onclick="sortTable(this)" class="center">Min. pris</th>
            <th onclick="sortTable(this)" class="center">Max. pris</th>
            <th>Noter</th>
          </tr></thead>
          <tbody>{hw_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- ══ VAS ═══════════════════════════════════════════════════════════════ -->
    <div id="section-vas" class="section">
      <div class="page-header">
        <h1>VAS — Value Added Services</h1>
        <p>Underholdningstjenester og tilbudte services</p>
      </div>
      <div class="filters" id="vas-filters">
        {filter_btns}
        <input type="text" class="search-input" placeholder="Søg…" oninput="filterSearch(this,'vas-table')">
      </div>
      <div class="table-wrap">
        <table id="vas-table">
          <thead><tr>
            <th onclick="sortTable(this)">Operatør</th>
            <th onclick="sortTable(this)">Tjeneste</th>
            <th onclick="sortTable(this)" class="center">Kategori</th>
            <th onclick="sortTable(this)" class="center">Status</th>
          </tr></thead>
          <tbody>{vas_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- ══ ROAMING ═══════════════════════════════════════════════════════════ -->
    <div id="section-roaming" class="section">
      <div class="page-header">
        <h1>🌍 Roaming</h1>
        <p>Sammenligning af Roam Like Home-vilkår · data og lande pr. abonnement · opdateres ugentligt</p>
      </div>
      <div class="roam-legend">
        <span class="roam-legend-dot" style="background:#FF620022;border:1.5px solid #FF6200"></span>
        <strong style="color:var(--text)">Farvet badge</strong> = landet er unikt for denne operatør
        &nbsp;·&nbsp;
        <span class="roam-legend-dot" style="background:var(--surface2);border:1px solid var(--border)"></span>
        Grå badge = delt med én eller flere andre operatører
      </div>
      <div class="filters" id="roaming-filters">
        {roaming_filter_btns}
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Operatør</th>
              <th>Abonnement</th>
              <th>Pris/md</th>
              <th style="text-align:center">Data i EU</th>
              <th style="text-align:center">Antal lande</th>
              <th>Zone</th>
              <th>Ekstra lande (ud over EU/EØS)</th>
            </tr>
          </thead>
          <tbody>{roaming_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- ══ NEWSROOM ══════════════════════════════════════════════════════════ -->
    <div id="section-newsroom" class="section">
      <div class="page-header">
        <h1>Newsroom</h1>
        <p>Seneste nyheder fra operatørerne · Google News · opdateret ugentligt</p>
      </div>
      <div class="filters" id="news-filters">
        {filter_btns}
      </div>
      <div class="news-grid" id="news-grid">
        {news_cards}
      </div>
    </div>

  </main>
</div>

<script>
// ── Embedded data ─────────────────────────────────────────────────────────────
const cheapestData    = {{ labels: {chart_labels},     values: {chart_values},     colors: {chart_colors},     names: {chart_names} }};
const cheapestDataAll = {{ labels: {chart_labels_all}, values: {chart_values_all}, colors: {chart_colors_all}, names: {chart_names_all} }};
const cheapestIntData = {{ labels: {int_chart_labels}, values: {int_chart_values}, colors: {int_chart_colors}, names: {int_chart_names} }};
const trendData    = {trend_json};
const kpiLabels    = {kpi_labels};
const kpiColors    = {kpi_colors};
const kpiMinPrice  = {kpi_min_price};
const kpiMinCamp   = {kpi_min_camp};
const kpiMaxMonths = {kpi_max_months};
const kpiMinAfter  = {kpi_min_after};
const campOps      = {json.dumps([
    {"op": s["operator"], "normal": s["price"], "camp": s["campaign_price"]}
    for s in all_subs if s.get("campaign_price") is not None
][:12])};

// ── Chart defaults ────────────────────────────────────────────────────────────
const BASE = {{
  responsive: true, maintainAspectRatio: false,
  plugins: {{ legend: {{ display: false }} }},
  scales: {{
    x: {{ ticks: {{ color: "#6B7285", maxRotation: 45 }}, grid: {{ color: "#DDE0EC" }} }},
    y: {{ ticks: {{ color: "#6B7285", callback: v => v + " kr." }}, grid: {{ color: "#DDE0EC" }} }}
  }}
}};
const BASE_MONTHS = {{
  ...BASE,
  scales: {{ ...BASE.scales, y: {{ ticks: {{ color: "#6B7285", callback: v => v + " mdr." }}, grid: {{ color: "#DDE0EC" }} }} }}
}};

// ── Bar chart helper ──────────────────────────────────────────────────────────
function barChart(id, labels, values, colors, unit, names) {{
  const opts = unit === "mdr" ? BASE_MONTHS : BASE;
  const suffix = unit === "mdr" ? " mdr." : " kr.";
  const tooltipPlugin = {{
    tooltip: {{
      callbacks: {{
        title: ctx => (names && names[ctx[0].dataIndex]) ? names[ctx[0].dataIndex] : ctx[0].label,
        label: ctx => ctx.parsed.y + suffix
      }}
    }}
  }};
  return new Chart(document.getElementById(id), {{
    type: "bar",
    data: {{ labels,
      datasets: [{{ data: values,
        backgroundColor: colors.map(c => c + "99"),
        borderColor: colors, borderWidth: 2, borderRadius: 6 }}] }},
    options: {{ ...opts, plugins: {{ ...opts.plugins, ...tooltipPlugin }} }}
  }});
}}

// ── Trend line chart helper ───────────────────────────────────────────────────
const _trendInstances = {{}};  // canvasId → Chart instance

function trendChart(canvasId, noteId, section, dataKey="prices", unit="kr", windowSize=26) {{
  const data = trendData[section];
  if (!data || data.dates.length < 2) {{
    const note = document.getElementById(noteId);
    if (note) note.textContent = "Trenddata vises fra og med anden kørsel (kræver mindst 2 ugers data)";
    return;
  }}
  // Slice to last N data points
  const n = Math.min(windowSize, data.dates.length);
  const slicedDates = data.dates.slice(-n);
  const suffix = unit === "mdr" ? " mdr." : " kr.";
  const datasets = Object.entries(data.operators)
    .filter(([, d]) => (d[dataKey] || []).some(p => p !== null))
    .map(([name, d]) => ({{
      label: name,
      data: (d[dataKey] || []).slice(-n),
      borderColor: d.color,
      backgroundColor: "transparent",
      stepped: true,
      borderWidth: 2,
      pointRadius: slicedDates.length > 20 ? 2 : 4,
      pointHoverRadius: 7,
      pointBackgroundColor: d.color,
    }}));
  // Destroy existing instance if re-rendering
  if (_trendInstances[canvasId]) {{ _trendInstances[canvasId].destroy(); }}
  _trendInstances[canvasId] = new Chart(document.getElementById(canvasId), {{
    type: "line",
    data: {{ labels: slicedDates, datasets }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: true, labels: {{ color: "#1A1D2E", boxWidth: 14, padding: 16 }} }} }},
      scales: {{
        x: {{ ticks: {{ color: "#6B7285", maxRotation: 45, maxTicksLimit: 16 }}, grid: {{ color: "#DDE0EC" }} }},
        y: {{ ticks: {{ color: "#6B7285", callback: v => v + suffix }}, grid: {{ color: "#DDE0EC" }} }}
      }}
    }}
  }});
}}

// ── Week-window selector ──────────────────────────────────────────────────────
function setTrendWindow(n, group) {{
  if (group === "sub") {{
    trendChart("subTrendChart", "sub-trend-note", "subscriptions", "prices", "kr", n);
  }} else {{
    trendChart("intTrendCamp",   "int-trend-camp-note",   "internet", "campaign_prices", "kr",  n);
    trendChart("intTrendStd",    "int-trend-std-note",    "internet", "prices",          "kr",  n);
    trendChart("intTrendMin",    "int-trend-min-note",    "internet", "min_prices",      "kr",  n);
    trendChart("intTrendPeriod", "int-trend-period-note", "internet", "intro_months",    "mdr", n);
  }}
}}

// ── Render all charts ─────────────────────────────────────────────────────────
let _cheapestType = "subs";
let _showSegment  = false;

function _getCheapestData() {{
  if (_cheapestType === "internet") return cheapestIntData;
  return _showSegment ? cheapestDataAll : cheapestData;
}}

function _updateCheapestChart() {{
  const d = _getCheapestData();
  const titles = {{
    subs:     _showSegment ? "Billigste abonnement pr. operatør — inkl. Børn/Ung (kr./md.)"
                           : "Billigste abonnement pr. operatør — ekskl. Børn/Ung (kr./md.)",
    internet: "Billigste internet pr. operatør (kr./md.)"
  }};
  document.getElementById("cheapest-title").textContent = titles[_cheapestType];
  // hide segment toggle when internet is selected
  document.getElementById("segment-toggle").style.display = _cheapestType === "internet" ? "none" : "";
  cheapestChartInst.data.labels = d.labels;
  cheapestChartInst.data.datasets[0].data = d.values;
  cheapestChartInst.data.datasets[0].backgroundColor = d.colors.map(c => c + "99");
  cheapestChartInst.data.datasets[0].borderColor = d.colors;
  cheapestChartInst.options.plugins.tooltip = {{
    callbacks: {{
      title: ctx => (d.names && d.names[ctx[0].dataIndex]) ? d.names[ctx[0].dataIndex] : ctx[0].label,
      label: ctx => ctx.parsed.y + " kr."
    }}
  }};
  cheapestChartInst.update();
}}

let cheapestChartInst = barChart("cheapestChart", cheapestData.labels, cheapestData.values, cheapestData.colors, "kr", cheapestData.names);

function switchCheapestChart(type, btn) {{
  _cheapestType = type;
  document.querySelectorAll("#type-toggle .toggle-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  _updateCheapestChart();
}}

function setSegment(show, btn) {{
  _showSegment = show;
  document.querySelectorAll("#segment-toggle .toggle-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  _updateCheapestChart();
}}

if (campOps.length > 0) {{
  new Chart(document.getElementById("campaignChart"), {{
    type: "bar",
    data: {{
      labels: campOps.map(d => d.op + " " + d.normal + " kr."),
      datasets: [
        {{ label: "Normal pris",   data: campOps.map(d => d.normal),
           backgroundColor: "#1A1D2E33", borderColor: "#1A1D2E", borderWidth: 2, borderRadius: 4 }},
        {{ label: "Kampagnepris",  data: campOps.map(d => d.camp),
           backgroundColor: "#FF540099", borderColor: "#FF5400", borderWidth: 2, borderRadius: 4 }}
      ]
    }},
    options: {{ ...BASE, plugins: {{ legend: {{ display: true, labels: {{ color: "#1A1D2E" }} }} }} }}
  }});
}}

// Internet KPI charts
barChart("intKpiCampChart",   kpiLabels, kpiMinCamp,   kpiColors, "kr");
barChart("intKpiPriceChart",  kpiLabels, kpiMinPrice,  kpiColors, "kr");
barChart("intKpiMonthsChart", kpiLabels, kpiMaxMonths, kpiColors, "mdr");
barChart("intKpiAfterChart",  kpiLabels, kpiMinAfter,  kpiColors, "kr");

// Trend charts (renders when 2+ data points exist)
trendChart("subTrendChart", "sub-trend-note", "subscriptions");

// Internet trend charts (4 metrics)
trendChart("intTrendCamp",   "int-trend-camp-note",   "internet", "campaign_prices", "kr");
trendChart("intTrendStd",    "int-trend-std-note",    "internet", "prices",          "kr");
trendChart("intTrendMin",    "int-trend-min-note",    "internet", "min_prices",      "kr");
trendChart("intTrendPeriod", "int-trend-period-note", "internet", "intro_months",    "mdr");

// Internet sub-tab toggle
let _intTrendsRendered = false;
function showIntTab(tab, btn) {{
  document.getElementById("int-tab-overview").style.display = tab === "overview" ? "" : "none";
  document.getElementById("int-tab-trends").style.display   = tab === "trends"   ? "" : "none";
  document.querySelectorAll("#int-subtab-toggle .toggle-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}}

// ── Navigation ────────────────────────────────────────────────────────────────
function showSection(name) {{
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("section-" + name).classList.add("active");
  event.currentTarget.classList.add("active");
  document.getElementById("global-search").value = "";
  document.querySelectorAll(".data-row").forEach(r => r.classList.remove("hidden"));
}}

// ── Global search (Ctrl+K) ────────────────────────────────────────────────────
document.addEventListener("keydown", e => {{
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {{
    e.preventDefault();
    document.getElementById("global-search").focus();
  }}
}});

function globalSearch(q) {{
  const query = q.toLowerCase().trim();
  const activeSection = document.querySelector(".section.active");
  if (!activeSection) return;
  activeSection.querySelectorAll(".data-row").forEach(row => {{
    row.classList.toggle("hidden", query.length > 0 && !row.textContent.toLowerCase().includes(query));
  }});
  // Also reset operator filters so search isn't blocked
  activeSection.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  const allBtn = activeSection.querySelector(".filter-btn[data-filter='all']");
  if (allBtn) allBtn.classList.add("active");
}}

// ── Operator filter ───────────────────────────────────────────────────────────
document.querySelectorAll(".filters").forEach(filterEl => {{
  filterEl.querySelectorAll(".filter-btn").forEach(btn => {{
    btn.addEventListener("click", function() {{
      filterEl.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      document.getElementById("global-search").value = "";
      const filter = this.dataset.filter;
      // Filter table rows (subscriptions, internet, etc.)
      const tableEl = filterEl.parentElement.querySelector("table");
      if (tableEl) {{
        tableEl.querySelectorAll(".data-row").forEach(row => {{
          row.classList.toggle("hidden", filter !== "all" && row.dataset.operator !== filter);
        }});
      }}
      // Filter news cards
      const grid = filterEl.parentElement.querySelector(".news-grid");
      if (grid) {{
        grid.querySelectorAll(".news-card").forEach(card => {{
          card.classList.toggle("hidden", filter !== "all" && card.dataset.operator !== filter);
        }});
      }}
    }});
  }});
}});

// ── News pill → Newsroom ─────────────────────────────────────────────────────
function goToNewsroom(op) {{
  showSection('newsroom');
  const filtersEl = document.getElementById('news-filters');
  if (!filtersEl) return;
  filtersEl.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  const target = op
    ? filtersEl.querySelector(`.filter-btn[data-filter="${{op}}"]`)
    : filtersEl.querySelector('.filter-btn[data-filter="all"]');
  const btn = target || filtersEl.querySelector('.filter-btn[data-filter="all"]');
  if (btn) btn.click();
}}

// ── In-section search ──────────────────────────────────────────────────────────
function filterSearch(input, tableId) {{
  const q = input.value.toLowerCase();
  document.querySelectorAll("#" + tableId + " .data-row").forEach(row => {{
    row.classList.toggle("hidden", q.length > 0 && !row.textContent.toLowerCase().includes(q));
  }});
}}

// ── Sort ──────────────────────────────────────────────────────────────────────
function sortTable(th) {{
  const table = th.closest("table");
  const idx   = Array.from(th.parentElement.children).indexOf(th);
  const asc   = th.dataset.sort !== "asc";
  th.dataset.sort = asc ? "asc" : "desc";
  th.parentElement.querySelectorAll("th").forEach(t => {{ if (t !== th) delete t.dataset.sort; }});
  const rows = Array.from(table.querySelectorAll("tbody .data-row"));
  rows.sort((a, b) => {{
    const av = a.cells[idx]?.textContent.trim() || "";
    const bv = b.cells[idx]?.textContent.trim() || "";
    const an = parseFloat(av.replace(/[^\d,]/g, "").replace(",", "."));
    const bn = parseFloat(bv.replace(/[^\d,]/g, "").replace(",", "."));
    if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
    return asc ? av.localeCompare(bv, "da") : bv.localeCompare(av, "da");
  }});
  rows.forEach(r => table.querySelector("tbody").appendChild(r));
}}
</script>
</body>
</html>"""

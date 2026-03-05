"""
Market Intelligence Agent — Baseline Data (Week 09, 2026)
Pre-loaded from the manually compiled Konkurrentovervågning report.
Used as fallback when live scraping fails, and as the prior week for change detection.
"""

BASELINE = {
    "week": "09",
    "year": "2026",
    "operators": {
        "3": {
            "subscriptions": [
                {"operator": "3", "name": "3Timer 3GB", "talk": "3 timer", "data_gb": 3, "coverage": "DK", "price": 60, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "3", "name": "8Timer 8GB", "talk": "8 timer", "data_gb": 8, "coverage": "DK", "price": 80, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "3", "name": "15Timer 15GB", "talk": "15 timer", "data_gb": 15, "coverage": "DK", "price": 100, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "3", "name": "Fri Tale 10GB", "talk": "Fri", "data_gb": 10, "coverage": "Verden", "price": 125, "campaign_price": None, "campaign_duration": None, "entertainment": ["Deezer"], "notes": "3LikeHome 100 lande"},
                {"operator": "3", "name": "Fri Tale 50GB", "talk": "Fri", "data_gb": 50, "coverage": "Verden", "price": 170, "campaign_price": 175, "campaign_duration": "3 mdr.", "entertainment": ["Deezer"], "notes": ""},
                {"operator": "3", "name": "Fri Tale 75GB", "talk": "Fri", "data_gb": 75, "coverage": "Verden", "price": 175, "campaign_price": None, "campaign_duration": None, "entertainment": ["Deezer"], "notes": ""},
                {"operator": "3", "name": "Fri Tale 100GB", "talk": "Fri", "data_gb": 100, "coverage": "Verden", "price": 210, "campaign_price": None, "campaign_duration": None, "entertainment": ["Deezer"], "notes": ""},
                {"operator": "3", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "Verden", "price": 270, "campaign_price": None, "campaign_duration": None, "entertainment": ["Deezer"], "notes": ""},
                {"operator": "3", "name": "Ekstrabruger", "talk": "Fri", "data_gb": 0, "coverage": "Verden", "price": 120, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
            ],
            "internet": [
                {"operator": "3", "name": "10GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 10, "price": 60, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "3", "name": "20GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 20, "price": 100, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "3", "name": "50GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 50, "price": 160, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "3", "name": "200GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 200, "price": 210, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "3", "name": "3Internet 5G", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 299, "campaign_price": 149, "campaign_duration": "6 mdr.", "notes": "Inkl. Lånerouter"},
            ],
            "vas": [
                {"operator": "3", "service": "Deezer", "category": "Musik", "price": None, "included": True},
                {"operator": "3", "service": "TV2 Play", "category": "Streaming", "price": None, "included": False},
                {"operator": "3", "service": "Viaplay", "category": "Streaming", "price": None, "included": False},
                {"operator": "3", "service": "Wype", "category": "Bøger/magasiner", "price": None, "included": False},
            ],
        },
        "oister": {
            "subscriptions": [
                {"operator": "OiSTER", "name": "5Timer 5GB", "talk": "5 timer", "data_gb": 5, "coverage": "EU", "price": 59, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "OiSTER", "name": "Fri Tale 35GB", "talk": "Fri", "data_gb": 35, "coverage": "EU", "price": 99, "campaign_price": 49, "campaign_duration": "3 mdr.", "entertainment": [], "notes": ""},
                {"operator": "OiSTER", "name": "Fri Tale 70GB", "talk": "Fri", "data_gb": 70, "coverage": "EU", "price": 109, "campaign_price": 54, "campaign_duration": "3 mdr.", "entertainment": [], "notes": ""},
                {"operator": "OiSTER", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 219, "campaign_price": 99, "campaign_duration": "3 mdr.", "entertainment": [], "notes": ""},
                {"operator": "OiSTER", "name": "Fri Tale 85GB + Disney+", "talk": "Fri", "data_gb": 85, "coverage": "EU", "price": 179, "campaign_price": 99, "campaign_duration": "1 mdr.", "entertainment": ["Disney+"], "notes": ""},
                {"operator": "OiSTER", "name": "Fri Tale 70GB + Viaplay", "talk": "Fri", "data_gb": 70, "coverage": "EU", "price": 199, "campaign_price": 159, "campaign_duration": "6 mdr.", "entertainment": ["Viaplay"], "notes": ""},
                {"operator": "OiSTER", "name": "Fri Tale 3GB Senior", "talk": "Fri", "data_gb": 3, "coverage": "EU", "price": 59, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "Til Seniorer"},
                {"operator": "OiSTER", "name": "5Timer 20GB Børn", "talk": "5 timer", "data_gb": 20, "coverage": "EU", "price": 79, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "Til børn"},
            ],
            "internet": [
                {"operator": "OiSTER", "name": "4G Internet 2000GB", "type": "Fast trådløs", "tech": "4G", "data_gb": 2000, "price": 239, "campaign_price": 159, "campaign_duration": "10 mdr.", "notes": "Inkl. Norton Antivirus + 4G Lånerouter"},
                {"operator": "OiSTER", "name": "5G Internet Fri", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 269, "campaign_price": 179, "campaign_duration": "10 mdr.", "notes": "Inkl. Disney+ + 5G Lånerouter"},
                {"operator": "OiSTER", "name": "50GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 50, "price": 99, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "OiSTER", "name": "200GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 200, "price": 149, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "OiSTER", "name": "1000GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 1000, "price": 199, "campaign_price": None, "campaign_duration": None, "notes": ""},
            ],
            "vas": [
                {"operator": "OiSTER", "service": "Disney+", "category": "Streaming", "price": None, "included": True},
                {"operator": "OiSTER", "service": "Viaplay", "category": "Streaming", "price": None, "included": False},
                {"operator": "OiSTER", "service": "TV2 Play", "category": "Streaming", "price": None, "included": False},
                {"operator": "OiSTER", "service": "Podimo", "category": "Streaming", "price": None, "included": False},
                {"operator": "OiSTER", "service": "Deezer", "category": "Musik", "price": None, "included": False},
            ],
        },
        "telenor": {
            "subscriptions": [
                {"operator": "Telenor", "name": "Fri Tale 30GB", "talk": "Fri", "data_gb": 30, "coverage": "Verden", "price": 169, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "Telenor", "name": "Fri Tale 80GB", "talk": "Fri", "data_gb": 80, "coverage": "Verden", "price": 209, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "Telenor", "name": "Fri Tale 120GB", "talk": "Fri", "data_gb": 120, "coverage": "Verden", "price": 239, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "Telenor", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "Verden", "price": 289, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "Telenor", "name": "Fri Tale 120GB Ung", "talk": "Fri", "data_gb": 120, "coverage": "Verden", "price": 189, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "Til unge under 24 år"},
                {"operator": "Telenor", "name": "Fri Tale FriGB Ung", "talk": "Fri", "data_gb": "Fri", "coverage": "Verden", "price": 239, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "Til unge under 24 år"},
                {"operator": "Telenor", "name": "Fri Tale 10GB Børn", "talk": "Fri", "data_gb": 10, "coverage": "Verden", "price": 129, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "Til børn under 13 år"},
            ],
            "internet": [
                {"operator": "Telenor", "name": "30GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 30, "price": 129, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. SafeSurf"},
                {"operator": "Telenor", "name": "80GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 80, "price": 189, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. SafeSurf"},
                {"operator": "Telenor", "name": "250GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 250, "price": 229, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. SafeSurf"},
                {"operator": "Telenor", "name": "5G Internet Fri", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 299, "campaign_price": 129, "campaign_duration": "6 mdr.", "notes": ""},
                {"operator": "Telenor", "name": "Fibernet 1000/1000", "type": "Fast trådløs", "tech": "Fiber", "data_gb": "Fri", "price": 319, "campaign_price": 99, "campaign_duration": "6 mdr.", "notes": ""},
            ],
            "vas": [],
        },
        "yousee": {
            "subscriptions": [
                {"operator": "YouSee", "name": "Fri Tale 25GB", "talk": "Fri", "data_gb": 25, "coverage": "Verden", "price": 179, "campaign_price": None, "campaign_duration": None, "entertainment": ["YouSee Musik"], "notes": ""},
                {"operator": "YouSee", "name": "Fri Tale 50GB", "talk": "Fri", "data_gb": 50, "coverage": "Verden", "price": 219, "campaign_price": None, "campaign_duration": None, "entertainment": ["YouSee Musik"], "notes": ""},
                {"operator": "YouSee", "name": "Fri Tale 100GB", "talk": "Fri", "data_gb": 100, "coverage": "Verden", "price": 249, "campaign_price": None, "campaign_duration": None, "entertainment": ["YouSee Musik"], "notes": ""},
                {"operator": "YouSee", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "Verden", "price": 299, "campaign_price": None, "campaign_duration": None, "entertainment": ["YouSee Musik"], "notes": ""},
                {"operator": "YouSee", "name": "Ekstrabruger", "talk": "Fri", "data_gb": 0, "coverage": "Verden", "price": 129, "campaign_price": None, "campaign_duration": None, "entertainment": ["YouSee Musik"], "notes": ""},
                {"operator": "YouSee", "name": "Børneabonnement", "talk": "Fri", "data_gb": 3, "coverage": "EU", "price": 79, "campaign_price": 0, "campaign_duration": None, "entertainment": [], "notes": "0 kr. Oprettelse"},
            ],
            "internet": [
                {"operator": "YouSee", "name": "30GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 30, "price": 119, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "YouSee", "name": "200GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 200, "price": 219, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "YouSee", "name": "Mobilt 5G Internet Fri", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": "Fri", "price": 329, "campaign_price": 164.5, "campaign_duration": "3 mdr.", "notes": "Eksl. Lånerouter (200 kr. engangsgebyr)"},
                {"operator": "YouSee", "name": "Internet 100/100", "type": "Fast trådløs", "tech": "Fiber", "data_gb": "Fri", "price": 349, "campaign_price": 249, "campaign_duration": "6 mdr.", "notes": ""},
                {"operator": "YouSee", "name": "Internet 200/200", "type": "Fast trådløs", "tech": "Fiber", "data_gb": "Fri", "price": 379, "campaign_price": 279, "campaign_duration": "6 mdr.", "notes": ""},
                {"operator": "YouSee", "name": "Internet 1000/1000", "type": "Fast trådløs", "tech": "Fiber", "data_gb": "Fri", "price": 409, "campaign_price": 309, "campaign_duration": "6 mdr.", "notes": ""},
            ],
            "vas": [
                {"operator": "YouSee", "service": "YouSee Musik", "category": "Musik", "price": None, "included": True},
                {"operator": "YouSee", "service": "YouSee Play", "category": "Streaming", "price": None, "included": False},
            ],
        },
        "norlys": {
            "subscriptions": [
                {"operator": "Norlys", "name": "Little One", "talk": "Fri", "data_gb": 3, "coverage": "EU", "price": 59, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "Norlys", "name": "Smart20", "talk": "Fri", "data_gb": 20, "coverage": "EU", "price": 159, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "1 valgfri tjeneste i 6 mdr."},
                {"operator": "Norlys", "name": "Smart60", "talk": "Fri", "data_gb": 60, "coverage": "EU", "price": 199, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "1 valgfri tjeneste i 6 mdr."},
                {"operator": "Norlys", "name": "Smart200", "talk": "Fri", "data_gb": 200, "coverage": "EU", "price": 229, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "1 valgfri tjeneste i 6 mdr."},
                {"operator": "Norlys", "name": "ONE", "talk": "Fri", "data_gb": "Fri", "coverage": "Verden", "price": 279, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "1 valgfri tjeneste i 12 mdr."},
                {"operator": "Norlys", "name": "Little OneMore", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 89, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "Kræver ONE abonnement"},
                {"operator": "Norlys", "name": "Smart Netflix", "talk": "Fri", "data_gb": 60, "coverage": "EU", "price": 279, "campaign_price": None, "campaign_duration": None, "entertainment": ["Netflix"], "notes": "1 valgfri tjeneste i 6 mdr."},
                {"operator": "Norlys", "name": "ONE Netflix", "talk": "Fri", "data_gb": "Fri", "coverage": "Verden", "price": 359, "campaign_price": None, "campaign_duration": None, "entertainment": ["Netflix"], "notes": "1 valgfri tjeneste i 12 mdr."},
            ],
            "internet": [
                {"operator": "Norlys", "name": "5G Internet Fri", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 299, "campaign_price": 199, "campaign_duration": "6 mdr.", "notes": "TV2 Play gratis 3 mdr. + MAX + Podimo gratis 2 mdr. Inkl. Lånerouter"},
                {"operator": "Norlys", "name": "Internet 1000 Basic", "type": "Fast trådløs", "tech": "Fiber", "data_gb": "Fri", "price": 369, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "Norlys", "name": "Internet 1000", "type": "Fast trådløs", "tech": "Fiber", "data_gb": "Fri", "price": 419, "campaign_price": None, "campaign_duration": None, "notes": ""},
            ],
            "vas": [
                {"operator": "Norlys", "service": "Netflix", "category": "Streaming", "price": None, "included": False},
                {"operator": "Norlys", "service": "Max", "category": "Streaming", "price": None, "included": False},
                {"operator": "Norlys", "service": "TV2 Play", "category": "Streaming", "price": None, "included": False},
                {"operator": "Norlys", "service": "Viaplay", "category": "Streaming", "price": None, "included": False},
                {"operator": "Norlys", "service": "Podimo", "category": "Streaming", "price": None, "included": False},
            ],
        },
        "cbb": {
            "subscriptions": [
                {"operator": "CBB", "name": "Fri Tale 50GB", "talk": "Fri", "data_gb": 50, "coverage": "EU", "price": 129, "campaign_price": 39, "campaign_duration": "2 mdr.", "entertainment": [], "notes": ""},
                {"operator": "CBB", "name": "Fri Tale 80GB", "talk": "Fri", "data_gb": 80, "coverage": "EU", "price": 139, "campaign_price": 49, "campaign_duration": "2 mdr.", "entertainment": [], "notes": ""},
                {"operator": "CBB", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 219, "campaign_price": 49, "campaign_duration": "2 mdr.", "entertainment": [], "notes": ""},
                {"operator": "CBB", "name": "Fri Tale 100GB + 2 tjenester", "talk": "Fri", "data_gb": 100, "coverage": "EU", "price": 259, "campaign_price": 139, "campaign_duration": "2 mdr.", "entertainment": [], "notes": "2 streamingtjenester"},
                {"operator": "CBB", "name": "Fri Tale 200GB + 2 tjenester", "talk": "Fri", "data_gb": 200, "coverage": "EU", "price": 279, "campaign_price": 149, "campaign_duration": "2 mdr.", "entertainment": [], "notes": "2 streamingtjenester"},
                {"operator": "CBB", "name": "Fri Tale FriGB + 2 tjenester", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 309, "campaign_price": 164, "campaign_duration": "2 mdr.", "entertainment": [], "notes": "2 streamingtjenester"},
            ],
            "internet": [
                {"operator": "CBB", "name": "7GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 7, "price": 59, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CBB", "name": "40GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 40, "price": 99, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CBB", "name": "75GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 75, "price": 129, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CBB", "name": "175GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 175, "price": 159, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CBB", "name": "300GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 300, "price": 199, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CBB", "name": "5G Internet Fri", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 299, "campaign_price": 129, "campaign_duration": "3 mdr.", "notes": "Inkl. Lånerouter"},
            ],
            "vas": [
                {"operator": "CBB", "service": "TV2 Play", "category": "Streaming", "price": None, "included": False},
                {"operator": "CBB", "service": "Viaplay", "category": "Streaming", "price": None, "included": False},
                {"operator": "CBB", "service": "Max", "category": "Streaming", "price": None, "included": False},
                {"operator": "CBB", "service": "Podimo", "category": "Streaming", "price": None, "included": False},
                {"operator": "CBB", "service": "Mofibo", "category": "Streaming", "price": None, "included": False},
                {"operator": "CBB", "service": "Nordisk Film+", "category": "Streaming", "price": None, "included": False},
                {"operator": "CBB", "service": "Deezer", "category": "Musik", "price": None, "included": False},
            ],
        },
        "telmore": {
            "subscriptions": [
                {"operator": "Telmore", "name": "3Timer 2GB Børn", "talk": "3 timer", "data_gb": 2, "coverage": "EU", "price": 79, "campaign_price": 39, "campaign_duration": "3 mdr.", "entertainment": [], "notes": "Til børn"},
                {"operator": "Telmore", "name": "Fri Tale 50GB", "talk": "Fri", "data_gb": 50, "coverage": "EU", "price": 149, "campaign_price": 69, "campaign_duration": "3 mdr.", "entertainment": [], "notes": ""},
                {"operator": "Telmore", "name": "Fri Tale 100GB", "talk": "Fri", "data_gb": 100, "coverage": "EU", "price": 169, "campaign_price": 79, "campaign_duration": "3 mdr.", "entertainment": [], "notes": ""},
                {"operator": "Telmore", "name": "Fri Tale 100GB + Telmore Musik", "talk": "Fri", "data_gb": 100, "coverage": "EU", "price": 179, "campaign_price": None, "campaign_duration": None, "entertainment": ["Telmore Musik"], "notes": ""},
                {"operator": "Telmore", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 249, "campaign_price": 119, "campaign_duration": "3 mdr.", "entertainment": [], "notes": ""},
                {"operator": "Telmore", "name": "Fri Tale FriGB + 3 tjenester", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 399, "campaign_price": 99, "campaign_duration": "1 mdr.", "entertainment": [], "notes": "3 valgfrie streamingtjenester"},
                {"operator": "Telmore", "name": "Fri Tale FriGB + 4 tjenester", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 449, "campaign_price": 99, "campaign_duration": "1 mdr.", "entertainment": [], "notes": "4 valgfrie streamingtjenester"},
                {"operator": "Telmore", "name": "Fri Tale FriGB + 5 tjenester", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 499, "campaign_price": 99, "campaign_duration": "1 mdr.", "entertainment": [], "notes": "5 valgfrie streamingtjenester"},
            ],
            "internet": [
                {"operator": "Telmore", "name": "5GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 5, "price": 49, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "Telmore", "name": "40GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 40, "price": 99, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "Telmore", "name": "125GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 125, "price": 149, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "Telmore", "name": "250GB Mobilt", "type": "Mobilt bredbånd", "tech": "4G", "data_gb": 250, "price": 199, "campaign_price": None, "campaign_duration": None, "notes": "Inkl. Lånerouter"},
                {"operator": "Telmore", "name": "4G Internet Fri", "type": "Fast trådløs", "tech": "4G", "data_gb": "Fri", "price": 259, "campaign_price": 99, "campaign_duration": "3 mdr.", "notes": "Inkl. Låne-router"},
                {"operator": "Telmore", "name": "5G Internet Fri", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 299, "campaign_price": 99, "campaign_duration": "3 mdr.", "notes": "Inkl. Låne-router"},
            ],
            "vas": [
                {"operator": "Telmore", "service": "Telmore Musik", "category": "Musik", "price": None, "included": True},
                {"operator": "Telmore", "service": "Netflix", "category": "Streaming", "price": None, "included": False},
                {"operator": "Telmore", "service": "Viaplay", "category": "Streaming", "price": None, "included": False},
                {"operator": "Telmore", "service": "TV2 Play", "category": "Streaming", "price": None, "included": False},
                {"operator": "Telmore", "service": "Disney+", "category": "Streaming", "price": None, "included": False},
                {"operator": "Telmore", "service": "Max", "category": "Streaming", "price": None, "included": False},
                {"operator": "Telmore", "service": "Saxo", "category": "Bøger/magasiner", "price": None, "included": False},
            ],
        },
        "eesy": {
            "subscriptions": [
                {"operator": "Eesy", "name": "Fri Tale 50GB", "talk": "Fri", "data_gb": 50, "coverage": "EU", "price": 119, "campaign_price": 39, "campaign_duration": "2 mdr.", "entertainment": [], "notes": ""},
                {"operator": "Eesy", "name": "Fri Tale 80GB", "talk": "Fri", "data_gb": 80, "coverage": "EU", "price": 129, "campaign_price": 49, "campaign_duration": "2 mdr.", "entertainment": [], "notes": ""},
                {"operator": "Eesy", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 219, "campaign_price": 49, "campaign_duration": "2 mdr.", "entertainment": [], "notes": ""},
            ],
            "internet": [
                {"operator": "Eesy", "name": "5G Internet Fri", "type": "Fast trådløs", "tech": "5G", "data_gb": "Fri", "price": 299, "campaign_price": 89, "campaign_duration": "3 mdr.", "notes": "Inkl. Lånerouter"},
            ],
            "vas": [],
        },
        "callme": {
            "subscriptions": [
                {"operator": "CallMe", "name": "2Timer 4GB", "talk": "2 timer", "data_gb": 4, "coverage": "DK", "price": 49, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "CallMe", "name": "7Timer 14GB", "talk": "7 timer", "data_gb": 14, "coverage": "DK", "price": 89, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "CallMe", "name": "Fri Tale 30GB", "talk": "Fri", "data_gb": 30, "coverage": "EU", "price": 119, "campaign_price": None, "campaign_duration": None, "entertainment": ["Viaplay", "Max", "Deezer", "Podimo"], "notes": "Gratis i 2 måneder"},
                {"operator": "CallMe", "name": "Fri Tale 50GB", "talk": "Fri", "data_gb": 50, "coverage": "EU", "price": 129, "campaign_price": 64, "campaign_duration": "3 mdr.", "entertainment": ["Viaplay", "Max", "Deezer", "Podimo"], "notes": "Gratis i 2 måneder"},
                {"operator": "CallMe", "name": "Fri Tale 80GB EU", "talk": "Fri", "data_gb": 80, "coverage": "EU", "price": 139, "campaign_price": None, "campaign_duration": None, "entertainment": ["Viaplay", "Max", "Deezer", "Podimo"], "notes": "Gratis i 2 måneder"},
                {"operator": "CallMe", "name": "Fri Tale 80GB Verden", "talk": "Fri", "data_gb": 80, "coverage": "Verden", "price": 179, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": ""},
                {"operator": "CallMe", "name": "Fri Tale FriGB", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 219, "campaign_price": None, "campaign_duration": None, "entertainment": ["Viaplay", "Max", "Deezer", "Podimo"], "notes": "Gratis i 2 måneder"},
                {"operator": "CallMe", "name": "Fri Tale FriGB Dobbelt", "talk": "Fri", "data_gb": "Fri", "coverage": "EU", "price": 199, "campaign_price": None, "campaign_duration": None, "entertainment": [], "notes": "V/ køb af to abonnementer 129 kr./md/pers"},
            ],
            "internet": [
                {"operator": "CallMe", "name": "5G Internet 500GB", "type": "Fast trådløs", "tech": "5G", "data_gb": 500, "price": 199, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CallMe", "name": "5G Internet 1000GB", "type": "Fast trådløs", "tech": "5G", "data_gb": 1000, "price": 279, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CallMe", "name": "100GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 100, "price": 159, "campaign_price": None, "campaign_duration": None, "notes": ""},
                {"operator": "CallMe", "name": "1000GB Mobilt", "type": "Mobilt bredbånd", "tech": "5G", "data_gb": 1000, "price": 229, "campaign_price": None, "campaign_duration": None, "notes": ""},
            ],
            "vas": [
                {"operator": "CallMe", "service": "Viaplay", "category": "Streaming", "price": None, "included": True},
                {"operator": "CallMe", "service": "Max", "category": "Streaming", "price": None, "included": True},
                {"operator": "CallMe", "service": "Deezer", "category": "Musik", "price": None, "included": True},
                {"operator": "CallMe", "service": "Podimo", "category": "Streaming", "price": None, "included": True},
            ],
        },
        "flexii": {
            "subscriptions": [],
            "internet": [],
            "vas": [],
        },
    }
}

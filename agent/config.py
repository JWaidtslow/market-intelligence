"""
Market Intelligence Agent — Operator Configuration
Defines URLs, brand identity, and scraping targets for each operator.
"""

OPERATORS = {
    "3": {
        "name": "3",
        "own_brand": True,
        "color": "#FF6200",
        "urls": {
            "subscriptions": "https://www.3.dk/abonnementer/",
            "internet": "https://www.3.dk/internet/",
            "hardware": "https://www.3.dk/shop/mobiler/",          # confirmed
        },
    },
    "oister": {
        "name": "OiSTER",
        "own_brand": True,
        "color": "#7C3AED",
        "urls": {
            "subscriptions": "https://oister.dk/abonnementer/",
            "internet": "https://oister.dk/internet/",
            "hardware": "https://oister.dk/kundeshop/mobiler/",
        },
    },
    "flexii": {
        "name": "Flexii",
        "own_brand": True,
        "color": "#60A5FA",
        "urls": {
            "subscriptions": "https://flexii.dk/abonnementer/",
            "internet": "https://flexii.dk/internet/",
            # No hardware — Flexii does not sell devices
        },
    },
    "telenor": {
        "name": "Telenor",
        "own_brand": False,
        "color": "#1D4ED8",
        "urls": {
            "subscriptions": "https://www.telenor.dk/mobilabonnement/",
            "internet": "https://www.telenor.dk/internet/mobilt-bredbaand/",
            "hardware": "https://www.telenor.dk/shop/mobiler/",     # confirmed
        },
    },
    "yousee": {
        "name": "YouSee",
        "own_brand": False,
        "color": "#16A34A",
        "urls": {
            "subscriptions": "https://yousee.dk/mobil/abonnementer/",
            "internet": "https://yousee.dk/internet/mobilt/",
            "hardware": "https://yousee.dk/shop/mobiltelefoner/",
        },
    },
    "norlys": {
        "name": "Norlys",
        "own_brand": False,
        "color": "#DC2626",
        "urls": {
            "subscriptions": "https://norlys.dk/mobil/",
            "internet": "https://norlys.dk/internet/",
            "hardware": "https://shop.norlys.dk/privat/webshop/mobiler/",
        },
    },
    "cbb": {
        "name": "CBB",
        "own_brand": False,
        "color": "#D97706",
        "urls": {
            "subscriptions": "https://www.cbb.dk/abonnementer/",
            "internet": "https://www.cbb.dk/internet/",
            "hardware": "https://www.cbb.dk/shop/mobiltelefoner/",
        },
    },
    "telmore": {
        "name": "Telmore",
        "own_brand": False,
        "color": "#EC4899",
        "urls": {
            "subscriptions": "https://www.telmore.dk/abonnementer/",
            "internet": "https://www.telmore.dk/internet/",
            "hardware": "https://www.telmore.dk/shop/mobiltelefoner/",
        },
    },
    "eesy": {
        "name": "Eesy",
        "own_brand": False,
        "color": "#0891B2",
        "urls": {
            "subscriptions": "https://eesy.dk/abonnementer/",
            "internet": "https://eesy.dk/internet/",
            # No hardware — Eesy does not sell devices
        },
    },
    "callme": {
        "name": "CallMe",
        "own_brand": False,
        "color": "#9F1239",
        "urls": {
            "subscriptions": "https://callme.dk/abonnementer/",
            "internet": "https://callme.dk/internet/",
            "hardware": "https://callme.dk/webshop/mobiler/",
        },
    },
}

# Devices to track in hardware comparison
TRACKED_DEVICES = [
    {"brand": "Apple", "model": "iPhone 17 Pro Max", "storage": "256GB"},
    {"brand": "Apple", "model": "iPhone 17 Pro", "storage": "256GB"},
    {"brand": "Apple", "model": "iPhone Air", "storage": "256GB"},
    {"brand": "Apple", "model": "iPhone 17", "storage": "256GB"},
    {"brand": "Apple", "model": "iPhone 16", "storage": "128GB"},
    {"brand": "Apple", "model": "iPhone 16e", "storage": "128GB"},
    {"brand": "Samsung", "model": "Galaxy S25", "storage": "128GB"},
    {"brand": "Samsung", "model": "Galaxy S25 Plus", "storage": "512GB"},
    {"brand": "Samsung", "model": "Galaxy S25 Ultra", "storage": "256GB"},
    {"brand": "Samsung", "model": "Galaxy Z Fold 7", "storage": "256GB"},
    {"brand": "Samsung", "model": "Galaxy Z Flip 7", "storage": "256GB"},
    {"brand": "Samsung", "model": "Galaxy A56", "storage": "128GB"},
    {"brand": "Samsung", "model": "Galaxy A36", "storage": "128GB"},
    {"brand": "Samsung", "model": "Galaxy A26", "storage": "128GB"},
]

# Streaming services to track for VAS
TRACKED_SERVICES = [
    "Viaplay", "Disney+", "Netflix", "TV2 Play", "HBO Max", "Max",
    "Deezer", "Telmore Musik", "YouSee Musik", "Podimo",
    "Nordisk Film+", "Sky Showtime", "Saxo", "Wype",
]

#!/usr/bin/env python3
"""Build Babe's Honey Farm store locator data from FreshBooks customer CSV."""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path("/workspace/locator")
CSV_PATH = Path("/workspace/customer-products-from-freshbooks.csv")
CACHE_PATH = ROOT / "geocode-cache.json"
FAIL_PATH = ROOT / "geocode-failures.json"
STORES_PATH = ROOT / "stores.json"
EXCLUDED_PATH = ROOT / "excluded.json"

USER_AGENT = "BabesHoneyFarmLocator/1.0 (brandon@babes-honey-farm.com)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
SLEEP = 1.1

# Vancouver Island / south-coast BC bias (west, south, east, north)
VIEWBOX = "-128.9,48.0,-122.7,51.1"

PRODUCT_ORDER = [
    "Wildflower 500g",
    "Clover 500g",
    "Creamed 500g",
    "Wildflower 1kg",
    "Clover 1kg",
    "Creamed 1kg",
    "Bulk",
    "Mermaid Tears 473ml",
    "Earl Grey 473ml",
    "Currantly Hip 473ml",
    "Ginger Splash 473ml",
    "Mermaid Tears 750ml",
    "Earl Grey 750ml",
    "Currantly Hip 750ml",
    "Ginger Splash 750ml",
    "On Tap",
]

CODE_TO_LABEL = {
    # Honey jars (glass)
    "B-WFW-500": "Wildflower 500g jar",
    "B-CLV-500": "Clover 500g jar",
    "B-CCW-500": "Creamed 500g jar",
    "A-WFW-1K": "Wildflower 1kg jar",
    "A-CLV-1K": "Clover 1kg jar",
    "A-CCW-1K": "Creamed 1kg jar",
    # Bee Line 473ml cans
    "BLINE-473-MER": "Mermaid Tears 473ml can",
    "BLINE-473-ERL": "Earl Grey 473ml can",
    "BLINE-473-CUR": "Currantly Hip 473ml can",
    "BLINE-473-GNG": "Ginger Splash 473ml can",
    # Bee Line 750ml glass bottles
    "BLINE-750-MER": "Mermaid Tears 750ml bottle",
    "BLINE-750-CUR": "Currantly Hip 750ml bottle",
    "BLINE-750-GNG": "Ginger Splash 750ml bottle",
    # Keg / draft
    "JUN-K18": "On Tap",
}

# Canonical codes stored in productCodes (original-ish, not uppercased BLine)
LABEL_TO_CODE = {
    "Wildflower 500g": "B-WFW-500",
    "Clover 500g": "B-CLV-500",
    "Creamed 500g": "B-CCW-500",
    "Wildflower 1kg": "A-WFW-1K",
    "Clover 1kg": "A-CLV-1K",
    "Creamed 1kg": "A-CCW-1K",
    "Bulk": "BULK",
    "Mermaid Tears 473ml": "BLine-473-MER",
    "Earl Grey 473ml": "BLine-473-ERL",
    "Currantly Hip 473ml": "BLine-473-CUR",
    "Ginger Splash 473ml": "BLine-473-GNG",
    "Mermaid Tears 750ml": "BLine-750-MER",
    "Earl Grey 750ml": "BLine-750-ERL",
    "Currantly Hip 750ml": "BLine-750-CUR",
    "Ginger Splash 750ml": "BLine-750-GNG",
    "On Tap": "Jun-k18",
}

BULK_RE = re.compile(r"^H-[A-Z]+-(15000|BK)$", re.I)
CRF_RE = re.compile(r"^CRF", re.I)
EMPRESS_RE = re.compile(r"EMPRESS|29\s*G", re.I)
UNIT_LEAD_RE = re.compile(
    r"^(?:unit\s+)?#?\s*\d+\s*[-–,]\s*",
    re.I,
)
UNIT_TRAIL_RE = re.compile(r"\s+#\s?\d+\s*$", re.I)
UNIT_HASH_COMMA_RE = re.compile(r"^#\s*\d+\s*,\s*", re.I)

EXCLUDE_NAME_RE = re.compile(
    r"grifflyn|electric inc|contractor",
    re.I,
)

ADDRESS_OVERRIDES = {
    "Tru Value Mayne": ("472 Village Bay Rd", "Mayne Island", "British Columbia", "V0N 2J2"),
    "Tru Value Foods (Mayne Island)": ("472 Village Bay Rd", "Mayne Island", "British Columbia", "V0N 2J2"),
    "Peppers Foods": ("3829 Cadboro Bay Rd", "Victoria", "British Columbia", "V8N 4G1"),
    "Thrifty Foods Wallace": ("7860 Wallace Dr", "Central Saanich", "British Columbia", "V8M 2B3"),
    "Thrifty Foods (08) Colwood": ("1860 Island Hwy", "Colwood", "British Columbia", "V9B 2V3"),
    "Thrifty Foods (09) Broadmead": ("777 Royal Oak Dr", "Saanich", "British Columbia", "V8X 4V1"),
    "Thrifty Foods Admirals": ("1495 Admirals Rd", "View Royal", "British Columbia", "V9A 2P3"),
    "Thrifty Foods Sidney": ("9810 Seventh St", "Sidney", "British Columbia", "V8L 2Y7"),
    "Market On Millstream": ("2401 Millstream Rd", "Langford", "British Columbia", "V9B 6C6"),
    "Health Essentials": ("300 Gorge Rd W #101", "Victoria", "British Columbia", "V9A 1M8"),
    "Fairway (Mckenzie)": ("1521 McKenzie Ave", "Saanich", "British Columbia", "V8N 1N4"),
    "Red Barn Sidney": ("10330 McDonald Park Rd", "Sidney", "British Columbia", "V8L 2L5"),
    "Country Bee Honey Farm": ("6440 W Saanich Rd", "Saanichton", "British Columbia", ""),
    "Deep Cove Market": ("10990 West Saanich Rd", "North Saanich", "British Columbia", "V8L 5P5"),
    "Butchart Gardens": ("800 Benvenuto Ave", "Brentwood Bay", "British Columbia", "V8M 1J8"),
    "Fernwood General Store": ("1308 Gladstone Ave", "Victoria", "British Columbia", "V8R 1S1"),
    # FreshBooks often labels Greater Victoria stores as city=Victoria; pin each to the real municipality.
    "Country Grocer (Royal Oak)": ("4420 W Saanich Rd", "Saanich", "British Columbia", "V8Z 3E9"),
    "Country Grocer (Esquimalt)": ("1153 Esquimalt Rd", "Esquimalt", "British Columbia", "V9A 3N7"),
    "Fairway (Goldstream)": ("772 Goldstream Ave", "Langford", "British Columbia", "V9B 2X3"),
    "Fairway (Gorge)": ("272 Gorge Rd W", "Saanich", "British Columbia", "V9A 1M6"),
    "Fairway (Oak Bay)": ("2187 Oak Bay Ave", "Oak Bay", "British Columbia", "V8R 1G1"),
    "Fairway (Shelbourne)": ("3651 Shelbourne St", "Saanich", "British Columbia", "V8P 5E3"),
    "Fairway (Sidney)": ("2531 Beacon Ave", "Sidney", "British Columbia", "V8L 1Y2"),
    "Fairway (West Saanich)": ("7108 W Saanich Rd", "Central Saanich", "British Columbia", "V8M 1P8"),
    "Fickle Fig Farm Market": ("1780 Mills Rd", "North Saanich", "British Columbia", "V8L 5S9"),
    "Flying Dutchman Market": ("4569 William Head Rd", "Metchosin", "British Columbia", "V9C 3Y6"),
    "Old Farm Market - Oak Bay": ("2585 Cadboro Bay Rd", "Oak Bay", "British Columbia", "V8R 5J1"),
    "Old Farm Market - Duncan": ("5164 Francis St", "Duncan", "British Columbia", "V0R 2C0"),
    "Red Barn Brookside": ("611 Brookside Rd", "Colwood", "British Columbia", "V9C 0C3"),
    "Red Barn Market (Matticks Farm)": ("5325 Cordova Bay Rd", "Saanich", "British Columbia", "V8Y 2L3"),
    "Red Barn - Esquimalt": ("1310 Esquimalt Rd", "Esquimalt", "British Columbia", "V9A 3P6"),
    "Red Barn - Oak Bay": ("1933 Oak Bay Ave", "Oak Bay", "British Columbia", "V8R 1C8"),
    "Red Barn - West Saanich": ("5550 W Saanich Rd", "Saanich", "British Columbia", ""),
    "Rootcellar Mckenzie": ("1286 McKenzie Ave", "Saanich", "British Columbia", "V8P 5P2"),
    "SAVE ON Beacon (428)": ("2345 Beacon Ave", "Sidney", "British Columbia", "V8L 1W9"),
    "SAVE ON Blanshard (504)": ("3510 Blanshard St", "Saanich", "British Columbia", "V8X 1W3"),
    "SAVE ON McCallum (553)": ("759 McCallum Rd", "Langford", "British Columbia", "V9B 6A2"),
    "SAVE ON Tillicum (532)": ("3170 Tillicum Rd", "Saanich", "British Columbia", "V9A 7C5"),
    "SAVE ON Wilson  (403)": ("172 Wilson St", "Victoria", "British Columbia", "V9A 7N6"),
    "SAVE ON Foul Bay (816)": ("1950 Foul Bay Rd", "Oak Bay", "British Columbia", "V8R 5A7"),
    "Thrifty Foods Belmont": ("3011 Merchant Way", "Langford", "British Columbia", "V9B 2M9"),
    "Thrifty Foods Tuscany": ("1626 McKenzie Ave", "Saanich", "British Columbia", "V8N 1A5"),
    "Thrifty Foods (13) Cloverdale": ("3475 Quadra St", "Saanich", "British Columbia", ""),
    "Dan's Farm & Country Market": ("2030 Bear Hill Rd", "Central Saanich", "British Columbia", "V8M 1X7"),
    "Silver Rill Corn": ("7117 Central Saanich Rd", "Central Saanich", "British Columbia", "V8M 1Y3"),
    "Co-op Food Store": ("2132 Keating Cross Rd", "Central Saanich", "British Columbia", "V8M 2A6"),
    "Heart Pharmacy": ("1594 Fairfield Rd", "Victoria", "British Columbia", ""),
    "Nootka Rose": ("4480 Happy Valley Rd", "Metchosin", "British Columbia", ""),
    "Save on Colwood": ("1913 Sooke Rd", "Colwood", "British Columbia", "V9B 1V9"),
    "Tru Value Mayne": ("472 Village Bay Rd", "Mayne Island", "British Columbia", ""),
}

CITY_FIX = {
    "vic": "Victoria",
    "victoria": "Victoria",
    "saanichton, bc v8m 2a6": "Saanichton",
    "salt spring": "Salt Spring Island",
}

TITLE_FIX = {
    "Country Grocer - Chemanus": "Country Grocer Chemainus",
    "McLennans island meat and seafood": "McLennan's Island Meat and Seafood",
    "SAVE ON Beacon (428)": "Save-On-Foods Beacon",
    "SAVE ON Blanshard (504)": "Save-On-Foods Blanshard",
    "SAVE ON Foul Bay (816)": "Save-On-Foods Foul Bay",
    "SAVE ON McCallum (553)": "Save-On-Foods McCallum",
    "SAVE ON Pandora (281)": "Save-On-Foods Pandora",
    "SAVE ON Tillicum (532)": "Save-On-Foods Tillicum",
    "SAVE ON Wilson  (403)": "Save-On-Foods Wilson",
    "Save on Colwood": "Save-On-Foods Colwood",
}


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def normalize_code(raw: str) -> str:
    part = raw
    for sep in (" — ", " – ", " - ", "—"):
        if sep in part:
            part = part.split(sep, 1)[0]
            break
    part = part.strip()
    part = re.sub(r"\s+", "", part)
    return part


def map_code(code: str) -> str | None:
    if not code:
        return None
    if CRF_RE.match(code):
        return None
    if EMPRESS_RE.search(code):
        return None
    key = code.upper()
    if key in CODE_TO_LABEL:
        return CODE_TO_LABEL[key]
    if BULK_RE.match(code) or key.startswith("H-") and (
        "15000" in key or key.endswith("-BK")
    ):
        return "Bulk"
    if key == "HONEY":
        return "Bulk"
    return None


def parse_products(products_field: str) -> tuple[list[str], list[str], list[str]]:
    """Return (labels, canonical_codes, raw_codes_deduped)."""
    if not products_field:
        return [], [], []
    items = [p.strip() for p in products_field.split(" | ") if p.strip()]
    seen_codes = []
    seen_set = set()
    labels_set = set()
    for item in items:
        code = normalize_code(item)
        if not code:
            continue
        key = code.upper()
        if key in seen_set:
            continue
        seen_set.add(key)
        seen_codes.append(code)
        label = map_code(code)
        if label:
            labels_set.add(label)
    labels = [p for p in PRODUCT_ORDER if p in labels_set]
    codes = [LABEL_TO_CODE[p] for p in labels]
    return labels, codes, seen_codes


def is_crf_only(raw_codes: list[str]) -> bool:
    return bool(raw_codes) and all(CRF_RE.match(c) for c in raw_codes)


def is_bulk_or_hotel_only(raw_codes: list[str]) -> bool:
    meaningful = [c for c in raw_codes if not CRF_RE.match(c)]
    if not meaningful:
        return True
    for c in meaningful:
        if map_code(c) and map_code(c) != "Bulk":
            # hotel minis map to None, so they don't count as consumer
            if EMPRESS_RE.search(c):
                continue
            return False
        if EMPRESS_RE.search(c):
            continue
        # unmapped non-bulk consumer-looking codes
        key = c.upper()
        if key.startswith("B-") or key.startswith("A-") or key.startswith("BLINE") or key.startswith("JUN"):
            return False
    return True


def usable_street(street: str) -> bool:
    s = (street or "").strip().strip(",")
    if not s:
        return False
    # Must have a digit (street number) to be walk-in locatable
    return bool(re.search(r"\d", s))


def clean_street(street: str) -> str:
    s = (street or "").strip().strip(",").strip()
    s = re.sub(r"\s+", " ", s)
    # truncated Sooke R
    if re.search(r"sooke r$", s, re.I):
        s = re.sub(r"sooke r$", "Sooke Rd", s, flags=re.I)
    # Quadra without suffix
    if re.fullmatch(r"\d+\s+QUADRA", s, re.I):
        s = re.sub(r"QUADRA", "Quadra St", s, flags=re.I)
    if re.fullmatch(r"\d+\s+Foul Bay", s, re.I):
        s = s + " Rd"
    if re.fullmatch(r"\d+\s+Pandora", s, re.I):
        s = s + " Ave"
    # title-ish
    if s.isupper() or s.islower():
        s = s.title()
    return s


def street_without_unit(street: str) -> str:
    s = clean_street(street)
    s = UNIT_HASH_COMMA_RE.sub("", s)
    s = UNIT_LEAD_RE.sub("", s)
    s = UNIT_TRAIL_RE.sub("", s)
    # 103-6661 Sooke Rd or 15-1594 Fairfield
    s = re.sub(r"^(\d+)-\s*(\d+\s+)", r"\2", s)
    s = re.sub(r"^#\s*\d+\s*-\s*", "", s)
    return s.strip()


def clean_city(city: str, name: str, postal: str) -> str:
    c = (city or "").strip()
    c = re.sub(r",?\s*BC\b.*", "", c, flags=re.I).strip()
    c = c.strip(",")
    key = c.lower()
    if key in CITY_FIX:
        return CITY_FIX[key]
    if not c:
        n = name.lower()
        if "sidney" in n:
            return "Sidney"
        if "colwood" in n:
            return "Colwood"
        if "duncan" in n:
            return "Duncan"
        if "fairfield" in n or "heart pharmacy" in n:
            return "Victoria"
        if "happy valley" in n or "nootka" in n:
            return "Metchosin"
        if postal.upper().startswith("V9B"):
            return "Victoria"
        if postal.upper().startswith("V0R"):
            return "Duncan"
        return ""
    # Title case if all lower/upper
    if c.islower() or c.isupper():
        c = c.title()
    return c


def clean_postal(postal: str) -> str:
    p = (postal or "").strip()
    p = re.sub(r"^BC\s+", "", p, flags=re.I)
    p = p.replace(" ", "").upper()
    if re.fullmatch(r"[A-Z]\d[A-Z]\d[A-Z]\d", p):
        return f"{p[:3]} {p[3:]}"
    return (postal or "").strip()


def clean_province(prov: str) -> str:
    p = (prov or "").strip()
    if p.lower() in {"bc", "b.c.", "b.c", "british columbia", "state", ""}:
        return "British Columbia"
    return p or "British Columbia"


def should_exclude_name(name: str) -> bool:
    return bool(EXCLUDE_NAME_RE.search(name or ""))


def nominatim_search(query: str, cache: dict) -> dict | None:
    if query in cache:
        hit = cache[query]
        if hit is None or hit.get("lat") is None:
            return None
        return hit
    params = {
        "q": query,
        "format": "json",
        "limit": "1",
        "countrycodes": "ca",
        "addressdetails": "1",
        "viewbox": VIEWBOX,
        "bounded": "0",
    }
    url = NOMINATIM + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  nominatim error for {query!r}: {e}")
        cache[query] = None
        time.sleep(SLEEP)
        return None
    time.sleep(SLEEP)
    if not data:
        cache[query] = None
        save_json(CACHE_PATH, cache)
        return None
    rec = data[0]
    # Bias check: reject results clearly off Vancouver Island / south BC coast
    lat = float(rec["lat"])
    lng = float(rec["lon"])
    addr = rec.get("address") or {}
    state = (addr.get("state") or "").lower()
    result = {
        "lat": lat,
        "lng": lng,
        "display_name": rec.get("display_name"),
        "state": addr.get("state"),
        "query": query,
    }
    if state and "british columbia" not in state and "bc" not in state:
        print(f"  off-province result for {query!r}: {rec.get('display_name')}")
        cache[query] = None
        save_json(CACHE_PATH, cache)
        return None
    # Rough BC south-island window
    if not (47.8 <= lat <= 51.2 and -129.0 <= lng <= -122.5):
        print(f"  out-of-bounds for {query!r}: {lat},{lng} {rec.get('display_name')}")
        cache[query] = None
        save_json(CACHE_PATH, cache)
        return None
    cache[query] = result
    save_json(CACHE_PATH, cache)
    return result


def geocode_store(street: str, city: str, province: str, postal: str, cache: dict) -> tuple[dict | None, list[str]]:
    attempts = []
    street_c = clean_street(street)
    city_c = city
    prov_c = clean_province(province)
    post_c = clean_postal(postal)

    queries = []
    # 1. full
    parts = [street_c, city_c, prov_c, post_c, "Canada"]
    queries.append(", ".join(p for p in parts if p))
    # 2. without unit
    no_unit = street_without_unit(street)
    if no_unit and no_unit.lower() != street_c.lower():
        parts = [no_unit, city_c, prov_c, post_c, "Canada"]
        queries.append(", ".join(p for p in parts if p))
        parts = [no_unit, city_c, prov_c, "Canada"]
        queries.append(", ".join(p for p in parts if p))
    # 3. street + city + province (no postal — postal typos hurt)
    parts = [no_unit or street_c, city_c, prov_c, "Canada"]
    q = ", ".join(p for p in parts if p)
    if q not in queries:
        queries.append(q)
    # 4. city + postal
    if city_c and post_c:
        queries.append(f"{city_c}, {post_c}, {prov_c}, Canada")
    elif post_c:
        queries.append(f"{post_c}, {prov_c}, Canada")

    seen = set()
    unique = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    for q in unique:
        attempts.append(q)
        hit = nominatim_search(q, cache)
        if hit:
            return hit, attempts
    return None, attempts


def display_address(street: str, street2: str) -> str:
    s = clean_street(street)
    s2 = (street2 or "").strip().strip(",")
    if s2:
        return f"{s}, {s2}"
    return s


OWNED = [
    {
        "id": "shop-sidney",
        "name": "Babe's Honey Sidney",
        "type": "shop",
        "address": "#7, 2042 Mills Rd W",
        "city": "Sidney",
        "postal": "",
        "hours": "Wed–Sat 10am–5pm",
        "phone": "250-658-8319",
        "products": [
            "Wildflower 500g",
            "Clover 500g",
            "Creamed 500g",
            "Wildflower 1kg",
            "Clover 1kg",
            "Creamed 1kg",
            "Mermaid Tears 473ml",
            "Earl Grey 473ml",
            "Currantly Hip 473ml",
            "Ginger Splash 473ml",
            "Mermaid Tears 750ml",
            "Earl Grey 750ml",
            "Currantly Hip 750ml",
            "Ginger Splash 750ml",
            "On Tap",
        ],
        "productCodes": [
            "B-WFW-500",
            "B-CLV-500",
            "B-CCW-500",
            "A-WFW-1K",
            "A-CLV-1K",
            "A-CCW-1K",
            "BLine-473-MER",
            "BLine-473-ERL",
            "BLine-473-CUR",
            "BLine-473-GNG",
            "BLine-750-MER",
            "BLine-750-ERL",
            "BLine-750-CUR",
            "BLine-750-GNG",
            "Jun-k18",
        ],
        "lastInvoice": None,
        "notes": "Full lineup: honey refills, growler fills, cans, bottles, and tasting.",
        "geocode_street": "2042 Mills Rd W",
        "geocode_city": "Sidney",
        "geocode_province": "British Columbia",
        "geocode_postal": "",
    },
    {
        "id": "shop-galey",
        "name": "Babe's at Galey Farms Market",
        "type": "shop",
        "address": "4150 Blenkinsop Rd",
        "city": "Saanich",
        "postal": "V8X 2C4",
        "hours": "Daily 9am–5:30pm",
        "phone": "",
        "products": [
            "Wildflower 500g",
            "Clover 500g",
            "Creamed 500g",
            "Wildflower 1kg",
            "Clover 1kg",
            "Creamed 1kg",
            "Bulk",
            "Mermaid Tears 473ml",
            "Earl Grey 473ml",
            "Currantly Hip 473ml",
            "Ginger Splash 473ml",
            "Mermaid Tears 750ml",
            "Earl Grey 750ml",
            "Currantly Hip 750ml",
            "Ginger Splash 750ml",
        ],
        "productCodes": [
            "B-WFW-500",
            "B-CLV-500",
            "B-CCW-500",
            "A-WFW-1K",
            "A-CLV-1K",
            "A-CCW-1K",
            "BULK",
            "BLine-473-MER",
            "BLine-473-ERL",
            "BLine-473-CUR",
            "BLine-473-GNG",
            "BLine-750-MER",
            "BLine-750-ERL",
            "BLine-750-CUR",
            "BLine-750-GNG",
        ],
        "lastInvoice": None,
        "notes": "Look for Babe's section inside Galey Farms Market. Honey (including 3kg) and Bee Line drinks in two coolers. No refills.",
        "geocode_street": "4150 Blenkinsop Rd",
        "geocode_city": "Saanich",
        "geocode_province": "British Columbia",
        "geocode_postal": "V8X 2C4",
    },
]


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    cache = load_cache()
    excluded = []
    candidates = []

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"CSV rows: {len(rows)}")

    for row in rows:
        name = (row.get("organization") or "").strip()
        street = (row.get("street") or "").strip()
        street2 = (row.get("street2") or "").strip()
        city_raw = (row.get("city") or "").strip()
        province = (row.get("province") or "").strip()
        postal = (row.get("postal") or "").strip()
        if name in ADDRESS_OVERRIDES:
            o_street, o_city, o_prov, o_postal = ADDRESS_OVERRIDES[name]
            # Overrides always win — FreshBooks often has blank street for key retailers.
            street = o_street
            city_raw = o_city
            province = o_prov
            postal = o_postal
        cid = (row.get("customerid") or "").strip()
        last_inv = (row.get("last_invoice") or "").strip() or None
        labels, codes, raw_codes = parse_products(row.get("products") or "")

        reason = None
        if should_exclude_name(name):
            reason = "contractor/office (not a store)"
        elif not usable_street(street):
            reason = "no usable street address"
        elif is_bulk_or_hotel_only(raw_codes):
            reason = "only bulk pails / hotel minis / no consumer SKUs"
        elif not labels:
            reason = "no consumer-facing products after CRF/bulk filter"

        if reason:
            excluded.append({"id": cid, "name": name, "reason": reason, "street": street, "city": city_raw})
            continue

        city = clean_city(city_raw, name, postal)
        postal_c = clean_postal(postal)
        display_name = TITLE_FIX.get(name, name)
        candidates.append(
            {
                "id": cid,
                "name": display_name,
                "type": "retailer",
                "address": display_address(street, street2),
                "city": city,
                "postal": postal_c,
                "hours": "",
                "phone": "",
                "products": labels,
                "productCodes": codes,
                "lastInvoice": last_inv,
                "notes": "",
                "geocode_street": street,
                "geocode_city": city,
                "geocode_province": clean_province(province),
                "geocode_postal": postal_c,
                "_raw_name": name,
            }
        )

    # Dedupe by normalized address (Red Barn Brookside x2)
    by_addr = {}
    deduped = []
    for st in candidates:
        key = re.sub(r"[^a-z0-9]", "", (street_without_unit(st["address"]) + st["city"]).lower())
        if key in by_addr:
            prev = by_addr[key]
            excluded.append(
                {
                    "id": st["id"],
                    "name": st["name"],
                    "reason": f"duplicate of {prev['name']} ({prev['id']}) at same address",
                    "street": st["address"],
                    "city": st["city"],
                }
            )
            # merge products into the keeper
            merged = list(dict.fromkeys(prev["products"] + st["products"]))
            prev["products"] = [p for p in PRODUCT_ORDER if p in merged]
            prev["productCodes"] = [LABEL_TO_CODE[p] for p in prev["products"]]
            if (st.get("lastInvoice") or "") > (prev.get("lastInvoice") or ""):
                prev["lastInvoice"] = st["lastInvoice"]
            continue
        by_addr[key] = st
        deduped.append(st)

    stores = []
    failures = []

    to_geocode = OWNED + deduped
    print(f"To include (pre-geocode): {len(to_geocode)}  excluded: {len(excluded)}")

    for i, st in enumerate(to_geocode, 1):
        print(f"[{i}/{len(to_geocode)}] geocoding {st['name']} — {st['address']}, {st['city']}")
        hit, attempts = geocode_store(
            st["geocode_street"],
            st["geocode_city"],
            st["geocode_province"],
            st["geocode_postal"],
            cache,
        )
        rec = {
            "id": st["id"],
            "name": st["name"],
            "type": st["type"],
            "address": st["address"],
            "city": st["city"],
            "postal": st["postal"],
            "lat": None,
            "lng": None,
            "hours": st.get("hours") or "",
            "phone": st.get("phone") or "",
            "products": st["products"],
            "productCodes": st["productCodes"],
            "lastInvoice": st.get("lastInvoice"),
            "notes": st.get("notes") or "",
        }
        if hit:
            rec["lat"] = round(hit["lat"], 6)
            rec["lng"] = round(hit["lng"], 6)
            print(f"  OK {rec['lat']},{rec['lng']}  ({hit.get('display_name','')[:80]})")
        else:
            failures.append(
                {
                    "id": st["id"],
                    "name": st["name"],
                    "address": st["address"],
                    "city": st["city"],
                    "postal": st["postal"],
                    "attempts": attempts,
                }
            )
            print("  FAIL")
        stores.append(rec)

    save_json(CACHE_PATH, cache)
    save_json(FAIL_PATH, failures)
    save_json(STORES_PATH, stores)
    save_json(EXCLUDED_PATH, excluded)

    ok = sum(1 for s in stores if s["lat"] is not None)
    print("\n=== SUMMARY ===")
    print(f"CSV rows: {len(rows)}")
    print(f"Excluded: {len(excluded)}")
    print(f"Included stores: {len(stores)} (owned {len(OWNED)} + retailers {len(deduped)})")
    print(f"Geocode OK: {ok}  FAIL: {len(failures)}")
    print("Excluded names:")
    for e in excluded:
        print(f"  - {e['name']}: {e['reason']}")
    if failures:
        print("Geocode failures:")
        for f in failures:
            print(f"  - {f['name']}: {f['address']}, {f['city']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Re-geocode stores with structured Nominatim, rejecting city centroids."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path("/workspace/locator")
STORES_PATH = ROOT / "stores.json"
CACHE_PATH = ROOT / "geocode-cache.json"
FAIL_PATH = ROOT / "geocode-failures.json"

UA = "BabesHoneyFarmLocator/1.0 (brandon@babes-honey-farm.com)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
SLEEP = 1.1
VIEWBOX = "-128.9,48.0,-122.7,51.1"

REJECT_PLACE = {
    "city", "town", "municipality", "island", "county", "state",
    "region", "province", "village", "hamlet", "suburb", "neighbourhood",
    "quarter", "city_block",
}

FSA_CITIES = {
    "V8L": ["Sidney", "North Saanich"],
    "V8M": ["Central Saanich", "Saanichton", "Brentwood Bay"],
    "V8X": ["Saanich", "Victoria"],
    "V8Y": ["Saanich"],
    "V8Z": ["Saanich"],
    "V8N": ["Saanich"],
    "V8P": ["Saanich"],
    "V8R": ["Oak Bay", "Victoria"],
    "V8S": ["Victoria", "Oak Bay"],
    "V8T": ["Victoria"],
    "V8V": ["Victoria"],
    "V8W": ["Victoria"],
    "V9A": ["Esquimalt", "Victoria"],
    "V9B": ["Langford", "Colwood", "View Royal"],
    "V9C": ["Colwood", "Langford", "Metchosin"],
    "V9G": ["Ladysmith"],
    "V9L": ["Duncan", "North Cowichan"],
    "V9Z": ["Sooke"],
    "V8K": ["Salt Spring Island"],
    "V9X": ["Cedar", "Nanaimo"],
    "V0N": ["Mayne", "Mayne Island", "Pender Island"],
    "V0R": ["North Cowichan", "Duncan", "Crofton", "Cobble Hill"],
}

NAME_HINTS = [
    (r"sidney|beacon", ["Sidney", "North Saanich"]),
    (r"fickle fig|mills rd", ["North Saanich", "Sidney"]),
    (r"galey|blenkinsop", ["Saanich"]),
    (r"colwood|brookside", ["Colwood"]),
    (r"goldstream|millstream|mccallum|belmont|merchant", ["Langford"]),
    (r"esquimalt", ["Esquimalt"]),
    (r"admirals", ["View Royal", "Esquimalt"]),
    (r"oak bay|cadboro", ["Oak Bay", "Saanich"]),
    (r"royal oak|mattick|cordova|mckenzie|shelbourne|broadmead|tuscany|cloverdale|blanshard|tillicum", ["Saanich", "Central Saanich"]),
    (r"wallace|keating|bear hill|silver rill", ["Central Saanich", "Saanichton"]),
    (r"west saanich|w saanich", ["Saanich", "Central Saanich", "Brentwood Bay"]),
    (r"flying dutchman|william head|happy valley|nootka", ["Metchosin"]),
    (r"mayne|village bay", ["Mayne Island", "Mayne"]),
    (r"pender", ["Pender Island"]),
    (r"salt spring|saltspring|ganges|purvis", ["Salt Spring Island"]),
    (r"francis|crofton", ["Crofton", "North Cowichan", "Duncan"]),
    (r"chemainus", ["Chemainus", "North Cowichan"]),
    (r"sooke", ["Sooke"]),
    (r"langford", ["Langford"]),
    (r"nanaimo|bowen|chase river|dufferin", ["Nanaimo"]),
    (r"cedar", ["Cedar", "Nanaimo"]),
    (r"duncan", ["Duncan", "North Cowichan"]),
    (r"ladysmith", ["Ladysmith"]),
    (r"lake cowichan", ["Lake Cowichan"]),
    (r"cobble hill", ["Cobble Hill"]),
    (r"saanichton|keating|bear hill|silver rill|co-op", ["Central Saanich", "Saanichton", "Saanich"]),
    (r"wilson st", ["Esquimalt"]),
    (r"foul bay", ["Oak Bay", "Victoria"]),
]


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def expand_street(street: str) -> str:
    s = (street or "").strip().strip(",")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^(?:unit\s+)?#?\s*\d+\s*[-–,]\s*", "", s, flags=re.I)
    s = re.sub(r"^#\s*\d+\s*,\s*", "", s)
    s = re.sub(r"^(\d+)-\s*(\d+\s+)", r"\2", s)
    s = re.sub(r"\s+#\s?\d+\s*$", "", s)
    # 711A -> 711
    s = re.sub(r"^(\d+)[A-Z]\b", r"\1", s, flags=re.I)
    repl = [
        (r"\bTrans-Canada Hwy\b", "Trans-Canada Highway"),
        (r"\bTrans-Canada\b", "Trans-Canada Highway"),
        (r"\bSooke R\b", "Sooke Road"),
        (r"\bW Saanich\b", "West Saanich"),
        (r"\bE Saanich\b", "East Saanich"),
        (r"\bGorge Rd W\b", "Gorge Road West"),
        (r"\bGorge Rd E\b", "Gorge Road East"),
        (r"\b1st\b", "First"),
        (r"\b2nd\b", "Second"),
        (r"\b3rd\b", "Third"),
        (r"\bRd\b", "Road"),
        (r"\bSt\b", "Street"),
        (r"\bAve\b", "Avenue"),
        (r"\bDr\b", "Drive"),
        (r"\bHwy\b", "Highway"),
        (r"\bLn\b", "Lane"),
        (r"\bWy\b", "Way"),
        (r"\bCres\b", "Crescent"),
        (r"\bBlvd\b", "Boulevard"),
    ]
    for pat, rep in repl:
        s = re.sub(pat, rep, s, flags=re.I)
    s = re.sub(r"\bW\b", "West", s)
    s = re.sub(r"\bE\b", "East", s)
    s = re.sub(r"\bN\b", "North", s)
    s = re.sub(r"\bS\b", "South", s)
    return s.strip()


def housenumber(street: str) -> str:
    m = re.search(r"(\d+)", expand_street(street) or street or "")
    return m.group(1) if m else ""


def candidate_cities(store: dict) -> list[str]:
    cities = []
    def add(c):
        if c and c not in cities:
            cities.append(c)
    name = f"{store.get('name','')} {store.get('address','')}".lower()
    for pat, opts in NAME_HINTS:
        if re.search(pat, name, re.I):
            for o in opts:
                add(o)
    postal = (store.get("postal") or "").replace(" ", "").upper()
    fsa = postal[:3] if len(postal) >= 3 else ""
    for o in FSA_CITIES.get(fsa, []):
        add(o)
    add(store.get("city") or "")
    add("Victoria")
    add("Saanich")
    return cities


def nominatim(params: dict, cache: dict):
    # stable key
    key = "v2:" + urllib.parse.urlencode(sorted(params.items()))
    if key in cache:
        return cache[key]
    q = dict(params)
    q.update({
        "format": "json",
        "limit": "5",
        "addressdetails": "1",
        "countrycodes": "ca",
        "viewbox": VIEWBOX,
        "bounded": "0",
    })
    url = NOMINATIM + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("    error", e)
        data = []
    time.sleep(SLEEP)
    cache[key] = data
    save_json(CACHE_PATH, cache)
    return data


def score(rec: dict, number: str, want_city: str) -> int:
    cls = rec.get("class") or ""
    typ = rec.get("type") or ""
    if cls == "place" and typ in REJECT_PLACE:
        return -100
    lat = float(rec["lat"])
    lng = float(rec["lon"])
    if not (47.8 <= lat <= 51.2 and -129.0 <= lng <= -122.5):
        return -100
    addr = rec.get("address") or {}
    state = (addr.get("state") or "").lower()
    if state and "british columbia" not in state:
        return -100
    display = rec.get("display_name") or ""
    s = 0
    if cls == "shop":
        s += 60
    elif cls == "amenity":
        s += 50
    elif cls == "building":
        s += 45
    elif cls == "place" and typ == "house":
        s += 45
    elif cls == "landuse" and typ == "retail":
        s += 40
    elif cls == "highway" and number and number in display:
        s += 18
    elif cls == "highway":
        s += 6
    else:
        s += 8
    if number and number in display:
        s += 25
    # municipality hint
    blob = display.lower()
    if want_city and want_city.lower() in blob:
        s += 8
    return s


def pick(results, number, want_city):
    ranked = []
    for rec in results or []:
        sc = score(rec, number, want_city)
        if sc > 0:
            ranked.append((sc, rec))
    ranked.sort(key=lambda x: -x[0])
    return ranked[0] if ranked else None


def geocode_one(store, cache):
    street = expand_street(store["address"])
    number = housenumber(store["address"])
    cities = candidate_cities(store)
    postal = store.get("postal") or ""
    best = None  # (score, rec, query)

    # 1. structured street + city
    for city in cities:
        data = nominatim({"street": street, "city": city, "state": "British Columbia", "country": "Canada"}, cache)
        hit = pick(data, number, city)
        if hit and (best is None or hit[0] > best[0]):
            best = (hit[0], hit[1], f"structured:{street}/{city}")
        if best and best[0] >= 70:
            return best

    # 2. free-form full
    for city in cities[:4]:
        q = ", ".join(p for p in [street, city, "British Columbia", postal, "Canada"] if p)
        data = nominatim({"q": q}, cache)
        hit = pick(data, number, city)
        if hit and (best is None or hit[0] > best[0]):
            best = (hit[0], hit[1], f"q:{q}")
        if best and best[0] >= 70:
            return best

    # 3. store name + street + first city
    name = re.sub(r"\s*\(.*\)", "", store["name"]).strip()
    city0 = cities[0] if cities else "British Columbia"
    q = f"{name}, {street}, {city0}, British Columbia, Canada"
    data = nominatim({"q": q}, cache)
    hit = pick(data, number, city0)
    if hit and (best is None or hit[0] > best[0]):
        best = (hit[0], hit[1], f"name:{q}")

    # 4. street + province only (no city)
    q = f"{street}, British Columbia, Canada"
    data = nominatim({"q": q}, cache)
    hit = pick(data, number, city0)
    if hit and (best is None or hit[0] > best[0]):
        best = (hit[0], hit[1], f"nocity:{q}")

    # 5. city + postal last, but only if it is NOT a city centroid
    if postal:
        q = f"{cities[0] if cities else ''}, {postal}, British Columbia, Canada".strip(", ")
        data = nominatim({"q": q}, cache)
        hit = pick(data, number, cities[0] if cities else "")
        if hit and hit[0] >= 20 and (best is None or hit[0] > best[0]):
            best = (hit[0], hit[1], f"postal:{q}")

    return best


DISPLAY_NAME = {
    "Village Food Market (Logan Group)": "Village Food Market",
    "Thrifty Foods (08) Colwood": "Thrifty Foods Colwood",
    "Thrifty Foods (09) Broadmead": "Thrifty Foods Broadmead",
    "Thrifty Foods (13) Cloverdale": "Thrifty Foods Cloverdale",
    "Rootcellar (cook st)": "The Root Cellar Cook Street",
    "Rootcellar Mckenzie": "The Root Cellar McKenzie",
    "Country Grocer (Esquimalt)": "Country Grocer Esquimalt",
    "Country Grocer (Royal Oak)": "Country Grocer Royal Oak",
    "Fairway (Sidney)": "Fairway Market Sidney",
    "Fairway (Goldstream)": "Fairway Market Goldstream",
    "Fairway (Gorge)": "Fairway Market Gorge",
    "Fairway (Oak Bay)": "Fairway Market Oak Bay",
    "Fairway (Quadra)": "Fairway Market Quadra",
    "Fairway (Shelbourne)": "Fairway Market Shelbourne",
    "Fairway (West Saanich)": "Fairway Market West Saanich",
    "Red Barn Market (Matticks Farm)": "Red Barn Market Mattick's Farm",
    "Red Barn Brookside": "Red Barn Market Brookside",
    "Red Barn - Esquimalt": "Red Barn Market Esquimalt",
    "Red Barn - James Bay": "Red Barn Market James Bay",
    "Red Barn - Oak Bay": "Red Barn Market Oak Bay",
    "Red Barn - West Saanich": "Red Barn Market West Saanich",
    "Lifestyle Markets Cook St.": "Lifestyle Markets Cook Street",
    "Mt Douglas Market": "Mount Douglas Market",
    "Caffe Fantastico - Harbour Rd": "Caffe Fantastico Harbour Road",
    "Caffe Fantastico - Kings Rd": "Caffe Fantastico Kings Road",
    "Forbes Pharmacy Fort Street": "Forbes Pharmacy (Jubilee on Fort)",
    "Heart Pharmacy": "Heart Pharmacy Fairfield",
    "Thrifty Foods Salt Spring": "Thrifty Foods Salt Spring",
    "Country Grocer - Duncan": "Country Grocer Duncan",
    "Country Grocer - Ladysmith": "Country Grocer Ladysmith",
    "Country Grocer Saltspring": "Country Grocer Salt Spring",
    "Tru Value Foods - Pender": "Tru Value Foods Pender",
    "Old Farm Market - Oak Bay": "Old Farm Market Oak Bay",
    "Old Farm Market - Duncan": "Old Farm Market Crofton",
    "Save-On-Foods Beacon": "Save-On-Foods Sidney",
    "Thrifty Foods Sidney": "Thrifty Foods Sidney",
    "Co-op Food Store": "Peninsula Co-op Keating",
}


def osm_city(rec):
    addr = rec.get("address") or {}
    for k in ("town", "city", "village", "municipality", "city_district", "suburb"):
        v = addr.get(k)
        if v and v.lower() not in {"capital regional district", "cowichan valley regional district"}:
            # skip CRD neighbourhood-only if we have town
            if k == "suburb":
                continue
            return v
    return None


def main():
    stores = load_json(STORES_PATH, [])
    cache = load_json(CACHE_PATH, {})
    failures = []
    ok = 0
    for i, st in enumerate(stores, 1):
        if st["name"] in DISPLAY_NAME:
            st["name"] = DISPLAY_NAME[st["name"]]
        print(f"[{i}/{len(stores)}] {st['name']} — {st['address']}, {st['city']}")
        hit = geocode_one(st, cache)
        if not hit:
            st["lat"] = None
            st["lng"] = None
            failures.append({
                "id": st["id"],
                "name": st["name"],
                "address": st["address"],
                "city": st["city"],
                "postal": st["postal"],
                "attempts": ["structured+freeform+name+nocity+postal"],
            })
            print("  FAIL")
            continue
        sc, rec, how = hit
        st["lat"] = round(float(rec["lat"]), 6)
        st["lng"] = round(float(rec["lon"]), 6)
        city = osm_city(rec)
        if city and st["type"] != "shop":
            # keep owned-shop cities as specified; refine retailers
            if st.get("city") in {"", "Victoria", "vic"} or city.lower() not in {"victoria"}:
                # don't overwrite a specific CSV city with Victoria
                if not (st.get("city") and st["city"] != "Victoria" and city == "Victoria"):
                    if city not in {"Capital Regional District"}:
                        st["city"] = city
        print(f"  OK {st['lat']},{st['lng']} score={sc} via {how}")
        print(f"     {rec.get('display_name','')[:100]}")
        ok += 1

    save_json(STORES_PATH, stores)
    save_json(CACHE_PATH, cache)
    save_json(FAIL_PATH, failures)
    print(f"\nGeocode OK {ok}  FAIL {len(failures)}")
    for f in failures:
        print(" ", f["name"], f["address"], f["city"])


if __name__ == "__main__":
    main()

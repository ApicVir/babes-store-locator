# Store locator geocode audit

Audit of every pin in `stores.json` / `index.html`. Re-geocoded suspects with
Nominatim (User-Agent `BabesHoneyFarmLocator/1.0 (babes-honey-farm.com)`),
structured `street` + real municipality (not blanket Victoria), ≥1.15s between
requests. City centroids were rejected. A second pass used OSM shop POIs
(Nominatim / Photon) for unique-but-wrong pins (e.g. Shelbourne stores sitting
~3 km south of the actual supermarket).

Known-good pins left untouched: Thrifty Wallace, Thrifty Colwood, Thrifty
Broadmead, Thrifty Admirals, Thrifty Sidney, Market On Millstream, Country Bee
Honey Farm, Peppers Foods.

`ADDRESS_OVERRIDES` in `build.py` and `NAME_HINTS` in `regeocode.py` were
extended so a future CSV rebuild does not collapse these pins onto the Victoria
centroid again. Do **not** run `regeocode.py` against the full file blindly — it
would overwrite already-specific pins.

## Counts

| Metric | Before | After |
|---|---:|---:|
| Stores | 93 | 93 |
| Null lat/lng | 1 | 0 |
| On known city centroid (Victoria / Duncan / Saanichton) | 20 | 0 |
| Duplicate identical-coord groups | 4 | 0 |
| Stores sharing a coord with another | 22 | 0 |
| Pins moved (lat/lng changed) | — | 34 |
| City/address-only fixes | — | 4 |
| Remaining geocode failures | — | 0 |
| `index.html` `STORES` matches `stores.json` | — | yes |

## Victoria centroid cluster (before)

These 16 stores all sat on `48.428318, -123.364953` (Nominatim city centroid
for Victoria — FreshBooks `city=Victoria` with no matching street):

- Babe's at Galey Farms Market — 4150 Blenkinsop Rd
- Country Grocer (Royal Oak) — 4420 W Saanich Rd
- Fairway (Goldstream) — 772 Goldstream Ave
- Fairway (Gorge) — 272 Gorge Rd W
- Fairway (West Saanich) — 7108 W Saanich Rd
- Fickle Fig Farm Market — 1780 Mills Rd
- Flying Dutchman Market — 4569 William Head Rd
- Old Farm Market - Oak Bay — 2585 Cadboro Bay Road
- Red Barn Brookside — 611 Brookside Rd
- Red Barn Market (Matticks Farm) — 5325 Cordova Bay Rd
- Rootcellar Mckenzie — 1286 McKenzie Ave
- Save-On-Foods Beacon — 2345 Beacon Ave
- Save-On-Foods McCallum — 759 McCallum Rd
- Thrifty Foods Belmont — 3011 Merchant Way
- Thrifty Foods Tuscany — 1626 McKenzie Ave
- Health Essentials — 300 Gorge Rd W #101

Other collapsed clusters:

- Duncan centroid `48.778687, -123.708045`: Country Grocer Duncan + Old Farm Market Duncan (the latter is in Koksilah, just south of Duncan)
- Saanichton centroid `48.592621, -123.397174`: Dan's Farm + Silver Rill Corn
- Esquimalt shared pin `48.431739, -123.394228`: Country Grocer Esquimalt + Red Barn Esquimalt (different civic numbers)

## Fixed pins (original → new)

| Store | Address / city | Old | New |
|---|---|---|---|
| Babe's at Galey Farms Market | 4150 Blenkinsop Rd, Saanich | `48.428318, -123.364953` | `48.478234, -123.356292` |
| Country Grocer - Duncan | 3288 Cowichan Lake Rd, Duncan | `48.778687, -123.708045` | `48.791086, -123.737121` |
| Country Grocer - Ladysmith | 1020 1st Ave, Ladysmith | `48.993658, -123.815796` | `48.996541, -123.822986` |
| Farm Gate Store | 568 Fernhill Road, Mayne Island | `48.850964, -123.298082` | `48.845387, -123.278183` |
| Tru Value Mayne | 472 Village Bay Rd, Mayne Island | `null` | `48.850444, -123.298511` |
| Dan's Farm & Country Market | 2030 Bear Hill Rd, Saanich | `48.592621, -123.397174` | `48.551049, -123.416752` |
| Silver Rill Corn | 7117 Central Saanich Rd, Central Saanich | `48.592621, -123.397174` | `48.575316, -123.402579` |
| Co-op Food Store | 2132 Keating Cross Rd, Central Saanich | `48.571977, -123.402332` | `48.565568, -123.412067` |
| Country Grocer (Esquimalt) | 1153 Esquimalt Rd, Esquimalt | `48.431739, -123.394228` | `48.429429, -123.411213` |
| Country Grocer (Royal Oak) | 4420 W Saanich Rd, Saanich | `48.428318, -123.364953` | `48.492293, -123.389568` |
| Fairway (Goldstream) | 772 Goldstream Ave, Langford | `48.428318, -123.364953` | `48.449203, -123.498251` |
| Fairway (Gorge) | 272 Gorge Rd W, Saanich | `48.428318, -123.364953` | `48.448547, -123.398968` |
| Fairway (Oak Bay) | 2187 Oak Bay Ave #101, Oak Bay | `48.426442, -123.323072` | `48.426376, -123.31646` |
| Fairway (Shelbourne) | 3651 Shelbourne St, Saanich | `48.43462, -123.333626` | `48.460131, -123.331959` |
| Fairway (West Saanich) | 7108 W Saanich Rd, Central Saanich | `48.428318, -123.364953` | `48.575258, -123.446383` |
| Fickle Fig Farm Market | 1780 Mills Rd, North Saanich | `48.428318, -123.364953` | `48.655785, -123.426692` |
| Flying Dutchman Market | 4569 William Head Rd, Metchosin | `48.428318, -123.364953` | `48.374393, -123.532973` |
| Mt Douglas Market | 4101 Shelbourne St, Saanich | `48.447595, -123.333263` | `48.477625, -123.333283` |
| Old Farm Market - Oak Bay | 2585 Cadboro Bay Road, Oak Bay | `48.428318, -123.364953` | `48.437946, -123.312403` |
| Red Barn - Esquimalt | 1310 Esquimalt Rd, Esquimalt | `48.431739, -123.394228` | `48.430024, -123.41738` |
| Red Barn Brookside | 611 Brookside Rd, Colwood | `48.428318, -123.364953` | `48.409163, -123.508799` |
| Red Barn Market (Matticks Farm) | 5325 Cordova Bay Rd, Saanich | `48.428318, -123.364953` | `48.529502, -123.372741` |
| Rootcellar Mckenzie | 1286 McKenzie Ave, Saanich | `48.428318, -123.364953` | `48.472533, -123.352137` |
| Save-On-Foods Beacon | 2345 Beacon Ave, Sidney | `48.428318, -123.364953` | `48.648143, -123.402325` |
| Save-On-Foods Blanshard | 3510 Blanshard St, Saanich | `48.421291, -123.363045` | `48.456581, -123.373091` |
| Save-On-Foods McCallum | 759 McCallum Rd, Langford | `48.428318, -123.364953` | `48.458855, -123.499346` |
| Save-On-Foods Tillicum | 3170 Tillicum Rd, Saanich | `48.446145, -123.387996` | `48.454854, -123.394901` |
| Save-On-Foods Wilson | 172 Wilson St, Victoria | `48.432472, -123.380776` | `48.432646, -123.380311` |
| Thrifty Foods (13) Cloverdale | 3475 Quadra St, Saanich | `48.422054, -123.360214` | `48.454804, -123.358692` |
| Thrifty Foods Belmont | 3011 Merchant Way, Langford | `48.428318, -123.364953` | `48.438122, -123.509366` |
| Thrifty Foods Tuscany | 1626 McKenzie Ave, Saanich | `48.428318, -123.364953` | `48.468944, -123.331584` |
| Health Essentials | 300 Gorge Rd W #101, Saanich | `48.428318, -123.364953` | `48.447923, -123.400767` |
| Heart Pharmacy | 1594 Fairfield Rd, Victoria | `48.418157, -123.356794` | `48.412415, -123.337687` |
| Old Farm Market - Duncan | 5164 Francis St, Duncan | `48.778687, -123.708045` | `48.760006, -123.683964` |

## City / address-only (coords unchanged)

- **Red Barn - Oak Bay**: Victoria → Oak Bay
- **Save-On-Foods Foul Bay**: Victoria → Oak Bay
- **Fairway (Mckenzie)**: Victoria → Saanich
- **Red Barn - West Saanich**: (empty) → Saanich; address `5550 W Saanich Rd, Victoria` → `5550 W Saanich Rd`

## Duplicate-coord groups remaining

None. Every store has a unique lat/lng.

## Remaining failures / null pins

None. Tru Value Mayne (the only previous null) is placed on the OSM supermarket
POI at Village Bay Road, Miners Bay, Mayne Island (`48.850444, -123.298511`).
Nominatim has no house number for 472 Village Bay Rd; Photon/OSM `shop=supermarket`
`Tru Value Foods` was used instead. First Nominatim free-form hit (Cadboro Bay)
was discarded as off-island.

## Notes

- FreshBooks exported almost every Greater Victoria store with `city=Victoria`.
  Queries now use the real municipality (Central Saanich, Colwood, Langford,
  View Royal, Sidney, Saanich, North Saanich, Metchosin, Esquimalt, Oak Bay, etc.).
- Save-On Blanshard and Thrifty Cloverdale had *unique* downtown pins that were
  still ~4 km south of the actual Uptown/Saanich stores.
- Fairway Shelbourne and Mt Douglas Market had unique pins ~3 km south of the
  OSM supermarket POIs on Shelbourne.
- Old Farm Market “Duncan” is at 5164 Francis St, Koksilah (just south of
  Duncan), not Crofton. City label kept as Duncan.
- Dan’s Farm is in District of Saanich (Bear Hill / Elk Lake), not Central Saanich.

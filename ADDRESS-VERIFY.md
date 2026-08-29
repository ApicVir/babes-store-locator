# Store locator address verification

Verified every pin in `stores.json` / `index.html` against the **public storefront** (official site, chain locator, chamber, OSM/MapQuest), not the FreshBooks invoice shipping line.

FreshBooks source: `/workspace/customer-products-from-freshbooks.csv` (105 customer rows). Known-good pins left untouched: Peppers Foods, Babe’s Honey Sidney, Babe’s at Galey Farms Market, Thrifty Wallace, Tru Value Mayne.

Date: 29 Aug 2026 (PT).

## Summary

| Class | Count | Notes |
|---|---:|---|
| **OK** | 52 | Name + address already match a real public storefront |
| **FIXED** | 41 | Corrected in `stores.json`, `index.html` `const STORES`, and `ADDRESS_OVERRIDES` / `TITLE_FIX` in `build.py` |
| **DROP-POINT?** | 0 remaining on the map | Three invoice-vs-storefront mismatches were found and **fixed**; still need Brandon to confirm (below) |
| **UNCLEAR** | 0 remaining unclassified | Open questions listed under Needs Brandon (missing chain stores, name aliases) |
| **Total** | **93** | Unique coords; no null pins |

Needs Brandon: **10 questions** (confirm the three civic-number fixes + missing stores + a few name aliases).

## Patterns

1. **Old civic / neighbour civic, not a commissary.** Country Grocer Chemainus was invoiced at **2835 Oak St** (the old 49th Parallel Grocery civic, same phone as today’s store). Public Country Grocer is **3055 Oak St**. The real CG warehouse/buying group is **3110 Hope Rd, Chemainus** — that address is *not* on the map.
2. **Adjacent civic number.** Deep Cove Market was at **10990 West Saanich Rd**, which is St. John’s United Church / **North Saanich Farm Market** (Saturday farmers’ market). The grocery is **10940 West Saanich Rd**, ~150 m south.
3. **Transposed digits.** Jollity Farm Shop & Cafe FreshBooks `2589 Oak St` vs official **2859 Oak St**.
4. **Red Barn is not dropping to a commissary in this data.** Each Red Barn invoice is a real retail storefront. Vanalman (751 Vanalman Ave — also their smokehouse / busiest deli) is a **public 8th store that is missing from FreshBooks / the map**, not a hidden drop used in place of another store.
5. **FreshBooks `city=Victoria` on most CRD stores** is already handled by municipality overrides. Remaining city labels now match the chain locator / the store’s own site (Saanichton, Brentwood Bay, North Saanich, Victoria).
6. **Invoice parent vs public name.** `Village Food Market (Logan Group)` is publicly **Village Food Markets**. `Co-op Food Store` is publicly **Peninsula Co-op Food Centre**. `Nootka Rose` is **Nootka Rose Milling**. Red Barn “Brookside” / “Sidney” are publicly **Latoria Walk** / **Sandown**.
7. **Unit numbers on chain locators** (Lifestyle Unit 180, Market on Millstream 125-2401C, Heart Pharmacy #15, Fantastico 102, Save-On #100 / #108) were missing from the customer-facing pin.

## FIXED (old → new)

### A. Street number / pin moved (3)

| Store | FreshBooks / old | Public storefront (now on map) | Source |
|---|---|---|---|
| Country Grocer Chemainus | 2835 Oak St, Chemainus `48.925554, -123.715371` | **3055 Oak St**, Chemainus V0R 1K0 `48.925946, -123.726366` | [countrygrocer.com/locations/chemainus](https://www.countrygrocer.com/locations/chemainus/) — OSM supermarket POI. Old 2835 = former 49th Parallel Grocery. Warehouse is 3110 Hope Rd, *not* used. |
| Jollity Farm Shop & Cafe | 2589 Oak St, Chemainus `48.925418, -123.718709` | **2859 Oak St**, Chemainus V0R 1K1 `48.925517, -123.716555` | [jollityfarm.ca/contact](https://www.jollityfarm.ca/contact) — OSM named cafe POI |
| Deep Cove Market | 10990 West Saanich Rd V8L 5P5 `48.68035, -123.45822` | **10940 West Saanich Rd**, North Saanich V8L 5R9 `48.679121, -123.458052` | Apple Maps / OSM `shop=supermarket`. 10990 = St. John’s United / North Saanich Farm Market |

### B. Name / city / street type (public storefront label)

| Store (now) | Old | New | Source |
|---|---|---|---|
| Peninsula Co-op Food Centre | Co-op Food Store, 2132 Keating Cross Rd, Central Saanich | **Peninsula Co-op Food Centre**, same civic, city **Saanichton** | [peninsulaco-op.com/locations/food-centre](https://www.peninsulaco-op.com/locations/food-centre/) |
| Village Food Markets | Village Food Market (Logan Group), 103-6661 Sooke Rd | **Village Food Markets**, **6661 Sooke Rd**, V9Z 0A1 | [villagefoodmarkets.com/contact](https://villagefoodmarkets.com/contact/) |
| Nootka Rose Milling | Nootka Rose, 4480 Happy Valley road | **Nootka Rose Milling**, 4480 Happy Valley Rd, V9C 3Z3 | MapQuest / directories |
| Red Barn Market (Latoria Walk) | Red Barn Brookside, 611 Brookside Rd, Colwood | **Red Barn Market (Latoria Walk)** — civic unchanged | [redbarnmarket.ca/locations/latoria-walk](https://www.redbarnmarket.ca/locations/latoria-walk/) |
| Red Barn Market (Sandown) | Red Barn Sidney, 10330 McDonald Park Rd, Sidney | **Red Barn Market (Sandown)**, city **North Saanich** | [redbarnmarket.ca/locations/sandown](https://www.redbarnmarket.ca/locations/sandown/) |
| Dan's Farm & Country Market | city Saanich | city **Saanichton** (2030 Bear Hill Rd unchanged) | [dansfarm.ca](https://www.dansfarm.ca/) |
| Country Bee Honey Farm | city Central Saanich | city **Saanichton** (6440 W Saanich Rd unchanged) | [countrybeehoney.ca](https://www.countrybeehoney.ca/) |
| Health Essentials | city Saanich | city **Victoria** (#101-300 Gorge Rd W unchanged) | [myhealthessentials.ca/contact](https://myhealthessentials.ca/contact/) |
| Fairway (West Saanich) | city Central Saanich | city **Brentwood Bay** (7108 W Saanich Rd unchanged) | [fairwaymarkets.com](https://www.fairwaymarkets.com/victoria---quadra-village) |
| Thrifty Foods Salt Spring | 114 Purvis **Ln** | **114 Purvis Rd**, V8K 2S5 | [pickup.thriftyfoods.com](https://pickup.thriftyfoods.com/store.php?city=Ganges&customer=75387) |

### C. Official unit / postal (pin not moved)

| Store | Old | New | Source |
|---|---|---|---|
| Country Grocer Cedar | 1824 Cedar Rd | **1824 Cedar Rd #3C**, V9X 1H9 | countrygrocer.com/our-locations |
| Country Grocer Cobble Hill | 1400 Cowichan Bay Rd | **#33-1400 Cowichan Bay Rd** | same |
| Country Grocer Saltspring | postal V0R 2P2 (wrong FSA) | **V8K 2V7** | same |
| Country Grocer Lake Cowichan / Bowen / Chase River | no postal | V0R 2G0 / V9S 0A9 / V9R 6R6 | same |
| Fairway Shelbourne / Gorge / Sidney | V8P 5E3 / V9A 1M6 / V8L 1Y2 | **V8P 4H1 / V9A 1M7 / V8L 1Y1** | fairwaymarkets.com |
| Lifestyle Markets (Douglas) | 2950 Douglas St | **2950 Douglas St, Unit 180** | lifestylemarkets.com/pages/locations |
| Lifestyle Markets Cook St. | 343 Cook Street, V8V 3X8 | **343 Cook St**, **V8V 3X6** | same |
| Market On Millstream | 2401 Millstream Rd, V9B 6C6 | **125-2401C Millstream Rd**, **V9B 3R5** | themarketstores.com/contact |
| Market On Yates | no postal | **V8V 3M4** | same |
| Heart Pharmacy | 1594 Fairfield Rd | **#15-1594 Fairfield Rd**, V8S 1G1 | heartpharmacy.com Fairfield Plaza |
| Caffe Fantastico - Harbour Rd | 398 Harbour Rd | **102-398 Harbour Rd** | caffefantastico.com/pages/bar-deli |
| Great Greens | 4485 Trans-Canada Hwy | **Suite G, 4485 Trans-Canada Hwy** | greatgreens.ca/contact |
| Save-On-Foods Wilson | 172 Wilson St | **#100-172 Wilson St** | Yext / HealthLink |
| Save-On-Foods Tillicum | 3170 Tillicum Rd | **#108-3170 Tillicum Rd** | same |
| Red Barn Market (Matticks Farm) | 5325 Cordova Bay Rd | **129-5325 Cordova Bay Rd** | redbarnmarket.ca/locations/matticks-farm |
| Thrifty Foods (08) Colwood | postal V9B 2V3 | **V9B 1J2** | directories / FoodHero |
| Pharmasave Hillside | V8T 2C4 | **V8T 5G1** | pharmasave.com/store/victoria-hillside |
| Quadra Village Drug Mart | V8T 4E3 | **V8T 4E4** | quadravillagepharmacy.com |
| Urban Grocer | V8R 1H9 | **V8R 1H8** | City of Victoria licence |
| Red Barn - James Bay | V8V 0C2 | **V8V 0C3** | redbarnmarket.ca |
| Red Barn - West Saanich | no postal | **V9E 2G1** | same |
| Mt Douglas Market | no postal | **V8N 3E8** | beatthewheat / directories |
| The Drake | no postal | **V8W 3J6** | drakeeatery.com |
| Pinhalla Pizzeria | no postal | **V8W 1R4** | pinhalla.com |

## OK (52) — verified, not changed

Babe’s Honey Sidney; Babe’s at Galey Farms Market; Peppers Foods; Thrifty Wallace; Tru Value Mayne; Tru Value Pender; Farm Gate Store; Country Grocer Duncan, Ladysmith, Esquimalt, Royal Oak; Silver Rill Corn; Stickleback Oceanfront Cider; Western Foods; Special Teas; Caffe Fantastico Kings Rd; Easy 4u Convenience; Fairway Goldstream, Oak Bay, Quadra, McKenzie; Fickle Fig Farm Market (Mills Rd flagship); Flying Dutchman Market; Forbes Pharmacy Fort Street; High Vibes Victoria; McLennan's Island Meat and Seafood; Old Farm Market Oak Bay & Duncan; Red Barn Esquimalt & Oak Bay; Refuge Tap Room; Rootcellar Cook St & McKenzie; Save-On Beacon, Blanshard, Foul Bay, McCallum, Pandora, Colwood; Siam Thai Restaurant; Sushi Time Express; Thrifty Broadmead, Cloverdale, Admirals, Belmont, Fairfield, Hillside, James Bay, Sidney, Tuscany; Tre Fantastico; Fernwood General Store.

## Needs Brandon

Please answer these so the map stays honest. I did **not** guess.

### 1. Country Grocer Chemainus — confirm the pin I moved

- **FreshBooks:** Country Grocer - Chemanus, **2835 Oak St**, Chemainus (last invoice 2026-07-21)
- **Public storefront:** Country Grocer **3055 Oak St**, Chemainus V0R 1K0 ([locator](https://www.countrygrocer.com/locations/chemainus/))
- **Also real, not used:** Warehouse & Buying Group **3110 Hope Rd**, Chemainus
- **What 2835 is:** old 49th Parallel Grocery civic (same phone 250-246-3551)
- **Need:** Is honey on the **3055 Oak** grocery floor (I pinned that), or do you still drop at 2835 / Hope Rd warehouse? If warehouse-only, this should not be a public pin.

### 2. Jollity Farm Shop & Cafe — confirm the digit swap

- **FreshBooks:** **2589** Oak St, Chemainus
- **Public:** **2859** Oak St ([jollityfarm.ca/contact](https://www.jollityfarm.ca/contact)); OSM names the cafe at 2859
- **Need:** Typo in FreshBooks, or a different door? I treated it as a typo and moved the pin ~150 m.

### 3. Deep Cove Market — confirm 10940 not 10990

- **Override / old pin:** **10990** West Saanich Rd (that civic is St. John’s United Church / North Saanich Farm Market, Sat 9:30–12)
- **Public grocery:** **10940** W Saanich Rd, North Saanich V8L 5R9
- **Need:** You sell at the grocery at 10940 (pinned), not the Saturday church market?

### 4. Red Barn Vanalman is missing

- Official Red Barn has **8** Greater Victoria stores. We have 7.
- **Not on the map:** Red Barn Market — Vanalman, **751 Vanalman Ave**, Saanich V8Z 3B8 (also their smokehouse / HQ-adjacent retail). [redbarnmarket.ca/locations/vanalman](https://www.redbarnmarket.ca/locations/vanalman/)
- FreshBooks has **no** Vanalman customer. Every other Red Barn invoice is a real storefront, not a commissary drop.
- **Need:** Do they stock Babe’s at Vanalman? If yes, add a pin. If you drop Bee Line to Vanalman for all stores, say so — right now each store has its own invoice address.

### 5. Village Food Markets name

- FreshBooks: **Village Food Market (Logan Group)**, 103-6661 Sooke R (truncated)
- Public: **Village Food Markets**, 6661 Sooke Road (no unit on their contact page)
- I renamed and dropped unit 103.
- **Need:** Keep “Logan Group” on the public map? Put the unit back?

### 6. Forbes Pharmacy Fort Street vs Jubilee

- FreshBooks / map: **Forbes Pharmacy Fort Street**, 1775 Fort St
- Babe’s `/honey-1` named **Jubilee on Fort**. Same civic (Jubilee Pharmacy & Market / Forbes).
- **Need:** Public label **Forbes**, **Jubilee**, or both?

### 7. Heart Pharmacy — only Fairfield is in FreshBooks

- Map: **#15-1594 Fairfield Rd** (Fairfield Plaza) — matches their location page and the FB street `15-1594 Fairfield Rd`.
- Heart has ~7 pharmacies. I did **not** add the others.
- **Need:** Is Fairfield the only Heart that actually sells Babe’s?

### 8. Chain stores Babe’s named “all locations” that are **not** in FreshBooks

I did **not** add these (no invoice = no proof of stocking):

| Chain | Missing public store | Address |
|---|---|---|
| Fairway (“all locations”) | Nanaimo — North Town Centre | #103-4750 Rutherford Rd, Nanaimo V9T 4K6 |
| Lifestyle (Bee Line named at Douglas only) | Sidney — Lifestyle Select | 9769 Fifth St, Sidney V8L 2X1 |
| Fickle Fig (FB is Mills Rd only) | Express + Airport | 2489 Beacon Ave, Sidney; #1071-1640 Electa Blvd, North Saanich |

**Need:** Should any of these be on the public map?

### 9. Red Barn public names

I renamed **Brookside → Latoria Walk** and **Sidney → Sandown** to match redbarnmarket.ca. Civics unchanged (611 Brookside Rd / 10330 McDonald Park Rd).

**Need:** Prefer FreshBooks nicknames on the map instead?

### 10. Siam Thai — still open?

- Address **512 Fort St** matches their site.
- SkipTheDishes listing is tagged **DNU**; DoorDash / Restaurantji still show it open as of Aug 2026.
- Last invoice 2026-07-23.
- **Need:** Still a live account, or pull the pin?

## Durable rebuild notes

`ADDRESS_OVERRIDES` and `TITLE_FIX` in `build.py` now include the civic-number, city, unit, and public-name fixes so a FreshBooks CSV rebuild will not revert Chemainus to 2835, Deep Cove to 10990, Jollity to 2589, or Millstream/Heart/Lifestyle unit-less addresses.

Do **not** run `regeocode.py` against the full file blindly.

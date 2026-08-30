# Online stockists for the recipe adapter

Research compiled 29 Aug 2026 (PT).

**Peppers v1 is implemented** in `/workspace/recipe-adapter/index.html` (`PEPPERS_HONEY`, `peppersCartUrl`, `peppersSearchUrl`): honey goes to a live Shopify cart permalink; other recipe ingredients use Peppers search links. Find Stores still opens the locator. This file remains the SKU/research source of truth.

**Market Stores Express v1 is implemented** in the same adapter (`MARKET_HONEY`, `mapMarketHoney`, `marketProductUrl`): opens the matching Babe's product page (shopper hits Add). No public cart permalink. Wildflower/clover map to live `babes-*` product URLs; other varieties fall back to wildflower 500g with a short “closest Babe's listing” note.

**Question:** which Babe’s retail customers already have a usable grocery / e-commerce portal (home delivery or curbside) so the recipe adapter can drop Babe’s honey into a cart **along with other recipe ingredients**.

**Sources:** `/workspace/locator/stores.json`, `/workspace/customer-products-from-freshbooks.csv`, `/workspace/babes-retailers.md`, live retailer sites (fetched 29 Aug 2026). FreshBooks is treated as source of truth for *who currently receives* which SKUs.

**Confidence key**
- **live-listed** — Babe’s SKU page exists on the retailer’s shop today
- **invoiced** — FreshBooks shows recent consumer SKUs; not proven on the website
- **portal-only** — store has e-commerce, Babe’s not found in public search

---

## Ranked list (usable online shopping + carries Babe’s)

Rank is “best for recipe-adapter cart integration,” not sales volume.

| Rank | Stockist | City | Online shop | Babe’s searchable online? | Fulfilment | Platform | Cart / deep-link feasibility |
|---|---|---|---|---|---|---|---|
| **1** | Peppers Foods | Cadboro Bay, Victoria | https://shop.peppers-foods.com/ | **Yes — honey + Bee Line** | Same-day delivery (before ~11:30am), 1-hour windows, $40 min, $7–$15 fee; curbside/in-store pickup | **Shopify** | **Best.** Product URLs + Shopify cart permalinks. Full grocery catalog (produce, dairy, pantry, baking). |
| **2** | The Market Stores (Yates + Millstream) | Victoria / Langford | https://express.themarketstores.com/ | **Yes — honey SKUs** | Home delivery + pickup. Online inventory is **Millstream only**. | Mighty Oaks MightyCart (custom grocery) | **Strong grocery mix** (~18k items) so other recipe ingredients exist. Add-to-cart from outside is **not** a public permalink; needs their session/API. |
| **3** | Lifestyle Markets (Douglas flagship; can transfer to Cook St / Sidney) | Victoria | https://lifestylemarkets.com/ | **Yes — 1kg Wildflower + 1kg Clover** | Canada Post on most dry goods ($89+ free); **local grocery / honey tagged `local-delivery`**; curbside at Douglas; phone local delivery Greater Victoria | **Shopify** | Easy cart permalinks for honey. Weaker as a *full recipe grocery* (produce exists but is local-delivery-only; Bee Line not listed online). |
| **4** | Save-On-Foods (8 Greater Victoria stores invoiced) | Victoria / Sidney / Colwood / View Royal | https://www.saveonfoods.com/sm/pickup/rsid/{store}/ | **Not found** in public honey search | Pickup + delivery on their site; also Instacart | Mercatus / mi9cloud | Full grocery cart. Babe’s is invoiced but looks like a **local SKU omitted from the website**. Deep-link only if a product ID appears. |
| **5** | Thrifty Foods (most Island stores invoiced for honey) | Greater Victoria + Island | https://pickup.thriftyfoods.com/ + Instacart + Uber Eats | **Not found** as a public product page | Own site: **pickup only** (48h); delivery by phone ($50 min). Instacart/Uber Eats for delivery. Voilà does **not** cover the Island. | Custom pickup portal + Instacart | Grocery-complete, but local honey often missing from third-party catalogs. No stable Babe’s product URL found. |
| **6** | Peninsula Co-op Food Centre | Saanichton | DoorDash only (no own shop) | Unknown on DoorDash | DoorDash grocery delivery | DoorDash | Heavy FreshBooks customer (23 invoices / 16 SKUs). No first-party cart to deep-link. |
| **7** | Red Barn Market (8 Greater Victoria stores) | Victoria area | Uber Eats all stores. `shop.redbarnmarket.ca` **500 error** today (COVID-era Shopify/app may be dead). | Not confirmed | Uber Eats delivery/pickup; sandwich app is prepared food, not grocery | Uber Eats / Moduurn | FreshBooks is **Bee Line only**, no honey. Uber Eats carts are a poor recipe-ingredient target. |
| **8** | Health Essentials | Gorge / Tillicum, Victoria | https://shop.myhealthessentials.ca/ | **No** (search “babes” returns baby/Birch Babe, not honey) | Canada Post ($100+ free) | Shopify | In-store honey (2 invoices). Not a grocery; skip for recipe carts. |

### Not usable as grocery portals (despite being Babe’s customers)

| Stockist | Why not |
|---|---|
| **Country Grocer** (11 Island stores, high invoice volume) | Site explicitly: “we do not deliver or offer online shopping.” Only platter order forms. Old grocery form at countrygrocerorders.com shutting down **1 May 2026**. |
| **Fairway Markets** (Victoria chain) | No own e-commerce. Instacart hits are the **NYC** Fairway, not this chain. |
| **The Root Cellar** | Shopify is **gift cards + swag only** (`the-rootcellar-online.myshopify.com`). No grocery cart. Strong in-store honey + Bee Line. |
| **Village Food Markets (Sooke)** | FAQ: “Do you offer grocery delivery? **No.**” Marketing page for Bee Line only. |
| **Great Greens (Duncan)** | Full-service farm market, no shop. Highest Cowichan SKU mix in FreshBooks. |
| **Heart Pharmacy** | Prescription delivery only, not grocery. |
| **Dan’s Farm, Old Farm Market, Fickle Fig, Urban Grocer, Fernwood General, Mt Douglas Market, Deep Cove, Western Foods, Mother Nature’s, Tru Value, Farm Gate** | Independent grocers / farm stands. No comprehensive online grocery found. |
| **Caffe Fantastico, Discovery Coffee, Boulder House, Sushi Time, restaurants** | Not grocery. |
| **Babe’s Sidney + Galey** | Own shops. No consumer e-commerce cart (wholesale Google Form only). |

---

## Best 1–2 first integration targets

### 1. Peppers Foods — do this first

**Why**
- Only portal that already lists **both** Babe’s honey **and** Bee Line drinks **and** a full grocery aisle (flour, eggs, dairy, produce, baking).
- Shopify, so the adapter can open a cart with honey + other SKUs in one URL, no partnership required for a v1.
- Cadboro Bay / Greater Victoria delivery — the adapter’s core geography.
- FreshBooks: **31 invoices in 12 months, 17 SKUs**, last invoice 25 Aug 2026. Current stock, not a leftover listing.
- Public product pages already exist (strongest third-party SKU evidence of any stockist).

**Caveats**
- Catalog is not 100% of the store (“search bar only provides top sellers”; missing items go in a special-request field at checkout).
- Local delivery / pickup only — no Canada-wide shipping.
- One store, not a chain.

### 2. The Market Stores Express — second, in parallel or immediately after

**Why**
- Closest thing to “load the whole recipe, not just the honey.” ~18k grocery items, delivery to the door.
- Babe’s honey **is** on the shop (500g wildflower, 500g clover, 1kg clover). Yates is one of Babe’s biggest accounts (29 invoices / 24 SKUs including 1kg honey and 750ml Bee Line).
- Two physical stores covering downtown + West Shore.

**Caveats**
- Online orders are fulfilled from **Millstream inventory**, not Yates. Banner on the shop: “Products listed here may not be available at the Market on Yates.”
- Custom Mighty Oaks cart — **no public add-to-cart permalink**. v1 is “open product page / search”; true cart-inject needs their API or a partnership.
- Bee Line drinks not found as product URLs (honey yes).

**Lifestyle Markets** is the easy Shopify runner-up if the goal is “add a jar of honey” (Canada-wide dry-goods shipping + local delivery), but it is a health-food store, not a recipe grocery. Use it as a honey-only fallback, not the primary “shop the recipe” target.

---

## How adding to cart works (top candidates)

### A. Peppers Foods (Shopify) — concrete URLs

**Shop:** https://shop.peppers-foods.com/  
**Search:** https://shop.peppers-foods.com/search?q=babes+honey  
(plain `?q=babes` also matches baby food — prefer `babes+honey`.)

| Product | Price (29 Aug 2026) | Product URL | Variant ID | Cart permalink (qty 1) |
|---|---|---|---|---|
| Creamed honey 500g | $15.49 | https://shop.peppers-foods.com/products/babes-honey-creamed-500g | `45118783750327` | https://shop.peppers-foods.com/cart/45118783750327:1 |
| Wildflower 500g | $15.49 | https://shop.peppers-foods.com/products/babes-honey-wildflower-500g | `45118783619255` | https://shop.peppers-foods.com/cart/45118783619255:1 |
| Wildflower 1kg | $29.69 | https://shop.peppers-foods.com/products/babes-honey-wildflower-1-kg | `45124987486391` | https://shop.peppers-foods.com/cart/45124987486391:1 |
| Clover Blossom 500g | $15.49 | https://shop.peppers-foods.com/products/babes-honey-clover-blossom-500g | `45118783881399` | https://shop.peppers-foods.com/cart/45118783881399:1 |
| Ginger Splash 473ml | $5.79 | https://shop.peppers-foods.com/products/babes-ginger-splash | `45360227647671` | https://shop.peppers-foods.com/cart/45360227647671:1 |
| Mermaid Tears 473ml | $5.79 | https://shop.peppers-foods.com/products/babe-s-honey-farm-fermentation-beeline-assorted-flavor-sparkling-culture-honey-drinks-473-ml | `45123672866999` | https://shop.peppers-foods.com/cart/45123672866999:1 |

Currantly Hip / Earl Grey / 750ml bottles: invoiced to Peppers, **not** found as Shopify products today.

**Adapter pattern (no API key):**

1. **Honey-only:** open the cart permalink for the recommended SKU. Shopify merges into the shopper’s existing cart cookie.
2. **Honey + other ingredients:** chain variant IDs  
   `https://shop.peppers-foods.com/cart/{honeyVariant}:1,{flourVariant}:1,{eggVariant}:1`  
   Other Peppers SKUs are on the same Shopify store (`/products/{handle}.js` returns `variants[0].id`).
3. **Search fallback:** `https://shop.peppers-foods.com/search?q={query}`
4. **JSON for live price/availability:**  
   `https://shop.peppers-foods.com/products/{handle}.js`  
   Suggest API: `https://shop.peppers-foods.com/search/suggest.json?q=babes+honey&resources[type]=product`

Barcodes observed (Peppers `sku` field): Wildflower 500g `6194900217`, Wildflower 1kg `6194900218`, Creamed 500g `6194900317`, Clover 500g `6194901002`, Ginger Splash `6194902001`, Mermaid Tears `6194902002`.

FAQs: https://shop.peppers-foods.com/pages/faqs  
Delivery: (250) 477-8259 · delivery@peppers-foods.com · 3829 Cadboro Bay Rd.

### B. Lifestyle Markets (Shopify) — concrete URLs

**Shop:** https://lifestylemarkets.com/  
**Search:** https://lifestylemarkets.com/search?q=babes+honeyfarm  
**Sweeteners collection:** https://lifestylemarkets.com/collections/sweeteners

| Product | Price | Product URL | Variant ID | Cart permalink |
|---|---|---|---|---|
| Wildflower 1kg | $27.99 | https://lifestylemarkets.com/products/babes-honeyfarm-wildflower-1kg | `43864972099722` | https://lifestylemarkets.com/cart/43864972099722:1 |
| Clover Blossom 1kg | $26.99 | https://lifestylemarkets.com/products/babes-honeyfarm-clover-blossom-1kg | `43864972263562` | https://lifestylemarkets.com/cart/43864972263562:1 |

Vendor on Shopify is `Babe's Honeyfarm`. Tags include `local-delivery` and `Sweeteners`. 500g / creamed / Bee Line **not** in the online catalog (in-store they do get 500g + Bee Line per FreshBooks).

Both products `available: true` on 29 Aug 2026.

Honey is a liquid/grocery item: Lifestyle’s shipping policy says they **do not ship grocery or perishable food outside Victoria**. Treat online Lifestyle honey as **local delivery / Douglas curbside / in-store pickup**, not Canada Post.

Curbside: Douglas only; they will transfer a packed order to Cook St or Sidney on request. Phone orders Mon–Fri 9am–noon: (250) 384-3388.  
https://lifestylemarkets.com/pages/online-curbside-orders

**Same Shopify cart-permalink pattern as Peppers.** Good v1 if Peppers is out of the shopper’s delivery zone and they only need the honey jar.

### C. The Market Stores Express (Mighty Oaks) — concrete URLs

**Shop:** https://express.themarketstores.com/  
**Grocery:** https://express.themarketstores.com/shop-online/grocery/  
**Honey aisle:** https://express.themarketstores.com/shop-online/grocery/jam-peanut-butter-spreads/honey/  
**Search (JS app; HTML fetch is empty):** try `/search/?q=babes`

| Product | Product URL |
|---|---|
| Babe’s Honey Farm raw wildflower 500g | https://express.themarketstores.com/product/babes-wildflower-honey-500g/ |
| Babe’s Honey Farm raw clover blossom 500g | https://express.themarketstores.com/product/babes-clover-blossom-honey-500g/ |
| Babe’s Honey Farm raw clover blossom 1kg | https://express.themarketstores.com/product/babes-clover-blssm-honey-1kg/ |

HTML snapshots of those product pages are a JS shell (MightyCart). Prices/UPCs did not render in a static fetch. They are live product routes as of today.

**How cart works from outside**
- Shopper must be in a browser session on express.themarketstores.com (sign-in encouraged).
- “Add to cart” is a client POST into MightyCart, not a documented public permalink.
- v1 for the adapter: **open the product URL** (shopper hits Add). Optional: also open honey aisle or search.
- True multi-item inject (honey + flour + eggs) needs Mighty Oaks / Market Stores cooperation, or reverse-engineering their XHR (fragile; don’t ship that without permission).
- Contact on the shop: (250) 391-1110, frontend2@themarketstores.com (Millstream number).

### D. Save-On-Foods (own site + Instacart)

**Pattern:** `https://www.saveonfoods.com/sm/pickup/rsid/{rsid}/`  
Search: `https://www.saveonfoods.com/sm/pickup/rsid/{rsid}/results?q=babes%20honey`  
Product (when it exists): `.../product/{slug}-id-{upc}`

Known Victoria rsiDs (incomplete):
- Tillicum: `1982` — https://www.saveonfoods.com/sm/pickup/rsid/1982/tillicum/
- Pandora: `987` — https://www.saveonfoods.com/sm/pickup/rsid/987/pandora/

Honey category example (Tillicum) listed Gramma Bee’s, **not** Babe’s. FreshBooks still invoices 500g + 1kg clover/wildflower to Beacon, Blanshard, Foul Bay, McCallum, Pandora, Tillicum, Wilson, Colwood.

**Instacart:** https://www.instacart.ca/retailer/save-on-foods-delivery/bc/near-me-in-victoria-british-columbia  
Instacart deep-links are store- and item-id specific and usually require the shopper’s address cookie. Not a clean first integration.

Also on Instacart in Victoria: Pharmasave, Shoppers — not Babe’s grocery stockists.

### E. Thrifty Foods

- Pickup portal: https://pickup.thriftyfoods.com/ (choose store → shop categories; 48h; pay in store).
- Delivery: call 250-544-1234 / 1-866-948-0196, $50 min — **not** self-serve on the site.
- Instacart + Uber Eats: https://www.thriftyfoods.com/our-services/instacart-and-uber-eats  
  Thrifty warns many in-store items (typical of local honey) are **missing** from those apps.
- Voilà by Sobeys: Ontario / Québec / Alberta only.

No Babe’s product URL found on thriftyfoods.com.

### F. Peninsula Co-op (Saanichton)

https://www.peninsulaco-op.com/services/food-centre/ — “Now offering fast grocery delivery straight to your door via DoorDash.” No first-party catalog. DoorDash item IDs are not stable enough for a recipe adapter.

---

## Suggested adapter behaviour

**Peppers v1 (implemented 29 Aug 2026):** cart permalink for the mapped honey SKU (default 500g) + per-ingredient Peppers search links. No invented flour/egg variant IDs. V8*/V9* postals emphasize Peppers; locator remains for drive-to-store.

**Market Stores Express v1 (implemented 29 Aug 2026):** open the matching Babe's product page (no public cart permalink — shopper hits Add on their site). Mapping: wildflower → 500g URL; clover 500g / clover 1kg; everything else (creamed, blackberry, fireweed, baker's) → wildflower 500g + “closest Babe's listing” note. No wildflower 1kg listing — 1kg wildflower stays on 500g with a note (clover 1kg only when the honey is clover). V9B/V9C postals emphasize West Shore / Langford. Cart inject later (no public permalink).

Remaining (not implemented):

1. **Lifestyle local delivery / Douglas curbside** for 1kg jars only, if Peppers is out of zone.
2. **Always keep** the existing locator (“Find Stores”) for everyone else — Country Grocer, Fairway, Root Cellar, Thrifty, Save-On, etc. still sell it in person. (Locator path is already preserved in v1.)

Do **not** send recipe shoppers to Red Barn Uber Eats, Health Essentials Shopify, or Root Cellar gift-card Shopify.

---

## FreshBooks reminder (Victoria-area volume, last 12 months)

Useful when choosing who is worth the integration work:

| Account | Invoices / 12mo | SKU mix | Online portal? |
|---|---|---|---|
| Peppers Foods | 31 | honey 500g+1kg, creamed, Bee Line 473+750 | **Yes — listed** |
| Thrifty Belmont | 33 | honey 500g+1kg | pickup / Instacart, Babe’s not listed |
| Country Grocer Royal Oak | 31 | honey + Bee Line | **No** |
| Market on Yates | 29 | honey 500g+1kg, Bee Line 473+750 | **Yes — honey listed** |
| Village Food Market Sooke | 27 | honey + Bee Line | **No delivery** |
| Root Cellar McKenzie | 25 | full honey + Bee Line | gift cards only |
| Co-op Saanichton | 23 | honey + Bee Line | DoorDash only |
| Thrifty Hillside | 23 | honey 500g+1kg | pickup / Instacart |
| Country Bee Honey Farm | 22 | Bee Line only | their own honey shop, not grocery |
| Fairmont Empress | 21 | hotel minis / pails | n/a (excluded from locator) |
| Red Barn West Saanich | 21 | Bee Line only | Uber Eats |
| Country Grocer Esquimalt | 20 | honey + Bee Line | **No** |
| Fairway Oak Bay | 20 | honey + Bee Line | **No** |
| Fickle Fig | 19 | Bee Line | no grocery shop |
| Save-On Tillicum | 18 | honey 500g+1kg | own site + Instacart, Babe’s not listed |
| Lifestyle Douglas | 17 | honey 500g+1kg, Bee Line 473+750 | **Yes — 1kg honey listed** |
| Market on Millstream | 17 | honey + Bee Line 473+750 | same Express shop as Yates |
| Great Greens Duncan | 16 | full lineup | **No** |

---

## Open questions / next checks (if integrating)

1. Peppers: map a short pantry dictionary (all-purpose flour, butter, eggs, milk, lemon) to variant IDs so “shop this recipe” is one cart URL.
2. Market Stores: ask Darryl Hein / Mighty Oaks whether they expose add-to-cart query params or a partner link. Product handles already exist.
3. Save-On / Thrifty: one in-browser search per Victoria `rsid` / pickup store for “Babe’s” — local SKUs may appear only after a store is selected (Cloudflare often blocks unattended fetch).
4. Lifestyle: confirm whether 1kg honey actually ships, or is blocked at checkout as `local-delivery`.
5. Red Barn: `shop.redbarnmarket.ca` 500s; treat as dead until they restore it. Uber Eats is not a recipe cart.
6. Do not assume Fairway Instacart — that is a different company in New York.

---

*File: `/workspace/recipe-adapter/online-stockists.md` · research date 29 Aug 2026 PT · Peppers v1 and Market Stores Express v1 (open product page) wired in the recipe adapter; live babes-honey-farm.com not modified.*

# Babe’s Honey Farm — Store Locator Style Notes

Restyled to match [babes-honey-farm.com](https://babes-honey-farm.com) Retailers page (Squarespace), not the previous cream/honey farm-app look.

## Fonts (Google Fonts)

| Role | Face | Notes |
|------|------|--------|
| Body, nav, store names, chips, legend, footer | **Raleway** 300–700 | Body ~15.5px / 300–400, letter-spacing 0.4px. Store names: 700, uppercase, letter-spacing ~1.2px |
| Section title (“Find Babe’s near you”) | **Rye** ~24px | Free stand-in for site’s Rosewood Std Fill (western/tuscan display) |
| Embed mode title | Raleway 700 uppercase | Simpler heading when iframe’d into Squarespace |

Dropped: Cormorant Garamond, decorative bee hex mark.

## Colors

| Token | Value | Use |
|-------|-------|-----|
| Base / ink | `#171717` | Page chrome / text on light |
| Retailers band | `#4D7099` → `#5B7FA6` (gradient) | Main app background (steel-blue band) |
| Light content | `#F2F2F2` | Store list panel, popups |
| Text on blue | `#FFFFFF` / `rgba(255,255,255,0.9)` | Titles, chips |
| Muted on blue | `rgba(255,255,255,0.7)` | Subcopy, footer note |
| Buttons / active chips | `#000` bg, white text | Square corners (Subscribe-style) |
| Shop pin | `#D4AF6A` | Light/gold Babe’s shops |
| Retailer pin | `#1A2E1C` | Dark green / near-black on map |

Avoided: cream `#F7F1E3`, honey-gold app chrome.

## Layout

- Map + list: `min(70vh, 720px)` so the map does not grow unboundedly.
- `?embed=1` / `embed.html`: fill viewport; Raleway uppercase title only; no fake Squarespace header/logo.
- Non-embed: minimal header with Rye title + short Raleway subline.
- Footer: *Stock changes. Call the store if you need a specific size.* (muted Raleway)

## Geolocation (29 Aug 2026)

- URL `?lat=48.43&lng=-123.36` (optional `sku`) centers the map, drops a square black “you are here” marker, sorts the list by haversine distance, and shows km on each store card. SKU AND-filters still apply; distance sort is on the filtered set.
- Custom **Near me** Leaflet control: black square + crosshair (not default locate CSS). On success: same as URL params. Denied / timeout: map stays put, no modal.
- Do **not** call `getCurrentPosition` / `map.locate` on page load — only the Near me control (or coords already in the URL).

## Files

- `/workspace/locator/index.html` — self-contained locator
- `/workspace/locator/embed.html` — redirects to `index.html?embed=1` and preserves query params (`lat`, `lng`, `sku`, …)


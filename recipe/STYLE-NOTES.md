# Babe’s Honey Farm — Recipe Adapter Style Notes

Restyled to match [babes-honey-farm.com](https://www.babes-honey-farm.com) (Squarespace Home + Retailers), **not** a black dashboard and **not** the cream/honey farm-app look.

Follows the Babe's site-design skill: light page canvas, photo hero, steel-blue Retailers band, square black CTAs, Rye + Raleway, dark ink on light cards.

## Fonts (Google Fonts)

| Role | Face | Notes |
|------|------|--------|
| Display / section titles / lockup | **Rye** | Free stand-in for site’s Rosewood Std Fill (western/tuscan) |
| Body, nav, labels, buttons, cards | **Raleway** 300–700 | Nav + eyebrows: 600–700, uppercase, letter-spacing ~0.14–0.18em |

## Colors

| Token | Value | Use |
|-------|-------|-----|
| Page canvas | `#FFFFFF` | Default body / science band |
| Light band | `#F2F2F2` | Adapter + honey product strips |
| Ink | `#171717` | Body text, headings on light, nav |
| Muted | `#555` / `#666` | Subcopy on white / light-gray cards |
| Borders | `#E0E0E0` | Cards, header rule, inputs |
| Steel blue | `#4D7099` → `#5B7FA6` | Stores / Retailers-style band (over farm photo) |
| Text on photo / blue | `#FFFFFF` / `rgba(255,255,255,0.85)` | Hero + stores titles |
| CTA | `#000` bg, `#FFF` text, `border-radius: 0` | Adapt, Search, Checkout, primary hero |
| Accent gold | `#D4AF6A` | Honey swatches / selected swap chips only — **not** page chrome |
| Footer strip | `#171717` with white type | Short dark bar only |

Avoided: cream `#F7F1E3`, honey-gold app chrome, painting the whole page `#171717`.

## Layout rhythm (matches live site)

1. **Sticky white header** — Raleway uppercase nav, centered B&W logo (`NO+BEE+LOGO+B+W.png`).
2. **Photo hero** — full-bleed farm/sky (`IMG_4489.JPG`) + `rgba(23,23,23,~0.55)` overlay; white Rye headline; black square CTA + white outlined secondary; white stats (readable on the photo).
3. **Adapter** — `#F2F2F2` band, dark Rye headings, white square cards, black Adapt CTA.
4. **Science** — white band, dark headings, white rule cards with `#555` body (not white-on-white).
5. **Honey** — `#F2F2F2`, white product cards, gold used only as swatch bars.
6. **Stores** — steel-blue over Retailers farm photo (`IMG_4496.JPG`), white titles, light inputs, black Search; white cart/store cards with dark ink.
7. **Footer** — short `#171717` strip.

## Contrast QA

Light cards / panels use `#171717` / `#555` — never `rgba(255,255,255,…)` body copy. White type is only on the photo hero, steel-blue stores band, black buttons, and footer.

## Files / wiring (unchanged)

- `/workspace/recipe-adapter/index.html` — visual chrome + CSS only
- `/workspace/recipe-adapter/support.js` — not modified
- Adapt engine (`<script type="text/x-dc">`) — logic untouched
- Find Stores still opens `https://apicvir.github.io/babes-store-locator/`

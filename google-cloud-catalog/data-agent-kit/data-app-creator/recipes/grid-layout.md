# Coordinate Grid (opt-in)

**Use when:** the app is a flat BI dashboard whose tiles must hold fixed positions —
everything lines up exactly and nothing reflows.

**Otherwise use ordinary responsive CSS** (`responsive-layout.md`), which is the
default: it adapts to any width by itself, and tiles grow with their content
instead of clipping.

Tiles sit on one shared CSS grid with fluid 96-column horizontal widths and a
deterministic 8px vertical row pitch. Make the app's main layout a
`.da-grid` and give each tile a `cell="x y w h"` coordinate; the browser
renders the grid natively.

**The cost of choosing it:** positions are absolute, so inserting a band means
renumbering the `y` of every tile below it, and heights are fixed in 8px steps
with overflow clipped — leave room for text that may wrap or grow.

## The model

- `.da-grid` is a real `display:grid` with **96 fluid columns** and **deterministic 8px row units**.
  Horizontal placement scales with container width, while vertical row heights remain pixel-perfect and non-fragile
  across desktop, laptop, and 4K displays.
- Each direct child is a tile placed by `cell="x y w h"`: the **0-based start
  column and row**, then the **width and height** in cells. Columns run 0–95.
- Each tile **owns a fixed cell**, so moving or resizing one **never disturbs
  another** (the BI-dashboard behaviour — not source-order auto-flow). It is fully
  responsive with multi-tier collapsing:
  - **Desktop (> 900px):** Strict 96-column placement as authored.
  - **Tablet / Intermediate (601px – 900px):** Quarter-width tiles (w ≤ 28, e.g. 4 KPIs)
    collapse into **2 columns × 2 rows**, and half/third-width charts (w ≥ 29) expand
    to full width (1 per row) so visualizations stay readable rather than shrinking.
  - **Mobile (≤ 600px):** All tiles collapse to a single stacked column.

Handy sizes (8px base row unit, 96-wide grid):
- **KPI card:** `h ≈ 10` (80px tall), quarter width `w ≈ 22`
- **Charts / Visualizations:** `h ≈ 36–40` (288px–320px tall), half width `w ≈ 46` or third width `w ≈ 30`
- **Hero banner:** `h ≈ 24` (192px tall), full width `w = 96`
- **Data Table (AG Grid):** `h ≈ 40–45` (320px–360px tall), full width `w = 96`
- **Row gaps:** Leave 1–2 rows empty between bands (e.g. KPIs at `y=0, h=10` $\rightarrow$ Charts at `y=12`).

## Snippet

```html
<div class="da-grid">

  <!-- Hero band: one full-width tile at the top -->
  <div class="hero-card" cell="0 0 96 24"> … </div>

  <!-- KPI row below hero: 4 cards 22 wide x 10 tall (80px height) -->
  <app-kpi cell="0 26 22 10"  label="Revenue" query-field="orders.total_revenue" format="usd"></app-kpi>
  <app-kpi cell="24 26 22 10" label="Orders"  query-field="orders.count"         format="int"></app-kpi>
  <app-kpi cell="48 26 22 10" label="Buyers"  query-field="users.count"          format="int"></app-kpi>
  <app-kpi cell="72 26 22 10" label="AOV"     query-field="orders.average_value" format="usd"></app-kpi>

  <!-- Two charts side-by-side: 46 wide x 36 tall (288px height) -->
  <div class="card da-tile" cell="0 38 46 36">
    <div class="card-head">Revenue by Country</div>
    <app-chart bare type="bar" height="100%"
      .query=${{ fields: ['users.country', 'orders.total_revenue'], limit: '8' }}
      .filters=${this.getEffectiveFilters()}></app-chart>
  </div>
  <div class="card da-tile" cell="48 38 46 36">
    <div class="card-head">Orders by Status</div>
    <app-chart bare type="donut" height="100%"
      .query=${{ fields: ['orders.status', 'orders.count'] }}
      .filters=${this.getEffectiveFilters()}></app-chart>
  </div>

  <!-- Full-width table below: 96 wide x 40 tall (320px height) -->
  <app-grid cell="0 76 96 40" title="Top Markets" height="100%"
    .query=${{ fields: ['users.state', 'orders.total_revenue'], limit: '12' }}
    .filters=${this.getEffectiveFilters()}></app-grid>
</div>
```

## Rules of thumb

- **Chrome above the grid.** A title bar or a filter `<app-select>` can
  sit above `.da-grid` — it doesn't have to be a tile.
- **Filling the cell.** A chart/grid that is a direct grid child, or the widget
  inside a `.da-tile` card, should carry `height="100%"` so it grows to the
  cell. The row span sets the height; don't also set a fixed px `height`.
- **Composed tiles stay whole.** A hero (a number over a background, a chart over
  art) is ONE tile with `cell` on the wrapper — never split the pieces into
  separate tiles.
- **Coordinates via `cell`, never `position: absolute`.** The `cell="x y w h"`
  coordinate IS how you place a tile. Absolute positioning doesn't reflow. If a design
  truly isn't a grid, use the **custom-layout** recipe as a deliberate opt-in.
- **Space tiles through the grid.** Keep `.da-grid { --da-grid-gutter: 0; }`
  so tiles sit flush in their cells, and separate them by leaving empty cells
  between tiles — on a grid this fine, that IS your spacing control, and how much
  is your judgement. Never put `gap` on a `.da-grid` (on a fine grid a real
  `gap` offsets every track, ballooning multi-cell tiles; the runtime forces
  `gap:0` anyway), and don't fake spacing with a
  margin gutter (`--da-grid-gutter > 0`) — that leaves padding between the widget
  and the grid squares.

## Fields to swap

- `cell="x y w h"` per tile — start from the coordinates above, then fine-tune
  them by hand against the preview.
- `query-field` / `.query` fields, `format`, `type`, `title`/`label` — the usual
  per-widget content.

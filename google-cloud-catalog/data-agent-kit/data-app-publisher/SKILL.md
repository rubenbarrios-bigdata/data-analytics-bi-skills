---
name: data-app-publisher
description: |
  Deploy and publish a Data App to the customer's Looker instance via the
  Data Apps extension framework. Trigger when publishing, deploying, or releasing
  a finished Data App to Looker.
---

You are publishing a completed, verified Data App into the customer's Looker instance.

## 1. Strict Requirement — Never Publish Autonomously

**Under NO circumstances should an AI agent run `publish-data-app.py` on its own.**
Publishing creates real, persistent resources on the customer's Looker instance and is strictly an interactive action requiring explicit user instruction. (Similarly, never run toolkit updates autonomously; see `skills/toolkit-updater/SKILL.md`.)

## 2. Configuration & Prerequisites

Publishing requires configuration from `data-apps-config.json` (written during bootstrap):
- **`data-apps-config.json`** (repo root) — Looker instance `base_url`, `client_id`, `client_secret`, and `publish_folder_id`.

To verify the instance supports inline extensions before publishing:
```bash
python3 scripts/verify-install.py
```

## 3. Publishing the Data App

When the user explicitly instructs you to publish, run:

```bash
python3 skills/data-app-publisher/tools/publish-data-app.py \
  --def apps/<app-name>/app.js \
  --title "<App Title>"
```

### Re-publishing an existing app in place:
When updating an already published app, pass `--dashboard-id <id>` using the dashboard ID printed by the previous publish:
```bash
python3 skills/data-app-publisher/tools/publish-data-app.py \
  --def apps/<app-name>/app.js \
  --title "<App Title>" \
  --dashboard-id <id>
```
Without `--dashboard-id`, every publish creates *another* dashboard at a new URL and leaves the old one behind.

> [!IMPORTANT]
> If the output contains `WARNING: Looker's dashboard header stays visible`, tell the user. Their Looker instance cannot hide the dashboard header, so the app works but renders below Looker's title and filter bar instead of full screen. The publish still succeeded; do not retry it.

> [!NOTE]
> Published apps should always reside under `apps/<app-name>/app.js`. Reference apps under `examples/` are overwritten during toolkit updates; publishing an app directly from `examples/` will warn the author to copy the app into `apps/` to preserve in-file publish metadata across updates.


### Automatic Metadata Tracking:
On initial publish, `publish-data-app.py` writes the dashboard identity back into the source `app.js` JSDoc header:
- `@looker-dashboard-id <id>`
- `@looker-instance <url>`
- `@published-at <iso8601>`
- `@published-by <author>`
- `@toolkit-version <version>`

On subsequent publishes with `--dashboard-id`, it updates `@published-at`, `@published-by`, and `@toolkit-version` (along with `@looker-dashboard-id` and `@looker-instance`) to reflect the latest publish state, while verifying that the target Looker instance matches the recorded `@looker-instance`. If the author lookup is unavailable, it records `@published-by unknown`.

### Architecture & Entity Model:
- **A Data App is a dashboard-mounted inline extension** — publishing creates both a **Dashboard** entity and an **Inline Extension** entity in Looker's database (`POST /data_app_extension`). The single dashboard element references the extension via `extension_id: "db::<uuid>"`. Looker serves `app.js` directly to the extension frame as an ES module.
- **Authoring Permissions & Entitlements** — Data Apps can be created by authors with standard `save_dashboards` permissions rather than developer `develop` permissions, because Looker fixes and manages the sandbox entitlements server-side.
- **The runtime is imported by URL** — the app imports `data-app.js` and `lit.mjs`, and publish rewrites those two specifiers to the hosted bundle (`publish-data-app.py`), which also prepends `window.__lookerDataAppMeta` with `publishedAt` from `@published-at`, and nothing else. The runtime stays out of the database and stays HTTP-cacheable across every dashboard.
- **Extension layout, always full bleed** — The app gets the `extension` layout (one element, full screen) with Looker's dashboard header (title, filter bar, reload, menu) and the tile title hidden, because the app draws its own. This is the only mode; there is no flag to keep Looker's header. Re-publishing with `--dashboard-id` hides them again if they were showing.
- **Instance requirement** — Requires the `inline_extensions` feature on the Looker instance.

## 4. URL Presentation Rule

**Always present the real Looker instance URL** to the user (e.g. `https://<customer-instance>.looker.com/dashboards/<id>`).
Never present localhost or proxy URLs.

## 5. Error Recovery & Structured Envelopes

`publish-data-app.py` outputs structured JSON error envelopes on failure (`ERROR_ENVELOPE_JSON: <json>`):

* **`def_too_large`:** The app definition exceeds the payload size limit (default 900 KB). Trim inline mock data or base64 assets.
* **`permission_denied` (HTTP 403):** The API user lacks `save_dashboards` or extension management permissions.
* **`folder_not_found` (HTTP 404):** `publish_folder_id` does not exist or is not viewable by the API user.
* **`data_app_extension_unavailable`:** The Looker instance lacks the `inline_extensions` feature.

## 6. Server Cleanup

When publishing is complete, stop any running preview server:
```bash
python3 skills/data-app-previewer/tools/stop-preview.py
# (alternate shortcut: make stop)
```

#!/usr/bin/env python3
"""
Publish a Data App to the customer's Looker instance.

Creates a new Looker dashboard, adds an extension tile pointing at the app,
and puts the dashboard in the `extension` layout so it renders full screen.
Every publish is full bleed: Looker's dashboard header and the tile title are
hidden, because the app draws its own.

The app **is** the extension. Its JavaScript is stored as the `code` of a
Data App extension (POST /data_app_extension) and the dashboard element
references it as `extension_id: "db::<uuid>"`. Nothing is written to
`body_text`, and there is no tile host to load first -- Looker serves the app
to the extension frame directly, as an ES module.

A Data App extension gets its entitlements and mount points assigned by the
server and needs only `save_dashboards` to create, which is what lets an ordinary
dashboard author publish without developer rights. The instance must have the
`inline_extensions` feature; there is no fallback path.

Talks to Looker via urllib -- no looker-sdk dependency. Config search order:
--config <path>, then data-apps-config.json at the repo root.
The chosen file must contain client_id + client_secret plus either base_url
or looker_instance_url; credentials may also come from LOOKERSDK_* / LOOKER_*
environment variables.

Usage:
    python3 skills/data-app-publisher/tools/publish-data-app.py --def <path.js> --title "<title>"
                                 [--folder-id <id>]
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import ssl
import sys
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def _base_ssl_context():
    """A usable CA bundle, nothing host-specific.

    macOS Python.org installs ship without CA roots wired into
    OpenSSL, so probe a few well-known bundle locations.
    """
    candidates = [
        "/etc/ssl/cert.pem",
        "/etc/pki/tls/certs/ca-bundle.crt",
        "/etc/ssl/certs/ca-certificates.crt",
        "/opt/homebrew/etc/openssl@3/cert.pem",
        "/usr/local/etc/openssl@3/cert.pem",
    ]
    cafile = next((p for p in candidates if os.path.exists(p)), None)
    if cafile is None:
        try:
            import certifi  # type: ignore
            cafile = certifi.where()
        except ImportError:
            return ssl.create_default_context()
    return ssl.create_default_context(cafile=cafile)


def _looker_ssl_context():
    """The base context, plus trust for a private CA if the instance opted in.

    A Looker instance behind a private CA — a local dev instance, or an
    internal deployment — serves a certificate the base store has no reason
    to trust, and such certs sometimes carry a key below OpenSSL's default
    security level. Point LOOKER_CA_BUNDLE at that certificate to trust it.
    Verification stays on: the cert is added as an anchor, never bypassed.
    """
    ctx = _base_ssl_context()
    extra_ca = os.environ.get("LOOKER_CA_BUNDLE")
    if extra_ca and os.path.exists(extra_ca):
        ctx.load_verify_locations(cafile=extra_ca)
        # Scoped to this context alone, not installed as the process
        # default: unqualified urlopen() calls must not inherit a cipher
        # floor lowered for a Looker instance's cert.
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    return ctx


# The default opener every unqualified urlopen() uses gets the base context,
# not the Looker one, so a weakened cipher floor never reaches a host that
# didn't opt into it. login() and call()
# pass _LOOKER_SSL_CTX explicitly instead of relying on this default.
urllib.request.install_opener(
    urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=_base_ssl_context())))

_LOOKER_SSL_CTX = _looker_ssl_context()


def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"error: config file not found at {path}. "
                 "Run scripts/bootstrap.sh to create it.")
    return json.loads(path.read_text(encoding="utf-8"))


# Guard against apps too large for the inline extension `code` column, which
# the server caps at 5 MB. Default well under it so the failure is a structured
# envelope with a fix, not an unmapped Looker 422 mid-publish. Override
# per-customer via `size_limit_fallback.max_def_bytes` in the skill config.
DEFAULT_MAX_DEF_BYTES = 900_000


def _die_with_envelope(env: dict) -> None:
    """Emit a structured error envelope on stderr (human lines + the
    machine-parseable ERROR_ENVELOPE_JSON) and exit non-zero."""
    sys.stderr.write("error: " + env["message"] + "\n")
    sys.stderr.write("  hint: " + env["hint"] + "\n")
    sys.stderr.write("  suggested_action: " + env["suggested_action"] + "\n")
    sys.stderr.write("ERROR_ENVELOPE_JSON: " + json.dumps(env) + "\n")
    sys.exit(1)


def check_def_size(html: str, cfg: dict) -> None:
    fallback = cfg.get("size_limit_fallback")
    if not isinstance(fallback, dict):
        # Tolerate a malformed value (string, number, null) — the guard
        # should never be the thing that breaks a publish.
        fallback = {}
    limit = int(fallback.get("max_def_bytes") or DEFAULT_MAX_DEF_BYTES)
    size = len(html.encode("utf-8"))
    if size <= limit:
        return
    _die_with_envelope({
        "error_type": "def_too_large",
        "message": (f"app is {size:,} bytes; the configured limit is "
                    f"{limit:,} bytes."),
        "hint": ("The app is stored as the inline extension's code, which "
                 "the server caps at 5 MB. Apps this large are almost always "
                 "inline mock data or base64 assets that shouldn't ship."),
        "suggested_action": ("Trim any large embedded data or assets, or "
                             "split the app into multiple tiles. Raise "
                             "size_limit_fallback.max_def_bytes in the skill "
                             "config if the app is genuinely irreducible."),
    })


def login(base_url, client_id, client_secret):
    body = urllib.parse.urlencode(
        {"client_id": client_id, "client_secret": client_secret}
    ).encode()
    req = urllib.request.Request(
        f"{base_url}/api/4.0/login", data=body, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60, context=_LOOKER_SSL_CTX) as r:
        return json.loads(r.read())["access_token"]


def _hint_for_publish_error(method, path, code, body_text, base_url):
    """Build a hint + suggested action tuned to the most common publish failures."""
    lowered = (body_text or "").lower()
    if code == 401:
        return ("Your Looker API key is invalid or expired. Regenerate "
                "the key in the Looker admin UI and update data-apps-config.json.",
                "Re-run scripts/bootstrap.sh to re-prompt for credentials.")
    if code == 403:
        return (f"The API user is authenticated but lacks permission for "
                f"{method} {path}. For dashboard publishing the user needs "
                f"`develop` (or at minimum `manage_models` + dashboard write).",
                f"Add the missing role in {base_url}/admin/roles, or use "
                f"admin credentials.")
    if code == 404 and "folder" in lowered:
        return ("The configured publish_folder_id doesn't exist or the API "
                "user can't see it.",
                "Open the customer's data-apps-config.json, set "
                "publish_folder_id to a valid folder, and retry.")
    if code == 404:
        return (f"{method} {path} returned 404. Most likely a stale id "
                "(dashboard, element, or layout was deleted between "
                "calls), or the path is wrong.",
                "Re-run publish-data-app.py to recreate the dashboard "
                "from scratch.")
    if code == 422 and "extension_id" in lowered:
        return ("Looker doesn't recognize the extension_id. It is derived "
                "from the inline extension this script just upserted, so "
                "the extension was most likely deleted between that call "
                "and this one.",
                "Re-run publish-data-app.py; it will recreate the inline "
                "extension and reference the new id.")
    if code == 422:
        return ("Looker rejected the request body as invalid. The HTTP "
                "body has the specific field that's wrong.",
                "Inspect `message` for the field name and fix the publish "
                "script's payload, or update the app code.")
    return ("Unmapped Looker API error. The full response body is in `message`.",
            "Open Looker's API docs for this endpoint and match the error "
            "against the documented shape.")


def _publish_error_envelope(method, path, code, body_text, base_url):
    """Structured error envelope, shape-compatible with serve.py."""
    hint, action = _hint_for_publish_error(method, path, code, body_text, base_url)
    return {
        "error_type": f"looker_http_{code}",
        "message": f"{method} {path} -> HTTP {code}: {body_text[:1500]}",
        "hint": hint,
        "suggested_action": action,
    }


def call(base, token, method, path, body=None, raise_on_err=True):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{base}/api/4.0{path}", data=data, method=method,
        headers={"Authorization": f"token {token}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=_LOOKER_SSL_CTX) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        if raise_on_err:
            # Emitted as both human-readable lines AND a JSON envelope on
            # stderr — the AI agent driving this script can parse the
            # envelope to self-correct without needing to scrape stdout.
            _die_with_envelope(
                _publish_error_envelope(method, path, e.code, raw, base))
        return e.code, raw


# --- data app extensions ----------------------------------------------------
#
# A Data App is published as its own inline extension: the app's JavaScript is
# the extension bundle (`code`), and a dashboard element references it as
# `extension_id: "db::<uuid>"`. Nothing is stored in body_text, and there is no
# tile host to load first -- Looker serves the app to the frame directly.
#
# Two properties of the `data_app` extension endpoint carry the security story,
# and both are enforced server-side rather than here:
#
#   * Entitlements and mount points are hardcoded by Looker, so an author
#     supplies code but never the powers it runs with.
#   * Creating one needs `save_dashboards` rather than `develop`, which is what
#     lets an ordinary dashboard author publish at all.
#
# The runtime is still imported by URL, so it stays out of the database and
# stays HTTP-cacheable across every tile on the instance.

# There is no fallback any more: publishing goes through a data app extension
# or not at all. An instance without the feature needs a release from before
# that changed, so say which knob to turn rather than implying a flag exists.
FALLBACK_HINT = (
    "  This version publishes via data app extensions. Enable the\n"
    "  `inline_extensions` feature on the instance, or use a release\n"
    "  from before inline-only publishing if you cannot.")


def _data_app_extension_unavailable(code, body, base):
    """Explain a non-200 from the /data_app_extension endpoint.

    The probe is a plain collection GET, so a non-200 nearly always means the
    capability is absent rather than the request being wrong. Looker reports
    that several different ways depending on how the feature is gated, and
    the distinction matters: a missing route is something the instance admin
    turns on, a 403 is something the API user's role fixes.
    """
    text = body if isinstance(body, str) else json.dumps(body or {})
    lowered = text.lower()

    if code == 404 and "sinatra::notfound" in lowered:
        # The route isn't registered at all -- the clearest possible signal
        # that the feature is off or the instance predates it.
        why = ("this instance has no /data_app_extension endpoint at all, so "
               "the\n  `inline_extensions` feature is off or the Looker "
               "version predates it.")
    elif code == 404:
        why = ("/data_app_extension returned 404. The `inline_extensions` "
               "feature is\n  most likely off on this instance.")
    elif code == 403:
        why = ("the API user is authenticated but not allowed to access "
               "/data_app_extension.\n  Either the `inline_extensions` feature "
               "is off, or this user is missing\n  dashboard author permissions "
               "(save_dashboards / access_data).")
    elif code == 400:
        why = ("/data_app_extension rejected the request as invalid, which on "
               "a plain\n  collection GET usually means the "
               "`inline_extensions` feature is off and\n  the route is a "
               "stub.")
    elif code >= 500:
        # Not a capability problem: the route is there and it broke. Saying
        # "unavailable" here would send someone to check a feature flag that
        # is already on.
        return (f"error: /data_app_extension on {base} returned HTTP {code}.\n"
                "  That's a server-side error, not a missing feature — the "
                "endpoint exists\n  but failed. Retry; if it persists, check "
                "the instance's logs.\n"
                f"{FALLBACK_HINT}\n"
                f"  Looker's response: {text[:300]}")
    else:
        why = f"/data_app_extension returned HTTP {code}."

    return (f"error: cannot publish to {base}:\n"
            f"  {why}\n"
            f"{FALLBACK_HINT}\n"
            f"  Looker's response: {text[:300]}")


DATA_APP_EXTENSION_PAGE_SIZE = 100
# A generous bound on how many pages to walk, not a real expectation of ever
# reaching it -- purely so a pagination param the endpoint doesn't respect
# can't spin the loop forever instead of failing.
DATA_APP_EXTENSION_MAX_PAGES = 200


def upsert_data_app_extension(base, token, name, title, app_code,
                              existing_id=None):
    """Create the inline extension holding the app, or update it.

    The app *is* the extension: `code` is the published app.js, loaded by the
    browser as an ES module. Nothing is stored in body_text.

    The dashboard element's `extension_id` is the only thing that says which
    row an app lives in, so it is the only thing consulted. `existing_id` is
    that reference; without one this creates a new row.

    Matching by name instead would silently couple dashboards. The name is
    derived from the title, Looker only requires titles to be unique per
    folder, so publishing the same title into two folders found the first
    app's row and overwrote its code -- leaving the first dashboard rendering
    the second app, with no error. An app is its own extension; two publishes
    are two apps unless the caller says otherwise with --dashboard-id.

    A reference to a row that no longer exists falls through to create, after
    which the caller's element PATCH repoints the dashboard at the new row.
    """
    match = None
    if existing_id and existing_id.startswith("db::"):
        code, out = call(base, token, "GET",
                         f"/data_app_extension/{existing_id[4:]}",
                         raise_on_err=False)
        if code == 200 and isinstance(out, dict):
            match = out

    # Entitlements and mount points are hardcoded server-side by Looker's dedicated
    # /data_app_extension endpoint (including core_api_methods and external_api_urls
    # for the runtime bundle host). The client sends only label, description, and app code.
    payload = {
        "name": name,
        "label": title,
        "description": f"Data App: {title}",
        "code": app_code,
    }

    if match:
        # Never rename an existing row: name is uniquely indexed, so pushing
        # the title-derived name onto a row found by id could collide with an
        # unrelated app's row and fail the whole publish with a 422.
        update_payload = {k: v for k, v in payload.items() if k != "name"}
        _, out = call(base, token, "PATCH",
                      f"/data_app_extension/{match['id']}", update_payload)
        return out, "updated"
    _, out = call(base, token, "POST", "/data_app_extension", payload)
    return out, "created"


def extension_name_for(title, override=None):
    """A name that cannot collide and never has to be kept up to date.

    Looker requires [a-zA-Z0-9-_] and indexes the column uniquely, so the
    name's only job is to stay out of the way. Deriving it from the title --
    with or without the folder -- does not manage that, because rows are
    never renamed on update: the name is identity and `label` carries the
    title. Rename a dashboard away from "Sales" and its row stays
    `data-app-sales` forever, so the next "Sales" published into that folder
    collides with a row nothing references any more. Deleting a dashboard
    without its row leaves the same trap.

    So: a readable prefix plus a UUID. The prefix is for whoever scans the
    list in Looker's admin UI, the UUID is what makes it unique -- in one
    call, with nothing to look up beforehand and nothing to reconcile after.
    The slug is cosmetic, so an empty, non-ASCII or very long title
    degrades it rather than failing.
    """
    if override:
        return override
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()[:64]
    return f"data-app-{slug or 'untitled'}-{uuid.uuid4()}"


# The appearance fields publish sets to hide Looker's chrome are newer than
# the rest of this flow. On an instance that predates them, POST /dashboards
# accepts the block and ignores it: the publish succeeds and the app renders
# inside Looker's header instead of full-bleed, with nothing said about why.
#
# The API self-describes, so that is detectable before anything is created,
# and _warn_header_stays_visible says so out loud.
# Two caveats found while wiring this up, both worth knowing:
#
#   * WriteDashboard declares neither `appearance` nor `settings`, even on an
#     instance where sending `appearance` demonstrably works -- so the probe
#     has to target the DashboardAppearance definition, and POST accepting
#     the field stays undocumented behaviour either way.
#   * DashboardLayout.type is an untyped string with no enum, so the same
#     trick cannot confirm the `extension` layout type. That one stays a
#     post-creation check (see the layout PATCH below).
APPEARANCE_PROBE_FIELD = "show_dashboard_header"


def _supports_dashboard_appearance(base, token):
    """Whether this instance's API declares the appearance field we set.

    Returns True/False, or None when the probe itself could not be completed
    -- an inconclusive probe must not block a publish that would otherwise
    work, so callers treat None as "proceed as before".
    """
    code, spec = call(base, token, "GET", "/swagger.json", raise_on_err=False)
    if code != 200 or not isinstance(spec, dict):
        return None
    definitions = spec.get("definitions")
    if not isinstance(definitions, dict):
        return None
    appearance = definitions.get("DashboardAppearance")
    if not isinstance(appearance, dict):
        # The definition is absent entirely: appearance isn't a concept on
        # this instance, which is a genuine negative rather than a failed
        # probe.
        return False
    props = appearance.get("properties")
    if not isinstance(props, dict):
        return None
    return APPEARANCE_PROBE_FIELD in props


def _apply_extension_layout(base, token, dash_id):
    """Switch a freshly created dashboard to the `extension` layout.

    Only the create path needs this. An update targets a dashboard that
    is already in this layout -- _open_dashboard_for_update refuses one
    that is not -- so it must never reach the cleanup below, which
    deletes the dashboard on failure.
    """
    code, ddash = call(base, token, "GET", f"/dashboards/{dash_id}")
    layouts = ddash.get("dashboard_layouts") or []
    active = next((l for l in layouts if l.get("active")), layouts[0] if layouts else None)
    if not active:
        sys.exit("error: dashboard has no layout after creation")
    layout_id = active["id"]
    # `extension` renders a single element full screen. It has to be
    # PATCHed on after creation: POST /dashboards ignores a layout type
    # supplied at creation and always returns `newspaper`.
    #
    # This is the second capability publishing depends on, and unlike the
    # endpoint probe it cannot be checked before creating anything: the
    # layout only exists once the dashboard does. An instance can have
    # inline extensions and still not take this layout type, in which
    # case the PATCH reports success and quietly returns `newspaper`.
    _, lay = call(base, token, "PATCH", f"/dashboard_layouts/{layout_id}",
                  {"type": "extension"})
    got = lay.get("type") if isinstance(lay, dict) else None
    if got is None:
        # A 2xx with an empty body (some Looker versions return 204, or a
        # 200 with nothing echoed) must not read the same as the PATCH
        # actually reporting `newspaper` -- call() already raised on a
        # non-2xx, so an empty body here means the request succeeded and
        # the response just didn't say what it did. Re-read the layout
        # directly rather than deleting a dashboard the PATCH may have
        # configured correctly.
        _, relay = call(base, token, "GET", f"/dashboard_layouts/{layout_id}",
                        raise_on_err=False)
        got = relay.get("type") if isinstance(relay, dict) else None
    if got != "extension":
        # The dashboard that exists at this point is unusable: an
        # extension element stranded in a newspaper layout, which is not
        # a view anyone asked for. Bin it rather than leave it for
        # someone to find. Best-effort: report the id either way so
        # nothing is lost silently if the cleanup itself fails.
        del_code, _ = call(base, token, "DELETE", f"/dashboards/{dash_id}",
                           raise_on_err=False)
        cleanup = (f"  Removed the half-built dashboard {dash_id}."
                   if del_code in (200, 204)
                   else f"  Could not remove dashboard {dash_id} "
                        f"(HTTP {del_code}) — delete it by hand.")
        sys.exit(
            f"error: this instance accepted the inline extension but not "
            f"the `extension`\n  dashboard layout — the type came back "
            f"{got!r} instead.\n"
            f"{cleanup}\n"
            f"{FALLBACK_HINT}")
    print(f"[4/5] layout {layout_id} type=extension, full screen")
    return layout_id


def _full_bleed_appearance():
    """A Data App draws its own header, so the host chrome is redundant.

    show_dashboard_header covers the title, filter bar, reload and menu;
    the rest is geometry so the app reaches the edges.
    """
    return {
        "show_dashboard_header": False,
        "page_side_margins": 0,
        "tile_space_between": 0,
        "tile_shadow": False,
    }


def _warn_header_stays_visible():
    """Say, loudly, that this instance cannot hide Looker's header.

    Full bleed is the only mode, but an instance without the appearance
    fields still gets a working tile, so this warns rather than fails.
    publish() prints it before writing anything and again beside the
    dashboard link, where whoever ran the publish is already looking.
    """
    print(f"WARNING: Looker's dashboard header stays visible on this dashboard.\n"
          f"  This instance's API does not declare "
          f"DashboardAppearance.{APPEARANCE_PROBE_FIELD}, so the dashboard\n"
          f"  title, filter bar, reload button and menu cannot be hidden here. "
          f"The app works,\n"
          f"  but renders below Looker's header instead of full screen. "
          f"Re-publishing with\n"
          f"  --dashboard-id after the instance gains support hides it.")


def _open_dashboard_for_update(base, token, dashboard_id):
    """Resolve --dashboard-id to (dashboard, element, active_layout), or exit.

    An update writes to a dashboard the caller named by id, so a wrong id
    has to fail rather than overwrite whatever it happened to land on.
    Every check here exists to make that failure loud: the dashboard must
    exist, hold exactly one extension tile, and already be in the
    `extension` layout -- together, the shape only this tool produces.
    """
    code, dash = call(base, token, "GET", f"/dashboards/{dashboard_id}",
                      raise_on_err=False)
    if code == 404:
        sys.exit(f"error: no dashboard {dashboard_id} on this instance.\n"
                 "  Publish without --dashboard-id to create a new one.")
    if code != 200 or not isinstance(dash, dict):
        sys.exit(f"error: could not read dashboard {dashboard_id} "
                 f"(HTTP {code}).")

    all_elements = dash.get("dashboard_elements") or []
    elements = [e for e in all_elements if e.get("type") == "extension"]
    if len(elements) != 1:
        sys.exit(
            f"error: dashboard {dashboard_id} ({dash.get('title')!r}) holds "
            f"{len(elements)} extension\n"
            f"  tiles, not 1, out of {len(all_elements)} tiles total.\n"
            "  This tool only updates a dashboard it published, which is a "
            "single\n  extension tile. Check the id, or publish without "
            "--dashboard-id to\n  create a new dashboard.")

    layouts = dash.get("dashboard_layouts") or []
    active = next((l for l in layouts if l.get("active")),
                  layouts[0] if layouts else None)
    if not active:
        sys.exit(f"error: dashboard {dashboard_id} has no layout to update.")
    if active.get("type") != "extension":
        sys.exit(
            f"error: dashboard {dashboard_id} ({dash.get('title')!r}) uses the "
            f"{active.get('type')!r}\n  layout, not `extension`. That is not a "
            "dashboard this tool published, so\n  refusing to rewrite it. "
            "Check the id.")
    return dash, elements[0], active


def resolve_version(install_root: Path) -> str:
    """Reads the current toolkit version from VERSION file."""
    for candidate in [
        install_root / "VERSION",
        install_root / "dist" / "VERSION",
        install_root.parent / "dist" / "VERSION",
    ]:
        if candidate.is_file():
            try:
                v = candidate.read_text(encoding="utf-8").strip()
                if v:
                    return v
            except Exception:
                pass
    return "0.9.0"


CANONICAL_BROWSER_ASSETS = "https://www.gstatic.com/looker-data-apps"
CANONICAL_SHARED_BASE = CANONICAL_BROWSER_ASSETS


def resolve_shared_urls(cfg: dict, install_root: Path) -> tuple:
    """Resolves where a published tile loads its runtime and vendored libraries.

    Returns `(runtime_url, vendor_url)`.

    A tile extension must load an immutable, version-pinned runtime, so
    releasing a new version can never alter an app that is already published.
    Vendored libraries and runtime assets live under `browser_assets_url`.
    """
    browser_assets = str(cfg.get("browser_assets_url") or CANONICAL_BROWSER_ASSETS).rstrip("/")
    if "/versions/" in browser_assets or browser_assets.endswith("/dev"):
        runtime = browser_assets
        if "/versions/" in browser_assets:
            vendor_url = browser_assets.rsplit("/versions/", 1)[0] + "/vendor"
        else:
            vendor_url = browser_assets.rstrip("/dev") + "/vendor"
    else:
        runtime = f"{browser_assets}/versions/{resolve_version(install_root)}"
        vendor_url = f"{browser_assets}/vendor"
    return runtime, vendor_url





def prepare_production_content(raw_content: str, runtime_url: str, vendor_url: str) -> str:
    """Prepares authored app code for tile extension publication.

    Rewrites relative imports to point at immutable bundle host assets,
    strips any leftover selection marker from the retired local editor,
    and prepends window.__lookerDataAppMeta with publishedAt from @published-at.
    """
    prod = re.sub(
        r"['\"][^'\"]*?data-app\.js['\"]",
        f"'{runtime_url}/data-app.js'",
        raw_content,
    )
    prod = re.sub(
        r"['\"][^'\"]*?lit\.mjs['\"]",
        f"'{vendor_url}/lit/3.3.1/lit.mjs'",
        prod,
    )
    # The retired local editor wrote `data-cd-selected` markers into app source;
    # apps authored before its removal may still carry one. Keep production defs clean.
    prod = re.sub(r'\s*data-(?:cd|app)-selected="true"', "", prod)

    meta = {}
    m = _find_header_jsdoc(raw_content)
    if m:
        jsdoc = m.group(1)
        pub_m = re.search(r"@published-at\s+([^\r\n*]+)", jsdoc, re.IGNORECASE)
        if pub_m:
            meta["publishedAt"] = pub_m.group(1).strip()

    if meta:
        meta_json = json.dumps(meta)
        meta_injection = f"window.__lookerDataAppMeta = Object.assign(window.__lookerDataAppMeta || {{}}, {meta_json});\n"
        m_prod = _find_header_jsdoc(prod)
        if m_prod:
            end = m_prod.end()
            # If followed by a newline, place after the newline
            if end < len(prod) and prod[end] == "\n":
                end += 1
            prod = prod[:end] + meta_injection + prod[end:]
        else:
            prod = meta_injection + prod

    return prod


METADATA_TAGS = (
    "looker-dashboard-id",
    "looker-instance",
    "published-at",
    "published-by",
    "toolkit-version",
)
TAG_REGEX = re.compile(
    r"^\s*\*\s*@(looker-dashboard-id|looker-instance|published-at|published-by|toolkit-version)\s+(.+?)\s*$",
    re.MULTILINE,
)


def _find_header_jsdoc(content: str) -> re.Match | None:
    """Find a leading header JSDoc block before any executable code or imports."""
    m = re.search(r"/\*\*([\s\S]*?)\*/", content)
    if not m:
        return None
    prefix = content[:m.start()]
    if prefix.startswith("#!"):
        prefix = prefix.split("\n", 1)[1] if "\n" in prefix else ""
    cleaned = re.sub(r"/\*[\s\S]*?\*/", "", prefix)
    cleaned = re.sub(r"//.*$", "", cleaned, flags=re.MULTILINE)
    if cleaned.strip():
        return None
    return m


def parse_metadata(content: str) -> dict:
    """Parse publish metadata from the leading header JSDoc block in content.

    Returns a dict mapping tag names to string values. Missing or malformed
    tags are omitted. Non-header JSDoc blocks are ignored.
    """
    m = _find_header_jsdoc(content)
    if not m:
        return {}
    res = {}
    for match in TAG_REGEX.finditer(m.group(1)):
        tag, val = match.group(1), match.group(2).strip()
        if val:
            res[tag] = val
    return res


def upsert_metadata(content: str, updates: dict) -> str:
    """Upsert publish metadata tags in place within the leading header JSDoc block.

    If no header JSDoc block exists before code statements, a new header block
    is prepended at the top of the file.
    """
    m = _find_header_jsdoc(content)
    if not m:
        lines = ["/**"]
        for tag in METADATA_TAGS:
            if tag in updates and updates[tag]:
                lines.append(f" * @{tag:<21} {updates[tag]}")
        lines.append(" */\n\n")
        header = "\n".join(lines)
        if content.startswith("#!"):
            parts = content.split("\n", 1)
            shebang = parts[0] + "\n"
            rest = parts[1] if len(parts) > 1 else ""
            return shebang + header + rest
        return header + content

    block = m.group(1)
    replaced = set()
    new_lines = []
    for line in block.split("\n"):
        match = TAG_REGEX.match(line)
        if match:
            tag = match.group(1)
            if tag in updates and updates[tag]:
                replaced.add(tag)
                new_lines.append(f" * @{tag:<21} {updates[tag]}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    to_add = [tag for tag in METADATA_TAGS if tag in updates and tag not in replaced and updates[tag]]
    if to_add:
        while new_lines and (not new_lines[-1].strip() or new_lines[-1].strip() == "*"):
            new_lines.pop()
        new_lines.append(" *")
        for tag in to_add:
            new_lines.append(f" * @{tag:<21} {updates[tag]}")
        new_lines.append(" ")

    new_block = "\n".join(new_lines)
    return content[:m.start(1)] + new_block + content[m.end(1):]


def fetch_authenticated_user(base: str, token: str) -> str | None:
    """Look up the authenticated user's display name via GET /user.

    Returns display_name, or 'first last', or None if unavailable.
    Failures are silent and non-fatal.
    """
    try:
        code, me = call(base, token, "GET", "/user", raise_on_err=False)
        if code == 200 and isinstance(me, dict):
            name = me.get("display_name")
            if name and str(name).strip():
                return " ".join(str(name).split())
            first = me.get("first_name") or ""
            last = me.get("last_name") or ""
            full = " ".join(f"{first} {last}".split())
            if full:
                return full
    except Exception:
        pass
    return None


def check_instance_mismatch(meta: dict, target_url: str, dashboard_id: str | None = None, fatal: bool = True) -> bool:
    """Guard against updating a dashboard across different Looker instances."""
    recorded_instance = meta.get("looker-instance")
    if not recorded_instance:
        return False

    def _norm(u: str) -> str:
        return u.strip().rstrip("/").lower()

    if _norm(recorded_instance) != _norm(target_url):
        if fatal:
            dash_str = f"dashboard {dashboard_id}" if dashboard_id else "this dashboard"
            sys.exit(
                f"error: app source was previously published to {recorded_instance},\n"
                f"  but the current target instance is {target_url}.\n"
                f"  Refusing to update {dash_str} across different instances.\n"
                f"  Publish without --dashboard-id to create a new dashboard on {target_url}."
            )
        else:
            print(f"note: this app was previously published to {recorded_instance}; "
                  f"that record is being replaced with {target_url}.")
            return True
    return False


def publish(args):
    # Locate config.json. The skill ships symlinked into the agent's
    # skill directory, so __file__ usually points through that symlink.
    # Path.resolve() walks the symlink to the real on-disk install location
    # before we navigate parents, so install_root lands in the actual install directory.
    script = Path(__file__).resolve()
    install_root = script.parent.parent.parent.parent  # .../<install dir>

    if args.config:
        cfg_path = Path(args.config)
        cfg = load_config(cfg_path)
    else:
        # Standard configuration: search candidate locations
        # 1. install_root / data-apps-config.json
        # 2. Path.cwd() / data-apps-config.json
        # 3. Parent directories (walking up from script location for developer checkouts)
        candidates = [
            install_root / "data-apps-config.json",
            Path.cwd() / "data-apps-config.json",
        ]
        curr = script.parent
        while curr != curr.parent:
            candidates.append(curr / "data-apps-config.json")
            curr = curr.parent

        cfg_file = None
        for candidate in candidates:
            if candidate.is_file():
                cfg_file = candidate
                break

        if cfg_file:
            cfg = load_config(cfg_file)
            cfg_path = str(cfg_file)
        else:
            cfg = {}
            cfg_path = "environment"

    # Environment variables override or provide config
    base = (os.environ.get("LOOKERSDK_BASE_URL") or
            os.environ.get("LOOKER_BASE_URL") or
            cfg.get("base_url") or
            cfg.get("looker_instance_url") or "").rstrip("/")
    cid = (os.environ.get("LOOKERSDK_CLIENT_ID") or
           os.environ.get("LOOKER_CLIENT_ID") or
           cfg.get("client_id"))
    sec = (os.environ.get("LOOKERSDK_CLIENT_SECRET") or
           os.environ.get("LOOKER_CLIENT_SECRET") or
           cfg.get("client_secret"))
    if not (base and cid and sec):
        sys.exit(
            f"error: Looker credentials missing. Looked at {cfg_path} and environment variables.\n"
            "Set LOOKERSDK_BASE_URL, LOOKERSDK_CLIENT_ID, LOOKERSDK_CLIENT_SECRET "
            "or re-run scripts/bootstrap.sh."
        )
    folder_id = args.folder_id or os.environ.get("LOOKER_PUBLISH_FOLDER_ID") or cfg.get("publish_folder_id") or "1"

    # Human-facing origin: the URL a person opens, which is not necessarily
    # the API base the client talks to (a proxied or split-port instance
    # serves the UI elsewhere). Only used for the link printed on success.
    display_base = (cfg.get("target_url") or cfg.get("looker_instance_url")
                    or base).rstrip("/")

    raw_content = Path(args.def_path).read_text(encoding="utf-8")
    check_def_size(raw_content, cfg)
    runtime_url, vendor_url = resolve_shared_urls(cfg, install_root)
    print(f"def: {args.def_path} ({len(raw_content):,} bytes)")
    print(f"target: {base}")
    print(f"folder: {folder_id}")
    print(f"runtime: {runtime_url}")
    print(f"vendor: {vendor_url}")
    print()

    if not args.dashboard_id and not args.title:
        sys.exit("error: the following arguments are required: --title")

    token = login(base, cid, sec)

    existing_meta = parse_metadata(raw_content)

    # Resolve --dashboard-id before anything is written. A bad id costs
    # nothing this way; validated after the upsert below, it would already
    # have rewritten the extension on its way to failing.
    update_target = None
    if args.dashboard_id:
        check_instance_mismatch(existing_meta, display_base, args.dashboard_id)
        update_target = _open_dashboard_for_update(
            base, token, args.dashboard_id)

    # Resolved before the dashboard exists so an unsupported instance is
    # reported up front rather than as a dashboard that quietly came out
    # looking wrong. Only a definite "no" withholds the appearance block; an
    # inconclusive probe (None) sends it as usual.
    header_hideable = _supports_dashboard_appearance(base, token) is not False
    if not header_hideable:
        _warn_header_stays_visible()
        print()

    author = fetch_authenticated_user(base, token)
    current_version = resolve_version(install_root)
    pub_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    resolved_def = Path(args.def_path).resolve()
    candidate_roots = [install_root, install_root / "dist"]
    if args.config:
        cfg_dir = Path(args.config).resolve().parent
        candidate_roots.extend([cfg_dir, cfg_dir / "dist"])
    cur = resolved_def.parent
    while cur != cur.parent:
        if (cur / "data-apps-config.json").exists() or (cur / "VERSION").exists():
            candidate_roots.extend([cur, cur / "dist"])
            break
        cur = cur.parent

    for root in candidate_roots:
        ex_dir = (root / "examples").resolve()
        try:
            resolved_def.relative_to(ex_dir)
            print("warning: publishing directly from examples/ — devtools updates will overwrite\n"
                  "         this file. Copy the app into apps/<name>/app.js to keep its publish metadata.")
            break
        except ValueError:
            pass

    updating = update_target is not None
    if updating:
        dash, el, layout = update_target
        dash_id, el_id, layout_id = dash["id"], el["id"], layout["id"]
        if not args.title:
            args.title = dash.get("title") or "Data App"
        print(f"[1/5] dashboard {dash_id} opened: {dash.get('title')!r}")

        meta_updates = {
            "looker-dashboard-id": str(dash_id),
            "looker-instance": display_base,
            "published-at": pub_time,
            "toolkit-version": current_version,
            "published-by": author if author else "unknown",
        }
        original_content = raw_content
        updated_source = upsert_metadata(raw_content, meta_updates)
        if updated_source != raw_content:
            Path(args.def_path).write_text(updated_source, encoding="utf-8")
            raw_content = updated_source

        try:
            prod_content = prepare_production_content(raw_content, runtime_url, vendor_url)
            check_def_size(prod_content, cfg)

            ext, verb = upsert_data_app_extension(
                base, token,
                extension_name_for(args.title, args.inline_name),
                args.title, prod_content,
                existing_id=el.get("extension_id"))
            extension_id = f"db::{ext['id']}"
            print(f"[2/5] data app extension {verb}: {extension_id} "
                  f"({ext.get('code_size', 0):,} bytes)")

            # Appearance and title_hidden are sent on every update, not only
            # on create, so a dashboard published before full bleed was the
            # only mode -- or edited in Looker since -- converges on it.
            dash_updates = {}
            if dash.get("title") != args.title:
                dash_updates["title"] = args.title
                print(f"      title -> {args.title!r}")
            if header_hideable:
                dash_updates["appearance"] = _full_bleed_appearance()
            if dash_updates:
                call(base, token, "PATCH", f"/dashboards/{dash_id}", dash_updates)

            el_updates = {}
            if el.get("extension_id") != extension_id:
                el_updates["extension_id"] = extension_id
                print(f"      extension_id -> {extension_id}")
            if el.get("title") != args.title:
                el_updates["title"] = args.title
            if el.get("title_hidden") is not True:
                el_updates["title_hidden"] = True
                print("      title_hidden -> True")
            if el_updates:
                call(base, token, "PATCH", f"/dashboard_elements/{el_id}",
                     el_updates)
            print(f"[3/5] dashboard_element reused: id={el_id}")
            print("[4/5] element configured (app code lives in the extension)")
            print(f"      layout {layout_id} type=extension, unchanged")
        except BaseException:
            if updated_source != original_content:
                Path(args.def_path).write_text(original_content, encoding="utf-8")
            raise
    else:
        check_instance_mismatch(existing_meta, display_base, fatal=False)

        dash_body = {"title": args.title, "folder_id": str(folder_id)}
        if header_hideable:
            dash_body["appearance"] = _full_bleed_appearance()
        code, dash = call(base, token, "POST", "/dashboards", dash_body)
        dash_id = dash["id"]
        print(f"[1/5] dashboard created: id={dash_id}")

        meta_updates = {
            "looker-dashboard-id": str(dash_id),
            "looker-instance": display_base,
            "published-at": pub_time,
            "toolkit-version": current_version,
            "published-by": author if author else "unknown",
        }
        original_content = raw_content
        updated_source = upsert_metadata(raw_content, meta_updates)
        Path(args.def_path).write_text(updated_source, encoding="utf-8")
        raw_content = updated_source

        try:
            prod_content = prepare_production_content(raw_content, runtime_url, vendor_url)
            check_def_size(prod_content, cfg)

            ext, verb = upsert_data_app_extension(
                base, token,
                extension_name_for(args.title, args.inline_name),
                args.title, prod_content)
            extension_id = f"db::{ext['id']}"
            print(f"[2/5] data app extension {verb}: {extension_id} "
                  f"({ext.get('code_size', 0):,} bytes)")

            code, el = call(base, token, "POST", "/dashboard_elements", {
                "dashboard_id": str(dash_id),
                "type": "extension",
                "extension_id": extension_id,
                "title": args.title,
            })
            el_id = el["id"]
            print(f"[3/5] dashboard_element created: id={el_id}")

            # The app code lives in the extension, so the element only needs its
            # title settings. Hidden rather than blanked: the title still
            # identifies the tile in the API and in edit mode. This does not
            # depend on the appearance probe, so it applies on every instance.
            code, _ = call(base, token, "PATCH", f"/dashboard_elements/{el_id}",
                           {"title_hidden": True})
            print("[4/5] element configured (app code lives in the extension)")
            layout_id = _apply_extension_layout(base, token, dash_id)
        except BaseException:
            Path(args.def_path).write_text(original_content, encoding="utf-8")
            raise
    print(f"[5/5] done")
    print()
    print(f"{display_base}/dashboards/{dash_id}")
    if not header_hideable:
        print()
        _warn_header_stays_visible()
    if not updating:
        print()
        print("Re-publish over this dashboard, rather than creating another, "
              "with:")
        print(f"  --dashboard-id {dash_id}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--def", dest="def_path", required=True,
                   help="Path to the Data App JS")
    p.add_argument("--title", default=None,
                   help="Dashboard title (required unless updating an existing dashboard with --dashboard-id)")
    p.add_argument("--folder-id", help="Looker folder id (overrides config)")
    p.add_argument("--config", help="Path to a config file (defaults to data-apps-config.json)")
    p.add_argument("--inline-name", default=None,
                   help="Override the extension name derived from the title. "
                        "Without it each app gets its own extension; pointing "
                        "two publishes at one name makes the second overwrite "
                        "the first app's code.")
    p.add_argument("--dashboard-id",
                   help="Update this dashboard in place instead of creating a "
                        "new one. It must be a dashboard this tool published: "
                        "one extension tile in an `extension` layout. The "
                        "folder is never changed. Looker's dashboard header "
                        "and the tile title are hidden again if they were "
                        "showing.")
    publish(p.parse_args())


if __name__ == "__main__":
    main()

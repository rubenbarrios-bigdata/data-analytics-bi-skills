#!/usr/bin/env python3
"""Multi-tiered Post-Creation QA & Verification Tool for Looker Data Apps.

Runs progressive validation stages to catch and diagnose dashboard failures
before the human sees them:
  Stage 1: JavaScript syntax & compilation check (e.g. catches unescaped quotes like "O'Hare").
  Stage 2: AST tile safety rules (catches storage, inline onclick, relative imports).
  Stage 3: Looker model & query dry-run (catches "Model Not Found", HTTP 422 bad fields, 0-row empties).
  Stage 4: Headless browser inspection & screenshot (catches stuck shimmer skeletons and visual error cards).

Usage:
    python3 skills/data-app-creator/tools/verify-app.py apps/<name>/app.js
    python3 skills/data-app-creator/tools/verify-app.py apps/<name>/app.js --no-browser
    python3 skills/data-app-creator/tools/verify-app.py apps/<name>/app.js --json

Exit 0: All checks passed (or warnings only).
Exit 1: Errors detected that require the agent to self-heal.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def _base_ssl_context():
    """A usable CA bundle, nothing host-specific."""
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
    ctx = _base_ssl_context()
    extra_ca = os.environ.get("LOOKER_CA_BUNDLE")
    if extra_ca and os.path.exists(extra_ca):
        ctx.load_verify_locations(cafile=extra_ca)
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")  # nosemgrep: python.lang.security.audit.insecure-transport.ssl.no-set-ciphers.no-set-ciphers
    return ctx


_LOOKER_SSL_CTX = _looker_ssl_context()


# ----------------------------------------------------------------------
# Stage 1: Syntax & Compile Check
# ----------------------------------------------------------------------

def check_syntax(path: Path) -> dict:
    """Check JavaScript syntax. Uses `node --check` if available,
    with a Python fallback for unbalanced quotes / template literals."""
    code = path.read_text(encoding="utf-8")
    lines = code.splitlines()

    # 1. Prefer Node.js syntax checker if installed
    node_bin = shutil.which("node")
    if node_bin:
        try:
            res = subprocess.run(
                ["node", "--input-type=module", "--check", "-"],
                input=code,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                shell=False,
            )
            if res.returncode != 0:
                err_text = res.stderr or res.stdout
                line_no = None
                col_no = None
                m = re.search(r"(?:\[stdin\]|:\s*|:)(\d+)(?::(\d+))?", err_text)
                if m:
                    line_no = int(m.group(1))
                    if m.group(2):
                        col_no = int(m.group(2))

                snippet = lines[line_no - 1] if line_no and line_no <= len(lines) else ""
                hint = "JavaScript syntax error."
                if "'" in snippet and any(token in snippet.lower() for token in ["o'hare", "o'clock", "o'"]):
                    hint = "Unescaped apostrophe inside a single-quoted string. Use double quotes or backticks, or escape with \\'."
                elif "unexpected identifier" in err_text.lower() and "'" in snippet:
                    hint = "Unescaped single quote/apostrophe inside a string literal. Use double quotes or escape with \\'."

                return {
                    "ok": False,
                    "engine": "node",
                    "error": err_text.strip(),
                    "line": line_no,
                    "column": col_no,
                    "snippet": snippet.strip()[:100],
                    "hint": hint,
                }
            return {"ok": True, "engine": "node"}
        except Exception:
            # Fall through to python check
            pass

    # 2. Pure Python Fallback (quote & bracket balance scanning)
    issues = []
    # Check for unescaped apostrophes inside single-quoted strings:
    # Matches words broken by an unescaped single quote (contractions, possessives, names like O'Hare)
    quote_issue_re = re.compile(r"""(?<!\\)'(?:[^'\\\n]|\\.)*?\b([a-zA-Z]+)(?<!\\)'([a-zA-Z]+)""")
    for idx, line in enumerate(lines, 1):
        m = quote_issue_re.search(line)
        if m:
            issues.append({
                "line": idx,
                "snippet": line.strip()[:100],
                "error": f"Suspected unescaped apostrophe in single-quoted string near '{m.group(1)}'{m.group(2)}'.",
                "hint": "Change enclosing quotes to double quotes (\"...\") or escape the apostrophe (\\').",
            })

    if issues:
        first = issues[0]
        return {
            "ok": False,
            "engine": "python_scanner",
            "error": first["error"],
            "line": first["line"],
            "snippet": first["snippet"],
            "hint": first["hint"],
        }

    return {"ok": True, "engine": "python_scanner"}


# ----------------------------------------------------------------------
# Stage 2: Tile Safety (AST Sandbox Constraints)
# ----------------------------------------------------------------------

RULES = [
    ("inline-handler",
     re.compile(r"""\bon(?:click|change|input|submit|load|error|mouse\w+|key\w+)\s*=\s*["']"""),
     "inline on* handler -- blocked by CSP. Use Lit event binding: @click=${() => ...}"),
    ("dialog",
     re.compile(r"(?<![.\w])(?:alert|confirm|prompt)\s*\("),
     "alert/confirm/prompt -- no-ops in the sandbox. Render a modal template instead."),
    ("storage",
     re.compile(r"\b(?:localStorage|sessionStorage)\b"),
     "storage throws in an opaque origin. Keep state in Lit component properties."),
    ("window-open",
     re.compile(r"""window\.open\s*\(|target\s*=\s*["']_blank["']"""),
     "window.open returns null in the sandbox. Render views inside the application."),
    ("relative-asset",
     re.compile(r"""\b(?:src|href)\s*=\s*["']\.{1,2}/"""),
     "relative URL to an external asset -- use an absolute URL or inline SVG."),
    ("duplicate-connect",
     re.compile(r"\bconnectExtensionHost\s*\("),
     "connectExtensionHost() is already called by the runtime. Use this.runQuery()."),
    ("outer-dom-mutation",
     re.compile(r"""\bdocument\.(?:body|documentElement)\.(?:classList|style|setAttribute)\b"""),
     "document.body/documentElement mutation. Scope theme classes to container: <div class=\"da-container\">"),
]
IMPORT_RE = re.compile(r"""^\s*import\s[^;]*?from\s*["'](\.[^"']*)["']""", re.M)
ID_RE = re.compile(r"""\bid\s*=\s*["']([A-Za-z][\w:.-]*)["']""")


def strip_comments(src: str) -> str:
    """Blank out // and /* */ comments, preserving line numbering and length so
    reported line numbers still point at the real source. A rule name mentioned
    in a comment is not a violation."""
    out = list(src)
    i, n = 0, len(src)
    in_line = in_block = in_str = False
    quote = ""
    while i < n:
        c, nxt = src[i], src[i + 1] if i + 1 < n else ""
        if in_line:
            if c == "\n":
                in_line = False
            else:
                out[i] = " "
        elif in_block:
            if c == "*" and nxt == "/":
                out[i] = out[i + 1] = " "
                in_block = False
                i += 2
                continue
            if c != "\n":
                out[i] = " "
        elif in_str:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                in_str = False
        elif c == "/" and nxt == "/":
            in_line = True
            out[i] = " "
        elif c == "/" and nxt == "*":
            in_block = True
            out[i] = " "
        elif c in "\"'`":
            in_str, quote = True, c
        i += 1
    return "".join(out)


def check_tile_safety(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    raw_lines = raw.splitlines()
    findings = []

    def line_of(pos):
        return raw.count("\n", 0, pos) + 1

    clean = strip_comments(raw)

    for rule_id, pattern, message in RULES:
        for m in pattern.finditer(clean):
            ln = line_of(m.start())
            findings.append({
                "line": ln,
                "rule": rule_id,
                "message": message,
                "snippet": raw_lines[ln - 1].strip()[:100],
            })

    for m in IMPORT_RE.finditer(clean):
        ln = line_of(m.start())
        findings.append({
            "line": ln,
            "rule": "second-module",
            "message": f"imports a second local file ({m.group(1)}) -- 404s in tile. Keep app to 1 file.",
            "snippet": raw_lines[ln - 1].strip()[:100],
        })

    seen = {}
    for m in ID_RE.finditer(clean):
        seen.setdefault(m.group(1), []).append(line_of(m.start()))
    for elem_id, lines in seen.items():
        if len(lines) > 1:
            findings.append({
                "line": lines[1],
                "rule": "duplicate-id",
                "message": f'id="{elem_id}" used on multiple elements (lines {", ".join(map(str, lines))}).',
                "snippet": raw_lines[lines[1] - 1].strip()[:100],
            })

    return sorted(findings, key=lambda x: x["line"])


def check_composition(path: Path) -> list:
    raw = path.read_text(encoding="utf-8")
    clean = strip_comments(raw)
    warnings = []

    # 1. No <app-grid tag
    if not re.search(r"<app-grid\b", clean):
        warnings.append("No detail table (<app-grid>). The default composition includes one unless the user asked for a minimal layout.")

    # 2. Fewer than 3 <app-chart or <app-grid tags in total
    chart_grid_matches = re.findall(r"<(?:app-chart|app-grid)\b", clean)
    if len(chart_grid_matches) < 3:
        warnings.append("Fewer than 3 charts/grids found. The default composition includes a time trend, a breakdown chart, and a detail table.")

    # 3. Numeric max: literal inside yAxis options object on a chart inside a .map( template
    for m in re.finditer(r"\.map\s*\(", clean):
        chunk = clean[m.start():m.start() + 2000]
        if re.search(r"<app-chart\b", chunk) and re.search(r"yAxis\s*:\s*\{[^}]*?\bmax\s*:\s*\d+", chunk):
            warnings.append("Hardcoded yAxis max in .map() template. Use y-scale-group on <app-chart> instead of hardcoding max.")
            break

    if "cross-filter" in clean:
        m = re.search(r"(?<!this\.)getEffectiveFilters\s*\([^)]*\)\s*\{", clean)
        if m:
            brace_count = 1
            idx = m.end()
            body_chars = []
            while idx < len(clean) and brace_count > 0:
                ch = clean[idx]
                if ch == '{':
                    brace_count += 1
                elif ch == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                body_chars.append(ch)
                idx += 1
            body = "".join(body_chars)
            if "crossFilters" not in body and "super.getEffectiveFilters" not in body:
                warnings.append(
                    "cross-filter is set, but getEffectiveFilters() does not spread this.crossFilters, so clicks will not filter the other widgets. Add ...(this.crossFilters || {})."
                )

    return warnings


# ----------------------------------------------------------------------
# Stage 3: Looker Query Dry-Run (Pure Python)
# ----------------------------------------------------------------------

def load_looker_credentials() -> dict:
    merged_data = {}
    candidates = [
        Path.cwd() / "data-apps-config.json",
    ]
    curr = Path(__file__).resolve().parent
    while curr != curr.parent:
        candidates.append(curr / "data-apps-config.json")
        if (curr / ".git").exists():
            break
        curr = curr.parent

    for candidate in candidates:
        if candidate.is_file():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    merged_data.update(data)
                    break
            except Exception:
                pass

    base_url = (os.environ.get("LOOKERSDK_BASE_URL") or
                os.environ.get("LOOKER_BASE_URL") or
                merged_data.get("base_url") or
                merged_data.get("looker_instance_url"))
    client_id = (os.environ.get("LOOKERSDK_CLIENT_ID") or
                 os.environ.get("LOOKER_CLIENT_ID") or
                 merged_data.get("client_id"))
    client_secret = (os.environ.get("LOOKERSDK_CLIENT_SECRET") or
                     os.environ.get("LOOKER_CLIENT_SECRET") or
                     merged_data.get("client_secret"))
    if base_url and client_id and client_secret:
        return {
            "base_url": str(base_url).rstrip("/"),
            "client_id": str(client_id),
            "client_secret": str(client_secret),
        }
    return {}


def get_auth_token(creds: dict) -> str | None:
    body = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            f"{creds['base_url']}/api/4.0/login",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
        with urllib.request.urlopen(req, context=_LOOKER_SSL_CTX, timeout=12) as r:
            return json.loads(r.read().decode("utf-8")).get("access_token")
    except Exception:
        return None


def extract_queries_from_code(code: str) -> list[dict]:
    """Parse queries, models, and explores from an app.js file."""
    # Default model / explore on class
    default_model = None
    m_model = re.search(r"""(?:this\.lookerModel|lookerModel)\s*=\s*['"]([^'"]+)['"]""", code)
    if m_model:
        default_model = m_model.group(1)

    default_explore = None
    m_exp = re.search(r"""(?:this\.explore|explore)\s*=\s*['"]([^'"]+)['"]""", code)
    if m_exp:
        default_explore = m_exp.group(1)

    queries = []

    # 1. Look for any <app-*> widget with .query (supports self-closing or explicit closing tag)
    widget_re = re.compile(
        r"""<(app-[a-z0-9-]+)\b([^>]*?)(?:/>|>(.*?)</\1>)""",
        re.DOTALL | re.IGNORECASE,
    )
    for m in widget_re.finditer(code):
        tag = m.group(1)
        if tag.lower() == "app-kpi":
            continue
        attrs = m.group(2) or ""
        content = m.group(3) or ""
        combined = attrs + " " + content

        title = "Untitled"
        t_m = re.search(r"""title=['"]([^'"]+)['"]""", combined)
        if t_m:
            title = t_m.group(1)

        model = default_model
        mod_m = re.search(r"""looker-model=['"]([^'"]+)['"]""", combined)
        if mod_m:
            model = mod_m.group(1)
        mod_query_m = re.search(r"""\bmodel\s*:\s*['"]([^'"]+)['"]""", combined)
        if mod_query_m:
            model = mod_query_m.group(1)

        explore = default_explore
        exp_m = re.search(r"""explore=['"]([^'"]+)['"]""", combined)
        if exp_m:
            explore = exp_m.group(1)
        exp_query_m = re.search(r"""\b(?:view|explore)\s*:\s*['"]([^'"]+)['"]""", combined)
        if exp_query_m:
            explore = exp_query_m.group(1)

        # Extract fields array from .query=${{ ... fields: [...] ... }}
        fields = []
        fields_m = re.search(r"""fields:\s*\[([^\]]+)\]""", combined)
        if fields_m:
            raw_fields = fields_m.group(1)
            for f in re.findall(r"""['"]([^'"]+)['"]""", raw_fields):
                fields.append(f.strip())

        if fields:
            queries.append({
                "widget": tag,
                "title": title,
                "model": model,
                "explore": explore,
                "fields": fields,
            })

    # 2. Look for <app-kpi> (supports self-closing, query-field, and .query)
    kpi_re = re.compile(r"""<app-kpi\b([^>]*?)(?:/>|>(.*?)</app-kpi>)""", re.DOTALL | re.IGNORECASE)
    for m in kpi_re.finditer(code):
        combined = (m.group(1) or "") + " " + (m.group(2) or "")
        label = "KPI"
        l_m = re.search(r"""label=['"]([^'"]+)['"]""", combined)
        if l_m:
            label = l_m.group(1)

        model = default_model
        mod_m = re.search(r"""looker-model=['"]([^'"]+)['"]""", combined)
        if mod_m:
            model = mod_m.group(1)
        mod_query_m = re.search(r"""\bmodel\s*:\s*['"]([^'"]+)['"]""", combined)
        if mod_query_m:
            model = mod_query_m.group(1)

        explore = default_explore
        exp_m = re.search(r"""explore=['"]([^'"]+)['"]""", combined)
        if exp_m:
            explore = exp_m.group(1)
        exp_query_m = re.search(r"""\b(?:view|explore)\s*:\s*['"]([^'"]+)['"]""", combined)
        if exp_query_m:
            explore = exp_query_m.group(1)

        fields = []
        fields_m = re.search(r"""fields:\s*\[([^\]]+)\]""", combined)
        if fields_m:
            raw_fields = fields_m.group(1)
            for f in re.findall(r"""['"]([^'"]+)['"]""", raw_fields):
                fields.append(f.strip())
        qf_m = re.search(r"""query-field=['"]([^'"]+)['"]""", combined)
        if qf_m:
            qf = qf_m.group(1).strip()
            if qf not in fields:
                fields.append(qf)

        if fields:
            queries.append({
                "widget": "app-kpi",
                "title": label,
                "model": model,
                "explore": explore,
                "fields": fields,
            })

    return queries


def dry_run_query(creds: dict, token: str, query: dict) -> dict:
    """Execute a single query with limit 1 to verify SQL compilation & data return."""
    model = query.get("model")
    explore = query.get("explore")
    fields = query.get("fields", [])

    if not model:
        return {
            "ok": False,
            "error_type": "missing_model",
            "message": f"Widget '{query['title']}' has no LookML model defined.",
            "hint": "Specify looker-model on the widget or set this.lookerModel in constructor.",
        }
    if not explore:
        return {
            "ok": False,
            "error_type": "missing_explore",
            "message": f"Widget '{query['title']}' has no explore defined.",
            "hint": "Specify explore='...' on the widget or set this.explore in constructor.",
        }

    body = {
        "model": model,
        "view": explore,
        "fields": fields,
        "limit": "1",
    }
    url = f"{creds['base_url']}/api/4.0/queries/run/json"

    t0 = time.time()
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"token {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
        with urllib.request.urlopen(req, context=_LOOKER_SSL_CTX, timeout=15) as resp:
            raw_text = resp.read().decode("utf-8")
            rows = json.loads(raw_text) if raw_text else []
            elapsed = time.time() - t0
            return {
                "ok": True,
                "rows_count": len(rows),
                "elapsed": round(elapsed, 2),
                "is_empty": len(rows) == 0,
            }
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        clean_msg = raw
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and "message" in parsed:
                clean_msg = parsed["message"]
        except Exception:
            pass

        if "model not found" in clean_msg.lower():
            return {
                "ok": False,
                "error_type": "model_not_found",
                "message": f"Looker returned HTTP 400: Model '{model}' Not Found.",
                "hint": f"The model '{model}' does not exist on this Looker instance. Use check-credentials.py to view valid models.",
            }
        elif "could not find field" in clean_msg.lower() or "field not found" in clean_msg.lower() or e.code == 422:
            return {
                "ok": False,
                "error_type": "field_not_found",
                "message": f"Looker returned HTTP {e.code}: {clean_msg}",
                "hint": f"One or more fields {fields} do not exist on explore '{explore}'. Check explore-model.py {model} {explore}.",
            }
        return {
            "ok": False,
            "error_type": "looker_api_error",
            "message": f"Looker returned HTTP {e.code}: {clean_msg}",
            "hint": "Check query fields, explore, and model configuration.",
        }
    except Exception as e:
        return {
            "ok": False,
            "error_type": "network_error",
            "message": f"Failed to execute test query: {e}",
            "hint": "Check network connection or Looker server reachability.",
        }


# ----------------------------------------------------------------------
# Stage 4: Headless Browser Visual Inspection & Screenshot
# ----------------------------------------------------------------------

def check_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Test TCP connectivity to a host and port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, TimeoutError):
        return False


def find_system_browser() -> str | None:
    """Find system Chromium-based browser for headless verification."""
    mac_candidates = [
        ("chrome_mac", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ("edge_mac", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ("brave_mac", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
    ]
    for b_type, path in mac_candidates:
        if os.path.exists(path):
            return b_type

    for b_type, binary in [
        ("google_chrome", "google-chrome"),
        ("chromium", "chromium"),
        ("chromium_browser", "chromium-browser"),
        ("microsoft_edge", "microsoft-edge"),
    ]:
        if shutil.which(binary):
            return b_type

    return None


SCREENSHOT_WIDTH = 1440
FOLD_HEIGHT = 900
MAX_SCREENSHOT_HEIGHT = 8000


def parse_content_height(dom: str):
    """Rendered page height that preview-host.js writes on #preview-diagnostics, or None."""
    m = re.search(
        r'id=["\']preview-diagnostics["\'][^>]*data-content-height=["\'](\d+)["\']|data-content-height=["\'](\d+)["\'][^>]*id=["\']preview-diagnostics["\']',
        dom,
    )
    if not m:
        return None
    return int(m.group(1) or m.group(2))


def parse_sandbox_state(dom: str):
    """Extract sandbox mount status and pending query count from #preview-diagnostics, or None."""
    tag_m = re.search(r'<[^>]*\bid=["\']preview-diagnostics["\'][^>]*>', dom)
    if not tag_m:
        return None
    tag_str = tag_m.group(0)
    mounted_m = re.search(r'\bdata-sandbox-mounted=["\']([^"\']*)["\']', tag_str)
    if not mounted_m:
        return None
    mounted = mounted_m.group(1) == "1"
    pending_m = re.search(r'\bdata-sandbox-pending=["\']([^"\']*)["\']', tag_str)
    try:
        pending = int(pending_m.group(1)) if pending_m else 0
    except ValueError:
        pending = 0
    return {"mounted": mounted, "pending": pending}


def run_headless_browser(browser_type: str, preview_url: str, screenshot_path: str, height: int = FOLD_HEIGHT) -> dict:
    """Run browser headless to capture DOM and screenshot."""
    # Static dispatch on browser_type to satisfy static analysis checks
    base_args = [
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        # Chrome runs the sandboxed preview iframe in its own process, and
        # --virtual-time-budget only waits for the top page. Without this flag the
        # sandbox pass is captured about 2s in, before its widgets load. The iframe
        # keeps its sandbox; only the process placement changes.
        "--disable-features=IsolateSandboxedIframes",
        f"--screenshot={screenshot_path}",
        f"--window-size={SCREENSHOT_WIDTH},{height}",
        "--virtual-time-budget=6000",
        "--dump-dom",
        preview_url,
    ]

    try:
        if browser_type == "chrome_mac":
            res = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        elif browser_type == "edge_mac":
            res = subprocess.run(
                ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        elif browser_type == "brave_mac":
            res = subprocess.run(
                ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        elif browser_type == "google_chrome":
            res = subprocess.run(
                ["google-chrome", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        elif browser_type == "chromium":
            res = subprocess.run(
                ["chromium", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        elif browser_type == "chromium_browser":
            res = subprocess.run(
                ["chromium-browser", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        elif browser_type == "microsoft_edge":
            res = subprocess.run(
                ["microsoft-edge", *base_args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        else:
            return {"ok": False, "skipped": True, "reason": "Unknown browser type."}
        dom = res.stdout or ""

        visual_errors = []
        # Check for #preview-diagnostics with data-error-count
        diag_count_match = re.search(
            r'id=["\']preview-diagnostics["\'][^>]*data-error-count=["\'](\d+)["\']|data-error-count=["\'](\d+)["\'][^>]*id=["\']preview-diagnostics["\']',
            dom,
        )
        if diag_count_match:
            count_str = diag_count_match.group(1) or diag_count_match.group(2)
            err_count = int(count_str) if count_str else 0
            if err_count > 0:
                diag_elem = re.search(r'<[^>]*id=["\']preview-diagnostics["\'][^>]*>(.*?)</', dom, re.DOTALL)
                payload = diag_elem.group(1).strip() if diag_elem else ""
                visual_errors.append({
                    "type": "runtime_error",
                    "message": f"Preview diagnostics recorded {err_count} runtime error(s): {payload[:300]}",
                    "hint": "Check preview server diagnostics and browser console.",
                })

        # Check for #sandbox-error-box
        if 'id="sandbox-error-box"' in dom and not any(e["type"] == "runtime_error" for e in visual_errors):
            m_sbx = re.search(r'<span class="sandbox-err-msg">([^<]+)</span>', dom)
            sbx_msg = m_sbx.group(1).strip() if m_sbx else "Sandbox error detected."
            visual_errors.append({
                "type": "sandbox_error",
                "message": f"Sandbox Error: {sbx_msg}",
                "hint": "The app threw an error or failed to load inside the tile sandbox iframe.",
            })

        # Check for .preview-load-error
        if '<div class="preview-load-error"' in dom or re.search(r"""<div[^>]*class=["'][^"']*preview-load-error""", dom):
            m_load = re.search(r"""<div class="preview-load-error"[^>]*>.*?<pre>([^<]*)</pre>""", dom, re.DOTALL)
            load_err = m_load.group(1).strip() if m_load else "Error loading Data App module."
            visual_errors.append({
                "type": "load_error",
                "message": f"Preview Load Error: {load_err}",
                "hint": "The data app module failed to load in the preview host.",
            })

        # Check for .da-error-card
        if "da-error-card" in dom:
            m = re.search(r"""<div class="da-error-message">([^<]+)</div>""", dom)
            msg = m.group(1) if m else "Error card detected in rendered DOM."
            visual_errors.append({
                "type": "error_card",
                "message": f"Rendered Error Card: {msg.strip()}",
                "hint": "A widget encountered an error during render or query.",
            })

        # Check for <app-kpi> error card
        if re.search(r'class=["\'][^"\']*\bda-kpi-wrap\s+error\b', dom) or re.search(r'class=["\'][^"\']*\bkpi-value\s+error\b', dom):
            m_kpi = re.search(r'<div[^>]*class=["\'][^"\']*\bda-kpi-wrap\s+error\b[^"\']*["\'][^>]*title="([^"]+)"', dom)
            if not m_kpi:
                m_kpi = re.search(r"<div[^>]*class=[\"'][^\"']*\bda-kpi-wrap\s+error\b[^\"']*[\"'][^>]*title='([^']+)'", dom)
            if not m_kpi:
                m_kpi = re.search(r"""<div[^>]*class=["'][^"']*\bkpi-value\s+error\b[^"']*["'][^>]*>([^<]+)</div>""", dom)
            kpi_msg = html.unescape(m_kpi.group(1)).strip() if m_kpi else "KPI widget query or render error."
            visual_errors.append({
                "type": "error_card",
                "message": f"Rendered KPI Error: {kpi_msg}",
                "hint": "An <app-kpi> encountered an error during render or query.",
            })

        # Check for .da-loading-skeleton
        if "da-loading-skeleton" in dom:
            visual_errors.append({
                "type": "stuck_loading",
                "message": "Widget is stuck in shimmer loading skeleton after 6 seconds.",
                "hint": "Check for Cartesian fan-out, hanging queries, or unhandled JS promise rejections.",
            })

        state = parse_sandbox_state(dom)
        if state is not None and not any(e["type"] in ("runtime_error", "sandbox_error", "load_error") for e in visual_errors):
            hint = "Check for slow or hanging queries. If the inspect pass renders, the app may be waiting on something the tile sandbox blocks."
            if not state["mounted"]:
                visual_errors.append({
                    "type": "stuck_loading",
                    "message": "The app had not mounted in the sandbox when the screenshot was taken.",
                    "hint": hint,
                })
            elif state["pending"] > 0:
                n = state["pending"]
                msg = f"{n} query was still running in the sandbox when the screenshot was taken." if n == 1 else f"{n} queries were still running in the sandbox when the screenshot was taken."
                visual_errors.append({
                    "type": "stuck_loading",
                    "message": msg,
                    "hint": hint,
                })

        screenshot_created = os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0
        return {
            "ok": len(visual_errors) == 0,
            "visual_errors": visual_errors,
            "screenshot": screenshot_path if screenshot_created else None,
            "content_height": parse_content_height(dom),
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "Headless browser timed out after 20 seconds.",
            "timed_out": True,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ----------------------------------------------------------------------
# Main Runner
# ----------------------------------------------------------------------

def verify_app(app_path: str, run_browser: bool = True, port: int = 8765) -> dict:
    p = Path(app_path).resolve()
    if not p.exists():
        return {
            "ok": False,
            "error": f"File not found: {app_path}",
        }

    results = {
        "app": str(p),
        "syntax": {},
        "safety": [],
        "warnings": [],
        "queries": [],
        "visual": {},
        "passed": False,
    }

    # 1. Syntax Check
    results["syntax"] = check_syntax(p)
    if not results["syntax"]["ok"]:
        return results

    # 2. Tile Safety Check & Composition Warnings
    results["safety"] = check_tile_safety(p)
    results["warnings"] = check_composition(p)
    if results["safety"]:
        return results

    # 3. Query Dry-Run
    creds = load_looker_credentials()
    if creds:
        token = get_auth_token(creds)
        if token:
            queries = extract_queries_from_code(p.read_text(encoding="utf-8"))
            for q in queries:
                q_res = dry_run_query(creds, token, q)
                results["queries"].append({"query": q, "result": q_res})

    query_failures = [q for q in results["queries"] if not q["result"]["ok"]]
    if query_failures:
        return results

    # 4. Headless Visual Check & Screenshot
    if run_browser:
        if not check_port_open("127.0.0.1", port):
            results["visual"] = {
                "skipped": True,
                "reason": f"Preview server is not running on port {port}; offline QA passed.",
            }
        else:
            b_type = find_system_browser()
            if b_type:
                inspect_url = f"http://localhost:{port}/preview-server/?app={app_path}&inspect=1"
                inspect_shot = str(p.parent / "preview.png")
                inspect_res = run_headless_browser(b_type, inspect_url, inspect_shot)

                # The first pass only sees the fold. When the app is taller,
                # re-shoot at full height so the screenshot shows the whole app.
                shot_h = FOLD_HEIGHT
                content_h = inspect_res.get("content_height")
                if not inspect_res.get("error") and content_h and content_h > FOLD_HEIGHT:
                    shot_h = min(content_h + 40, MAX_SCREENSHOT_HEIGHT)
                    inspect_res = run_headless_browser(b_type, inspect_url, inspect_shot, height=shot_h)

                if inspect_res.get("error"):
                    sandbox_res = {"ok": False, "visual_errors": [], "screenshot": None}
                else:
                    sandbox_url = f"http://localhost:{port}/preview-server/?app={app_path}"
                    sandbox_shot = str(p.parent / "preview-sandbox.png")
                    sandbox_res = run_headless_browser(b_type, sandbox_url, sandbox_shot, height=shot_h)

                all_visual_errors = []
                for ve in inspect_res.get("visual_errors", []):
                    ve_copy = dict(ve)
                    ve_copy["message"] = f"[inspect] {ve_copy['message']}"
                    all_visual_errors.append(ve_copy)
                for ve in sandbox_res.get("visual_errors", []):
                    ve_copy = dict(ve)
                    ve_copy["message"] = f"[sandbox] {ve_copy['message']}"
                    all_visual_errors.append(ve_copy)

                exec_error = inspect_res.get("error") or sandbox_res.get("error")
                results["visual"] = {
                    "ok": len(all_visual_errors) == 0 and not exec_error,
                    "visual_errors": all_visual_errors,
                    "screenshot": inspect_res.get("screenshot") or sandbox_res.get("screenshot"),
                    "screenshots": {
                        "inspect": inspect_res.get("screenshot"),
                        "sandbox": sandbox_res.get("screenshot"),
                    },
                    "error": exec_error,
                    "timed_out": bool(inspect_res.get("timed_out") or sandbox_res.get("timed_out")),
                }
            else:
                results["visual"] = {"skipped": True, "reason": "No Chromium browser found."}

    visual_failures = results["visual"].get("visual_errors", [])
    visual_ok = results["visual"].get("ok", False) or results["visual"].get("skipped", False) or not run_browser
    results["passed"] = (
        results["syntax"]["ok"]
        and len(results["safety"]) == 0
        and len(query_failures) == 0
        and visual_ok
        and len(visual_failures) == 0
    )
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Post-creation QA & Verification for Data Apps.")
    parser.add_argument("app", help="Path to app.js (e.g. apps/sales/app.js)")
    parser.add_argument("--no-browser", action="store_true", help="Skip headless browser inspection")
    parser.add_argument("--port", type=int, default=8765, help="Preview server port (default 8765)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args(argv)

    res = verify_app(args.app, run_browser=not args.no_browser, port=args.port)

    if args.json:
        print(json.dumps(res, indent=2))
        return 0 if res.get("passed") else 1

    print("\n" + "=" * 64)
    print(f"DATA APP QA VERIFICATION: {args.app}")
    print("=" * 64)

    # 1. Syntax
    syn = res.get("syntax", {})
    if not syn.get("ok"):
        print("\n✗ STAGE 1 FAILED: JavaScript Syntax Error")
        print(f"  Line:    {syn.get('line')}")
        print(f"  Error:   {syn.get('error')}")
        if syn.get("snippet"):
            print(f"  Snippet: {syn['snippet']}")
        if syn.get("hint"):
            print(f"  Hint:    {syn['hint']}")
        print("\nAgent action: Fix the syntax error in app.js and re-run verify-app.py.\n")
        return 1
    print(f"✓ Stage 1: JavaScript syntax valid ({syn.get('engine', 'clean')})")

    # 2. Tile Safety
    safety = res.get("safety", [])
    if safety:
        print(f"\n✗ STAGE 2 FAILED: {len(safety)} Tile Sandbox Violation(s)")
        for s in safety:
            print(f"  Line {s['line']} [{s['rule']}]: {s['message']}")
            print(f"    > {s['snippet']}")
        print("\nAgent action: Remove sandbox violations in app.js and re-run verify-app.py.\n")
        return 1
    print("✓ Stage 2: Tile safety sandbox rules clean")
    for w in res.get("warnings", []):
        print(f"  ⚠ Warning: {w}")

    # 3. Query Dry-Run
    queries = res.get("queries", [])
    query_fails = [q for q in queries if not q["result"].get("ok")]
    query_warns = [q for q in queries if q["result"].get("ok") and q["result"].get("is_empty")]

    if query_fails:
        print(f"\n✗ STAGE 3 FAILED: {len(query_fails)} Looker Query Error(s)")
        for f in query_fails:
            q = f["query"]
            r = f["result"]
            print(f"  Widget '{q['title']}' ({q['widget']}):")
            print(f"    Error: {r['message']}")
            print(f"    Hint:  {r['hint']}")
        print("\nAgent action: Fix model, explore, or field names in app.js and re-run verify-app.py.\n")
        return 1

    if queries:
        print(f"✓ Stage 3: {len(queries)} query dry-run(s) executed successfully")
        for w in query_warns:
            q = w["query"]
            print(f"  ⚠ Warning: Widget '{q['title']}' query returned 0 rows (chart may appear empty).")
    else:
        print("✓ Stage 3: Query dry-run passed (no queries or offline mode)")

    # 4. Visual Inspection
    visual = res.get("visual", {})
    if visual.get("skipped"):
        print(f"ℹ Stage 4: Visual inspection skipped ({visual.get('reason')})")
    elif visual.get("visual_errors"):
        print(f"\n✗ STAGE 4 FAILED: Visual DOM Error(s)")
        for ve in visual["visual_errors"]:
            print(f"  Type:    {ve['type']}")
            print(f"  Message: {ve['message']}")
            print(f"  Hint:    {ve['hint']}")
        print("\nAgent action: Resolve visual errors in app.js and re-run verify-app.py.\n")
        return 1
    elif visual.get("error"):
        print(f"\n✗ STAGE 4 FAILED: Browser Inspection Error")
        print(f"  Error: {visual.get('error')}")
        if "timed out" in str(visual.get("error", "")).lower() or visual.get("timed_out"):
            print("\nAgent action: Headless browser timed out. Do not debug the browser or modify app.js. Re-run with --no-browser to complete offline verification.\n")
        else:
            print("\nAgent action: Ensure preview server is accessible or run with --no-browser.\n")
        return 1
    elif visual.get("ok"):
        print("✓ Stage 4: Headless visual inspection clean (no error cards or stuck skeletons)")
        if visual.get("screenshot"):
            print(f"  Screenshot saved: {visual['screenshot']}")

    print("\n✓ ALL QA CHECKS PASSED. Application is verified and ready for preview.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

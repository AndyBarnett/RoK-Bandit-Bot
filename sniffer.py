import json
import os
import sys
from mitmproxy import http, ctx


SESSION_FILE = "session.json"

captured = {
    "auth_token": None,
    "client_version": None
}


# =========================
# STARTUP DIAGNOSTICS
# =========================

def load(loader):
    print("[SNIFFER] LOADED SUCCESSFULLY", flush=True)
    print("[SNIFFER] Python executable:", sys.executable, flush=True)
    print("[SNIFFER] Working directory:", os.getcwd(), flush=True)
    print("[SNIFFER] Script path:", os.path.abspath(__file__), flush=True)


def request(flow: http.HTTPFlow):
    url = flow.request.url

    # prove interception is working at all
    if "riseofcultures" in url:
        print("[SNIFFER] TRAFFIC:", url, flush=True)

    if "/game/startup" not in url:
        return

    print("[SNIFFER] /game/startup DETECTED", flush=True)

    headers = flow.request.headers

    auth = headers.get("X-Auth-Token")
    version = headers.get("X-ClientVersion")

    print("[SNIFFER] HEADERS:", dict(headers), flush=True)

    if auth:
        print("[SNIFFER] AUTH TOKEN FOUND", flush=True)
        captured["auth_token"] = auth

    if version:
        print("[SNIFFER] CLIENT VERSION FOUND", flush=True)
        captured["client_version"] = version

    if captured["auth_token"] and captured["client_version"]:
        write_and_exit()


# =========================
# SESSION OUTPUT
# =========================

def write_and_exit():
    print("[SNIFFER] Writing session.json", flush=True)

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(captured, f, indent=2)

    print("[SNIFFER] session.json written", flush=True)

    ctx.master.shutdown()
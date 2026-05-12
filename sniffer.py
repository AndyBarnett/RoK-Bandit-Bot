import json
from mitmproxy import http, ctx


SESSION_FILE = "session.json"

captured = {
    "auth_token": None,
    "client_version": None
}


def request(flow: http.HTTPFlow):
    url = flow.request.url

    if "/game/startup" not in url:
        return

    headers = flow.request.headers

    auth = headers.get("X-Auth-Token")
    version = headers.get("X-ClientVersion")

    if auth:
        captured["auth_token"] = auth

    if version:
        captured["client_version"] = version

    if captured["auth_token"] and captured["client_version"]:
        write_and_exit()


def write_and_exit():
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(captured, f, indent=2)

    ctx.master.shutdown()
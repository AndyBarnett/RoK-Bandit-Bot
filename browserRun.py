import json
import os
import sys
import time

from playwright.sync_api import sync_playwright


SESSION_FILE = "session.json"


class GameBrowser:
    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self, email: str, password: str):
        self.delete_session_file()

        self.pw = sync_playwright().start()

        self.browser = self.pw.chromium.launch(
            headless=True,
            proxy={"server": "http://127.0.0.1:8080"},
            args=[
                "--ignore-certificate-errors",
                "--disable-quic"
            ]
        )

        self.context = self.browser.new_context(ignore_https_errors=True)
        self.page = self.context.new_page()

        self.page.goto(
            "https://am0.riseofcultures.com",
            wait_until="domcontentloaded"
        )

        self.dismiss_cookie_banner()
        self.login(email, password)

        self.wait_for_session_file()

    def dismiss_cookie_banner(self):
        try:
            self.page.click("#pop-up_cookie_button_accept", timeout=5000)
        except Exception:
            pass

    def login(self, email: str, password: str):
        self.page.fill(
            "#page_login_always-visible_input_player-identifier",
            email
        )

        self.page.fill(
            "#page_login_always-visible_input_password",
            password
        )

        self.page.click("#page_login_always-visible_button_login")

        self.page.wait_for_timeout(20000)

    def delete_session_file(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    def wait_for_session_file(self):
        while True:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if data.get("auth_token") and data.get("client_version"):
                    self.close()
                    return

            time.sleep(1)

    def close(self):
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    browser = GameBrowser()
    browser.start(sys.argv[1], sys.argv[2])
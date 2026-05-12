import sys
import os
from playwright.sync_api import sync_playwright


SESSION_FILE = "session.json"


class GameBrowser:
    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

    # =========================
    # START
    # =========================

    def start(self, email: str, password: str):
        self.delete_session_file()

        self.pw = sync_playwright().start()

        self.browser = self.pw.chromium.launch(
            headless=False,
            proxy={
                "server": "http://127.0.0.1:8080"
            },
            args=[
                "--ignore-certificate-errors",
                "--disable-quic"
            ]
        )

        self.context = self.browser.new_context(
            ignore_https_errors=True
        )

        self.page = self.context.new_page()

        print("[INFO] Opening game")

        self.page.goto(
            "https://am0.riseofcultures.com",
            wait_until="domcontentloaded"
        )

        self.dismiss_cookie_banner()
        self.login(email, password)

        print("[INFO] Login submitted, browser exiting")

        self.close()

    # =========================
    # LOGIN FLOW
    # =========================

    def dismiss_cookie_banner(self):
        try:
            self.page.click(
                "#pop-up_cookie_button_accept",
                timeout=5000
            )
            print("[INFO] Cookie banner dismissed")
        except Exception:
            print("[INFO] No cookie banner found")

    def login(self, email: str, password: str):
        print("[LOGIN] Filling credentials")

        self.page.fill(
            "#page_login_always-visible_input_player-identifier",
            email
        )

        self.page.fill(
            "#page_login_always-visible_input_password",
            password
        )

        self.page.click(
            "#page_login_always-visible_button_login"
        )

        print("[LOGIN] Submitted")

    # =========================
    # CLEANUP
    # =========================

    def delete_session_file(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            print(f"[INFO] Deleted existing {SESSION_FILE}")

    def close(self):
        if self.browser:
            self.browser.close()

        if self.pw:
            self.pw.stop()


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python browserRun.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    browser = GameBrowser()
    browser.start(email, password)
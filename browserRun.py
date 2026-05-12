import sys
import time
from playwright.sync_api import sync_playwright


class GameBrowser:
    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

        # captured values
        self.auth_token = None
        self.client_version = None

    # =========================
    # LIFECYCLE
    # =========================

    def start(self, email: str, password: str):
        self.pw = sync_playwright().start()

        self.browser = self.pw.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        self.attach_network_logging()

        self.open_login_page()
        self.dismiss_cookies()
        self.login(email, password)

        print("[INFO] Login submitted")

    def close(self):
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()

    # =========================
    # NAVIGATION
    # =========================

    def open_login_page(self):
        self.page.goto("https://am0.riseofcultures.com", wait_until="domcontentloaded")

    # =========================
    # COOKIE BANNER
    # =========================

    def dismiss_cookies(self):
        try:
            self.page.click(
                "#pop-up_cookie_button_accept",
                timeout=5000
            )
            print("[INFO] Cookie banner dismissed")
        except Exception:
            print("[INFO] Cookie banner not present")


    # =========================
    # LOGIN FLOW
    # =========================

    def login(self, email: str, password: str):
        self.page.fill("#page_login_always-visible_input_player-identifier", email)
        self.page.fill("#page_login_always-visible_input_password", password)
        self.page.click("#page_login_always-visible_button_login")

    # =========================
    # NETWORK MONITORING
    # =========================

    def attach_network_logging(self):
        self.page.on("request", self._on_request)

    def _on_request(self, request):
        url = request.url

        if "/game/startup" in url and "am2.riseofcultures.com" in url:
            headers = request.all_headers()

            self.auth_token = headers.get("x-auth-token")
            self.client_version = headers.get("x-clientversion")

            print("\n[GAME STARTUP REQUEST CAPTURED]")

            print("URL:", url)
            print("X-AUTH-TOKEN:", self.auth_token)
            print("X-ClientVersion:", self.client_version)

    # =========================
    # DEBUG HELPERS
    # =========================

    def print_captured(self):
        print("\n--- CAPTURED VALUES ---")
        print("Auth Token:", self.auth_token)
        print("Client Version:", self.client_version)


# =========================================================
# RUN SCRIPT
# =========================================================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    browser = GameBrowser()

    try:
        browser.start(email, password)

        print("[INFO] Running... watching network")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        browser.print_captured()
        browser.close()

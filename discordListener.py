import json
import subprocess
import sys
import discord
from discord.ext import commands
import time
import os
import shutil
import socket

SESSION_FILE = "session.json"

# =========================
# BOOTSTRAP
# =========================

if len(sys.argv) < 2:
    print("Usage: python discordListener.py <DISCORD_BOT_TOKEN>")
    sys.exit(1)

TOKEN = sys.argv[1]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# SESSION HELPERS
# =========================

def wait_for_session_file(timeout=60):
    start = time.time()

    while True:
        if time.time() - start > timeout:
            raise Exception("Timed out waiting for session.json")

        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("auth_token") and data.get("client_version"):
                return data

        except Exception:
            pass

        time.sleep(1)


# =========================
# MITM STARTUP
# =========================

    print("[INFO] Starting mitmdump", flush=True)

    mitmdump_path = shutil.which("mitmdump")

    if not mitmdump_path:
        raise Exception("mitmdump not found in PATH")

    process = subprocess.Popen(
        [
            mitmdump_path,
            "-p",
            "8080",
            "-s",
            os.path.abspath("sniffer.py")
        ],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("[INFO] mitmdump launched", flush=True)

    return process
def start_sniffer():
    print("[INFO] Starting mitmdump", flush=True)

    mitmdump_path = shutil.which("mitmdump")

    if not mitmdump_path:
        raise Exception("mitmdump not found in PATH")

    sniffer_path = os.path.abspath("sniffer.py")

    process = subprocess.Popen(
        [
            mitmdump_path,
            "-p",
            "8080",
            "-s",
            sniffer_path
        ],
        cwd=os.path.dirname(sniffer_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("[INFO] mitmdump launched", flush=True)
    return process

# =========================
# DISCORD COMMAND
# =========================
# !bandit <region> <email> <password>
# =========================

@bot.command()
async def bandit(ctx, region, email, password):
    print(f"[bandit] {ctx.author} -> {ctx.message.content}", flush=True)

    await ctx.send("```Starting automation flow...```")

    sniffer = None

    try:
        # -------------------------
        # 1. Start MITM proxy
        # -------------------------
        sniffer = start_sniffer()

        # -------------------------
        # 2. Run browser automation
        # -------------------------
        await ctx.send("```Launching browser...```")

        result = subprocess.run(
            ["python", "browserRun.py", email, password],
            capture_output=True,
            text=True
        )

        print(result.stdout, flush=True)
        print(result.stderr, flush=True)

        if result.returncode != 0:
            raise Exception("browserRun.py failed")

        # -------------------------
        # 3. Wait for session
        # -------------------------
        await ctx.send("```Waiting for session capture...```")

        session = wait_for_session_file()

        auth_token = session["auth_token"]
        client_version = session["client_version"]

        print("[SESSION] Captured", flush=True)
        print("Auth:", auth_token, flush=True)
        print("Client:", client_version, flush=True)

        await ctx.send("```Session captured```")

        # -------------------------
        # 4. Run game exe
        # -------------------------
        await ctx.send("```Running request...```")

        result = subprocess.run(
            [
                "poll_bandits.exe",
                region,
                auth_token,
                client_version
            ],
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr

        if not output:
            output = "(no output)"

        await ctx.send(f"```{output[:1900]}```")

    except Exception as e:
        await ctx.send(f"```ERROR:\n{str(e)}```")

    finally:
        if sniffer:
            try:
                sniffer.kill()
                print("[INFO] mitmdump stopped", flush=True)
            except Exception:
                pass


# =========================
# START BOT
# =========================

bot.run(TOKEN)
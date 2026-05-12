import sys
import os
import subprocess
import discord
from discord.ext import commands
from session_utils import load_session


if len(sys.argv) < 2:
    print("Usage: python discordListener.py <DISCORD_BOT_TOKEN>")
    sys.exit(1)

TOKEN = sys.argv[1]

SNIFFER_FILE = "sniffer.py"
BROWSER_FILE = "browserRun.py"


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def start_sniffer():
    sniffer_path = os.path.abspath(SNIFFER_FILE)

    return subprocess.Popen(
        [
            "mitmdump",
            "-p", "8080",
            "-s", sniffer_path
        ]
    )


def start_browser(email, password):
    browser_path = os.path.abspath(BROWSER_FILE)

    return subprocess.Popen(
        [
            "python",
            browser_path,
            email,
            password
        ]
    )


@bot.command()
async def bandit(ctx, region, email, password):
    await ctx.send("```Logging in with browser and getting auth token...```")
    try:
        sniffer_proc = start_sniffer()
        browser_proc = start_browser(email, password)

        browser_proc.wait()

        # wait for session file (hard gate)
        for _ in range(30):
            if os.path.exists("session.json"):
                break
            time.sleep(1)
        else:
            await ctx.send("```ERROR: session.json not found```")
            return

        session = load_session()

        auth_token = session.get("auth_token")
        client_version = session.get("client_version")

        if not auth_token or not client_version:
            await ctx.send("```ERROR: invalid session data```")
            return

        await ctx.send("```Running special exe with the info provided and found...```")

        result = subprocess.run(
            [
                "poll_bandits.exe",
                region,
                auth_token,
                client_version
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = (result.stdout or "") + (result.stderr or "")

        if not output.strip():
            output = "(no output)"

        await ctx.send(f"```{output[:1900]}```")

    except subprocess.TimeoutExpired:
        await ctx.send("```ERROR: poll_bandits.exe timed out```")

    except Exception as e:
        await ctx.send(f"```ERROR:\n{repr(e)}```")

    finally:
        try:
            sniffer_proc.terminate()
        except:
            pass


bot.run(TOKEN)
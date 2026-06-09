import sys
import os
import time
import subprocess
import discord
from discord.ext import commands
from session_utils import load_session
import re
import asyncio


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
            sys.executable,
            browser_path,
            email,
            password
        ]
    )


def clean_output(text):
    lines = []
    in_upcoming = False

    for line in text.splitlines():
        stripped = line.strip()

        # remove unwanted process noise
        if stripped.startswith("Process with ID") and "not found" in stripped:
            continue

        # track section
        if stripped.startswith("### Upcoming"):
            in_upcoming = True

        if stripped.startswith("### Previous"):
            in_upcoming = False

        # remove "Not Spawned" only in upcoming section
        if in_upcoming:
            line = line.replace("Not Spawned", "")
            line = re.sub(r"\s{2,}", " ", line).rstrip()

        lines.append(line)

    cleaned = "\n".join(lines)

    # restore newline after Upcoming header
    cleaned = re.sub(
        r"(### Upcoming)\s*",
        r"\1\n",
        cleaned
    )

    return cleaned


def add_relative_times(text):
    updated_lines = []
    in_upcoming = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("### Upcoming"):
            in_upcoming = True
            updated_lines.append(line)
            continue

        if stripped.startswith("### Previous"):
            in_upcoming = False
            updated_lines.append(line)
            continue

        if in_upcoming:
            match = re.search(r"<t:(\d+):F>", line)

            if match:
                ts = match.group(1)

                line = line.replace(
                    f"<t:{ts}:F>",
                    f"<t:{ts}:F> <t:{ts}:R>",
                    1
                )

        updated_lines.append(line)

    return "\n".join(updated_lines)


@bot.command()
async def bandit(ctx, region, email, password):

    print(
        f"[COMMAND] "
        f"guild={ctx.guild.name if ctx.guild else 'DM'} "
        f"user={ctx.author} "
        f"region={region} "
        f"email={email}"
    )

    await ctx.send("```Logging in with browser and getting auth token...```")

    sniffer_proc = None
    browser_proc = None

    try:
        # remove stale session file
        if os.path.exists("session.json"):
            os.remove("session.json")

        sniffer_proc = start_sniffer()
        browser_proc = start_browser(email, password)

        await asyncio.wait_for(
            asyncio.to_thread(browser_proc.wait),
            timeout=360
        )

        # wait for session file
        for _ in range(30):
            if os.path.exists("session.json"):
                break
            await asyncio.sleep(1)
        else:
            await ctx.send("```ERROR: session.json not found```")
            return

        session = load_session()

        auth_token = session.get("auth_token")
        client_version = session.get("client_version")

        if not auth_token or not client_version:
            await ctx.send("```ERROR: invalid session data```")
            return

        print(
            f"[SESSION] "
            f"auth_token_found={bool(auth_token)} "
            f"client_version={client_version}"
        )

        await ctx.send(
            "```Running special exe with the info provided and found...```"
        )

        result = await asyncio.to_thread(
            subprocess.run,
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

        output = clean_output(output)
        output = add_relative_times(output)

        if not output.strip():
            output = "(no output)"

        # split at LAST occurrence of "### Upcoming"
        parts = output.rsplit("### Upcoming", 1)

        if len(parts) == 2:
            first_part = parts[0].strip()
            second_part = "### Upcoming\n" + parts[1].strip()
        else:
            first_part = output
            second_part = ""

        first_part = first_part[:1900]
        second_part = second_part[:1900]
        second_part = second_part[:1900]

        # send first half
        if first_part:
            await ctx.send(first_part)

        # send second half
        if second_part:
            await ctx.send(second_part)

    except asyncio.TimeoutError:
        await ctx.send("```ERROR: browser login timed out```")

    except subprocess.TimeoutExpired:
        await ctx.send("```ERROR: poll_bandits.exe timed out```")

    except Exception as e:
        await ctx.send(f"```ERROR:\n{repr(e)}```")

    finally:
        try:
            if sniffer_proc:
                sniffer_proc.terminate()
        except:
            pass

        try:
            if browser_proc:
                browser_proc.terminate()
        except:
            pass


bot.run(TOKEN)
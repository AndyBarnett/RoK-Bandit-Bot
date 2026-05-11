import sys
import subprocess
import discord
from discord.ext import commands

if len(sys.argv) < 2:
    print("Usage: python run.py <DISCORD_BOT_TOKEN>")
    sys.exit(1)

TOKEN = sys.argv[1]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def bandit(ctx, arg1, arg2):
	print(f"[bandit] Requested by {ctx.author}", flush=True)
	print(f"Guild: {ctx.guild}", flush=True)
	print(f"Message: {ctx.message.content}", flush=True)
	
    result = subprocess.run(
        [
			"poll_bandits.exe",
			arg1,
			arg2,
			"1.136.5"],
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr

    if not output:
        output = "(no output)"

    await ctx.send(f"```{output[:1900]}```")

bot.run(TOKEN)
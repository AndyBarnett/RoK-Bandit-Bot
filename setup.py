import subprocess
import sys
import os

def run(cmd):
    print(f"\n→ Running: {' '.join(cmd)}\n")
    subprocess.check_call(cmd)

def main():
    # 1. Install dependencies
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. Install Playwright browser binaries
    run(["playwright", "install", "chromium"])

    # 3. Optional: verify install
    try:
        import discord
        print("discord.py OK")
    except Exception as e:
        print("discord.py import failed:", e)

    print("\nSetup complete.")

if __name__ == "__main__":
    main()
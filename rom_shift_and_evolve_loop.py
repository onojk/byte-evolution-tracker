#!/usr/bin/env python3
import os
import time
import shutil
from datetime import datetime
from rom_delta_logger import compute_delta_log_and_sum
from evolve_try_script_autoweight import evolve_try_script

EVOLVED_DIR = os.path.expanduser("~/evolved_roms")
ITERATIONS = 50
SLEEP_SECONDS = 5

def get_sorted_roms():
    roms = sorted([
        os.path.join(EVOLVED_DIR, f) for f in os.listdir(EVOLVED_DIR)
        if f.endswith(".bin")
    ])
    return roms[-2:] if len(roms) >= 2 else []

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def run_loop():
    print("🔁 Starting ROM evolution loop...")
    for iteration in range(1, ITERATIONS + 1):
        print(f"\n▶️ [{iteration}/{ITERATIONS}] Checking evolved_roms/ directory...")
        roms = get_sorted_roms()
        if len(roms) < 2:
            print("❌ Need at least two ROMs to compute delta.")
            break

        older_rom, newer_rom = roms
        print(f"📂 Older ROM:  {older_rom}")
        print(f"📂 Newer ROM:  {newer_rom}")

        # Step 1: Compute delta and delta sum
        delta_path = f"delta_log_{iteration}.txt"
        delta_sum = compute_delta_log_and_sum(older_rom, newer_rom, delta_path)
        if delta_sum is None:
            print("⚠️ Could not parse delta sum.")
            delta_sum = 0
        print(f"📊 Delta sum: {delta_sum}")

        # Step 2: Evolve try script using deltas
        print("🔁 Evolving try script from delta logs (weighted)...")
        evolve_try_script(delta_path, delta_path, "evolved_try_script.txt")

        # Step 3: Generate new ROM based on evolved script
        with open(newer_rom, "rb") as f:
            data = bytearray(f.read())
        for line in open("evolved_try_script.txt"):
            if line.startswith("#") or not line.strip():
                continue
            try:
                offset, value = line.strip().split()
                data[int(offset, 0)] = int(value, 16)
            except Exception as e:
                print(f"⚠️ Skipped line: {line.strip()} — {e}")
                continue

if __name__ == "__main__":
    run_loop()

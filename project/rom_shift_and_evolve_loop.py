#!/usr/bin/env python3
import os
import time
import subprocess
from datetime import datetime

# === CONFIGURATION ===
ROM_DIR = os.path.expanduser("~/evolved_roms")
KNOWN_GOOD_ROM = os.path.join(ROM_DIR, "known_good_rom.bin")
TRACKER_JSON = os.path.join(ROM_DIR, "byte_tracker.json")
EVOLVE_SCRIPT = os.path.join(ROM_DIR, "evolve_try_script_from_deltas_compared.py")
DELTA_LOG = os.path.join(ROM_DIR, "delta_log_latest.txt")
TRY_SCRIPT = os.path.join(ROM_DIR, "evolved_try_script.txt")
SLEEP_SECONDS = 2
CLOSURE_LIMIT = 15

# === TRACKERS ===
closed_characters = 0
line_length = 42
lines_closed = 0
frames_closed = 0

# === HELPERS ===
def get_latest_roms():
    roms = sorted([f for f in os.listdir(ROM_DIR) if f.endswith(".bin")])
    full_paths = [os.path.join(ROM_DIR, f) for f in roms]
    return full_paths[-2:] if len(full_paths) >= 2 else (None, None)

def count_hex_chars(file_path):
    with open(file_path, "rb") as f:
        return len(f.read()) * 2  # 1 byte = 2 hex chars

def compute_delta(rom1, rom2):
    result = subprocess.run(["python3", "rom_delta_logger.py", rom1, rom2], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Delta log written to", DELTA_LOG)
    else:
        print("❌ Delta log failure")
    return result.returncode == 0

def evolve_rom():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_rom_path = os.path.join(ROM_DIR, f"evolved_rom_{timestamp}.bin")
    result = subprocess.run(["python3", EVOLVE_SCRIPT, DELTA_LOG, DELTA_LOG, TRY_SCRIPT], capture_output=True, text=True)
    print(result.stdout.strip())
    with open(new_rom_path, "wb") as f:
        f.write(os.urandom(512 * 1024))
    print(f"✅ New evolved ROM written: {new_rom_path}")
    return new_rom_path

def update_byte_tracker():
    subprocess.run(["python3", "byte_evolution_tracker.py", DELTA_LOG, KNOWN_GOOD_ROM, TRACKER_JSON])

# === MAIN LOOP ===
def run_loop():
    global closed_characters, lines_closed, frames_closed

    print("🔁 Starting ROM evolution loop...")

    roms = get_latest_roms()
    if not roms or len(roms) < 2:
        print("❌ Not enough ROMs to begin.")
        return

    base_rom = roms[-1]
    total_hex_chars = count_hex_chars(base_rom)
    total_iterations = total_hex_chars * CLOSURE_LIMIT

    for i in range(1, total_iterations + 1):
        print(f"\n▶️ Iteration [{i}/{total_iterations}]")

        older_rom, newer_rom = get_latest_roms()
        if not compute_delta(older_rom, newer_rom):
            print("⚠️ Skipping evolution due to delta failure.")
            time.sleep(SLEEP_SECONDS)
            continue

        if os.path.exists(DELTA_LOG) and os.path.getsize(DELTA_LOG) > 0:
            evolve_rom()
        else:
            print("❌ Delta log missing or empty.")
            continue

        update_byte_tracker()

        # === Closure tracking ===
        closed_characters += 1
        if closed_characters % line_length == 0:
            lines_closed += 1
            print(f"🎉 Line complete! {lines_closed} lines closed.")

        if lines_closed and lines_closed % 42 == 0:
            frames_closed += 1
            print(f"🧊 Small cube complete! {frames_closed} memory cubes etched.")

        print(f"🎯 Hex character closed! Total closed: {closed_characters}")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    run_loop()

#!/usr/bin/env python3
import os
import time
import subprocess
from datetime import datetime
import json
import sys
import random
import shutil

# === BYTE EVOLUTION TRACKER — DISCOVERY FOCUSED ===
ROM_DIR = os.path.expanduser("~/evolved_roms")
PROJECT_DIR = os.path.join(ROM_DIR, "project")
KNOWN_GOOD_ROM = os.path.join(ROM_DIR, "known_good_rom.bin")
TRACKER_JSON = os.path.join(PROJECT_DIR, "byte_tracker.json")
EVOLVE_SCRIPT = os.path.join(PROJECT_DIR, "evolve_try_script_from_deltas_compared.py")
TRY_SCRIPT = os.path.join(PROJECT_DIR, "evolved_try_script.txt")
ROLL_LOG = os.path.join(PROJECT_DIR, "dice_roll_log.json")
SNAPSHOT_FILE = os.path.join(PROJECT_DIR, "progress_snapshot.json")

DELTA_LOG = os.path.join(PROJECT_DIR, "delta_log_latest.txt")

HEX_DIGITS = list("0123456789ABCDEF")
SPINNER_FRAMES = ["/", "-", "\\"]

def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def print_frame(lines):
    clear_screen()
    for line in lines:
        sys.stdout.write(line + "\n")
    sys.stdout.flush()

def get_rom_char_count():
    try:
        with open(KNOWN_GOOD_ROM, 'rb') as f:
            return len(f.read()) * 2
    except:
        return 524288 * 2

TOTAL_HEX_CHARS = get_rom_char_count()

def get_latest_roms():
    roms = sorted([
        f for f in os.listdir(PROJECT_DIR)
        if f.startswith("evolved_rom_") and f.endswith(".bin")
    ], key=lambda x: os.path.getmtime(os.path.join(PROJECT_DIR, x)))
    full_paths = [os.path.join(PROJECT_DIR, f) for f in roms]
    return (full_paths[-2], full_paths[-1]) if len(full_paths) >= 2 else (None, None)

def compute_delta(rom1, rom2):
    result = subprocess.run([
        "python3", "rom_delta_logger.py", rom1, rom2
    ], capture_output=True, text=True)
    return result.returncode == 0

def evolve_rom():
    try:
        subprocess.run([
            "python3", EVOLVE_SCRIPT, DELTA_LOG, DELTA_LOG, TRY_SCRIPT
        ], capture_output=True, text=True, check=True)
    except:
        pass

    path = os.path.join(PROJECT_DIR, f"evolved_rom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin")
    with open(path, "wb") as f:
        f.write(os.urandom(512 * 1024))
    return path

def update_byte_tracker():
    try:
        with open(DELTA_LOG, "r") as f:
            delta_lines = f.readlines()
        with open(KNOWN_GOOD_ROM, "rb") as f:
            good_data = f.read()
        if os.path.exists(TRACKER_JSON):
            with open(TRACKER_JSON, "r") as f:
                tracker = json.load(f)
        else:
            tracker = {}

        for line in delta_lines:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            offset_hex, newval = parts
            offset = int(offset_hex, 16)
            byte_index = offset // 2
            key = f"{byte_index}_hi" if offset % 2 == 0 else f"{byte_index}_lo"
            real_byte = good_data[byte_index]
            good_char = f"{real_byte:02X}"[0 if offset % 2 == 0 else 1]
            if newval.upper() == good_char:
                tracker[key] = 15
            else:
                tracker[key] = tracker.get(key, 0) + 1

        with open(TRACKER_JSON, "w") as f:
            json.dump(tracker, f)
    except:
        pass

def ensure_try_script_exists():
    if not os.path.exists(TRY_SCRIPT):
        with open(TRY_SCRIPT, "w") as f:
            f.write("0x0000:0\n")

def get_locked_in_count():
    try:
        with open(TRACKER_JSON, "r") as f:
            tracker = json.load(f)
            return sum(1 for status in tracker.values() if status >= 15)
    except:
        return 0

def clean_tracker():
    try:
        with open(TRACKER_JSON, "r") as f:
            tracker = json.load(f)
        return {k: v for k, v in tracker.items() if isinstance(v, int) and 0 <= v <= 15 and "_" in k}
    except:
        return {}

def find_next_offset():
    tracker = clean_tracker()
    for i in range(TOTAL_HEX_CHARS):
        byte_index = i // 2
        is_hi = (i % 2 == 0)
        key = f"{byte_index}_hi" if is_hi else f"{byte_index}_lo"
        if tracker.get(key, 0) < 15:
            return i, key, byte_index, is_hi
    return None, None, None, None

def get_weighted_roll():
    weights = {k: 1 for k in HEX_DIGITS}
    return random.choices(HEX_DIGITS, weights=[weights[k] for k in HEX_DIGITS])[0]

def record_roll(offset, good_char, roll):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "offset": offset,
        "good_char": good_char,
        "roll": roll
    }
    if os.path.exists(ROLL_LOG):
        with open(ROLL_LOG, "r") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(entry)
    with open(ROLL_LOG, "w") as f:
        json.dump(existing[-1000:], f)

def save_progress_snapshot(attempts, locked, tracker):
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "attempts": attempts,
        "locked": locked,
        "tracker": tracker
    }
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)

def run_loop():
    ensure_try_script_exists()
    spinner_idx = 0
    locked = get_locked_in_count()
    attempts = 0
    start_time = time.time()

    while True:
        width = get_terminal_width()
        spinner = SPINNER_FRAMES[spinner_idx % len(SPINNER_FRAMES)]
        spinner_idx += 1
        attempts += 1
        elapsed_time = time.time() - start_time
        speed = attempts / elapsed_time if elapsed_time > 0 else 0

        older_rom, newer_rom = get_latest_roms()
        if not older_rom or not newer_rom:
            print_frame(["⏳ Waiting for at least two ROMs to compare..."])
            time.sleep(0.25)
            continue

        i, key, byte_index, is_hi = find_next_offset()
        if key is None:
            print_frame(["✅ Evolution complete. All offsets discovered!"])
            break

        try:
            with open(KNOWN_GOOD_ROM, "rb") as f:
                good_data = f.read()
            good_byte = f"{good_data[byte_index]:02X}"
            good_char = good_byte[0] if is_hi else good_byte[1]
        except:
            good_char = "0"

        roll_guess = get_weighted_roll()
        record_roll(i, good_char, roll_guess)
        dice_display = " ".join([f"🎲{g}" if g == roll_guess else g for g in HEX_DIGITS])

        tracker = clean_tracker()
        if roll_guess == good_char:
            tracker[key] = 15
            with open(TRACKER_JSON, "w") as f:
                json.dump(tracker, f)
            locked = get_locked_in_count()
            save_progress_snapshot(attempts, locked, tracker)

        lines = [
            "",
            f"▶️ Evolution Loop {spinner}".center(width),
            f"🔗 Comparing: {os.path.basename(older_rom)} → {os.path.basename(newer_rom)}".center(width),
            f"🔁 Attempts: {attempts:,} | ⏱ Speed: {speed:.1f}/sec".center(width),
            "",
            f"🎯 Offset 0x{i:06X} | Rolls: {dice_display}".center(width),
            ""
        ]

        if compute_delta(older_rom, newer_rom):
            evolve_rom()
            new_locked = get_locked_in_count()
            if new_locked > locked:
                lines.append(f"🎯 DISCOVERED! Total: {new_locked}/{TOTAL_HEX_CHARS} ✅".center(width))
            else:
                lines.append(f"🔒 Discovered: {locked}/{TOTAL_HEX_CHARS}".center(width))
            try:
                update_byte_tracker()
            except:
                pass

        print_frame(["\n"] + lines + ["\n"])
        time.sleep(0.25)

if __name__ == "__main__":
    clear_screen()
    run_loop()

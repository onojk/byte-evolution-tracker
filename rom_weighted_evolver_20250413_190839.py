#!/usr/bin/env python3
import os
import time
import json
import random
from pathlib import Path

# === CONFIGURATION ===
rom_dir = Path.home() / "evolved_roms"
rom_dir.mkdir(exist_ok=True)
weights_file = Path.home() / "char_weights.json"
max_iterations = 50
rom_size = 512 * 1024  # 512KB ROM size
sleep_time = 5

# === UTILITY: Load or init weights ===
def load_weights():
    if weights_file.exists():
        with open(weights_file, "r") as f:
            return json.load(f)
    else:
        return {f"{i:X}": 1.0 for i in range(16)}

def save_weights(weights):
    with open(weights_file, "w") as f:
        json.dump(weights, f, indent=2)

# === UTILITY: Weighted nibble chooser ===
def weighted_guess(weights):
    total = sum(weights.values())
    r = random.uniform(0, total)
    upto = 0
    for char, w in weights.items():
        if upto + w >= r:
            return char
        upto += w
    return random.choice(list(weights))  # fallback

# === UTILITY: Generate ROM ===
def generate_rom(weights):
    return bytes(int(weighted_guess(weights) + weighted_guess(weights), 16)
                 for _ in range(rom_size))

# === UTILITY: Delta sum calculation ===
def compute_delta_sum(rom_a, rom_b):
    return sum(abs(a - b) for a, b in zip(rom_a, rom_b))

# === MAIN LOOP ===
def evolve_roms():
    weights = load_weights()
    roms = sorted(rom_dir.glob("evolved_rom_*.bin"))

    # Create first ROMs if none exist
    if len(roms) < 2:
        print("⚙️ Generating initial ROMs...")
        for i in range(2):
            rom = generate_rom(weights)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            path = rom_dir / f"evolved_rom_{stamp}_{i}.bin"
            with open(path, "wb") as f:
                f.write(rom)
            print(f"🆕 Created: {path}")
            time.sleep(1)
        roms = sorted(rom_dir.glob("evolved_rom_*.bin"))

    for i in range(1, max_iterations + 1):
        print(f"\n▶️ [{i}/{max_iterations}] ROM evolution step")

        roms = sorted(rom_dir.glob("evolved_rom_*.bin"))
        if len(roms) < 2:
            print("❌ Not enough ROMs for evolution.")
            break

        # Pick last two
        older_rom_path = roms[-2]
        newer_rom_path = roms[-1]
        print(f"📂 Older ROM: {older_rom_path}")
        print(f"📂 Newer ROM: {newer_rom_path}")

        with open(older_rom_path, "rb") as f1, open(newer_rom_path, "rb") as f2:
            older_rom = f1.read()
            newer_rom = f2.read()

        if len(older_rom) != len(newer_rom):
            print("❌ ROM sizes differ. Skipping iteration.")
            continue

        prev_delta = compute_delta_sum(older_rom, newer_rom)
        print(f"📊 Previous delta sum: {prev_delta}")

        # Generate next ROM using weights
        next_rom = bytearray()
        for a, b in zip(older_rom, newer_rom):
            nibble_pair = []
            for nibble_a, nibble_b in zip(f"{a:02X}", f"{b:02X}"):
                choice = weighted_guess(weights)
                nibble_pair.append(choice)
            byte = int("".join(nibble_pair), 16)
            next_rom.append(byte)

        # Save next ROM
        stamp = time.strftime("%Y%m%d_%H%M%S")
        out_path = rom_dir / f"evolved_rom_{stamp}_{i}.bin"
        with open(out_path, "wb") as f:
            f.write(next_rom)
        print(f"💾 Wrote new ROM: {out_path}")

        # Compare new ROM to newer_rom to determine feedback
        delta = compute_delta_sum(newer_rom, next_rom)
        delta_trend = "UNCHANGED"
        if delta < prev_delta:
            delta_trend = "SHRANK"
        elif delta > prev_delta:
            delta_trend = "GREW"
        print(f"📉 Delta sum {delta_trend}: {prev_delta} → {delta}")

        # Adjust weights based on delta trend
        for byte_new, byte_latest in zip(next_rom, newer_rom):
            for nib_new, nib_latest in zip(f"{byte_new:02X}", f"{byte_latest:02X}"):
                if delta_trend == "SHRANK":
                    weights[nib_new] += 0.1
                    weights[nib_latest] += 0.1
                elif delta_trend == "GREW":
                    weights[nib_new] = max(0.1, weights[nib_new] - 0.05)

        save_weights(weights)
        time.sleep(sleep_time)

# === ENTRY POINT ===
if __name__ == "__main__":
    evolve_roms()

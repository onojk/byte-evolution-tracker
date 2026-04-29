#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime

# === CONFIG ===
log1_path = "rom_delta_log_1_20250413_090649.txt"
log2_path = "rom_delta_log_2_20250413_090649.txt"
output_script = "evolved_try_script.txt"
weights_file = "delta_weights.json"

# === Load logs ===
def parse_delta_log(path):
    delta_map = {}
    with open(path, 'r') as f:
        for line in f:
            if line.startswith("(") and "):" in line:
                coord, delta = line.strip().split(":")
                coord = tuple(map(int, coord.strip("()").split(",")))
                delta_map[coord] = int(delta.strip())
    return delta_map

delta1 = parse_delta_log(log1_path)
delta2 = parse_delta_log(log2_path)

# === Load or init weights ===
if os.path.exists(weights_file):
    with open(weights_file, "r") as wf:
        weights = json.load(wf)
        weights = {tuple(map(int, k.split(","))): v for k, v in weights.items()}
else:
    weights = {}

# === Auto-weight logic ===
selection = {}
for coord in sorted(set(delta1) | set(delta2)):
    d1 = delta1.get(coord, float('inf'))
    d2 = delta2.get(coord, float('inf'))

    if coord not in weights:
        weights[coord] = 1.0

    if d2 < d1:
        weights[coord] *= 1.05  # reward progress
        selection[coord] = "use_log2"
    elif d2 > d1:
        weights[coord] *= 0.95  # penalize regression
        selection[coord] = "use_log1"
    else:
        # No change — lean toward heavier weighted choice
        w1 = weights.get(coord, 1.0)
        if w1 > 1.0:
            selection[coord] = "use_log1"
        else:
            selection[coord] = "use_log2"

# === Normalize weights to avoid runaway growth ===
max_weight = max(weights.values(), default=1.0)
if max_weight > 10.0:
    for k in weights:
        weights[k] /= max_weight

# === Save selection script ===
with open(output_script, "w") as f:
    for (line, idx), decision in sorted(selection.items()):
        f.write(f"{line},{idx} = {decision}\n")

print(f"✅ Selection file written: {output_script}")

# === Save updated weights ===
with open(weights_file, "w") as wf:
    json.dump({f"{k[0]},{k[1]}": v for k, v in weights.items()}, wf, indent=2)

print(f"📈 Weights updated and saved to: {weights_file}")

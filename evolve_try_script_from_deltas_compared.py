#!/usr/bin/env python3

# === SCRIPT: evolve_try_script_from_deltas_compared.py ===
# Merges delta logs into a new patch script based on a selection file.

import sys
import re
from datetime import datetime

if len(sys.argv) != 4:
    print("Usage: evolve_try_script_from_deltas_compared.py <log1> <log2> <output>")
    sys.exit(1)

log1_path, log2_path, output_path = sys.argv[1:4]
selection_path = "evolved_try_script.txt"

# Read logs
with open(log1_path, 'r') as f:
    log1_lines = f.readlines()
with open(log2_path, 'r') as f:
    log2_lines = f.readlines()
with open(selection_path, 'r') as f:
    selections = [line.strip() for line in f if line.strip()]

# Parse logs
delta_pattern = re.compile(r"Line (\d+):")
def parse_log(lines):
    data = {}
    current_line = None
    for line in lines:
        match = delta_pattern.match(line)
        if match:
            current_line = int(match.group(1))
        elif "idx" in line and current_line is not None:
            idx_match = re.search(r"idx (\d+):", line)
            if idx_match:
                idx = int(idx_match.group(1))
                data[(current_line, idx)] = line.strip()
    return data

log1_data = parse_log(log1_lines)
log2_data = parse_log(log2_lines)

# Select best entries based on selection file
results = []
for sel in selections:
    try:
        parts = sel.split()
        line, idx = int(parts[0]), int(parts[1])
        source = parts[2]
        chosen = log1_data if source == "use_log1" else log2_data
        results.append(chosen.get((line, idx), f"# Missing {source} data for {line:03d} {idx:02d}"))
    except Exception as e:
        results.append(f"# Error parsing selection: {sel} ({e})")

# Save output
with open(output_path, 'w') as f:
    f.write("\n".join(results))

print(f"📄 Created evolved ROM script: {output_path}")

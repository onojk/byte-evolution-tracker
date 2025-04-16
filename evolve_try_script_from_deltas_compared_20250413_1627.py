#!/usr/bin/env python3

# === SCRIPT: evolve_try_script_from_deltas_compared_20250413_1627.py ===
# This script combines two delta logs based on a third file specifying which line+idx to use from each log.
# 📅 Creation timestamp: 20250413_1627

import sys
import re

# File paths
log1_path = "rom_delta_log_1_20250413_090649.txt"
log2_path = "rom_delta_log_2_20250413_090649.txt"
selection_path = "evolved_try_script.txt"
output_path = "evolved_rom_try_script_output.txt"

# Read in the logs
with open(log1_path, 'r') as f:
    log1_lines = f.readlines()

with open(log2_path, 'r') as f:
    log2_lines = f.readlines()

# Read selection list
with open(selection_path, 'r') as f:
    selections = [line.strip() for line in f if line.strip()]

# Parse both logs into a dict: {(line_number, idx_number): line_text}
delta_pattern = re.compile(r"Line (\d+):")

def parse_log(lines):
    log_data = {}
    current_line = None
    for line in lines:
        match = delta_pattern.match(line)
        if match:
            current_line = int(match.group(1))
        elif "idx" in line and current_line is not None:
            idx_match = re.search(r"idx (\d+):", line)
            if idx_match:
                idx = int(idx_match.group(1))
                log_data[(current_line, idx)] = line.strip()
    return log_data

log1_data = parse_log(log1_lines)
log2_data = parse_log(log2_lines)

# Merge based on selection
result_lines = []
for selection in selections:
    try:
        parts = selection.split()
        line_num = int(parts[0])
        idx_num = int(parts[1])
        choice = parts[2]
        if choice == "use_log1":
            result = log1_data.get((line_num, idx_num), f"# Missing log1 data for {line_num:03d} {idx_num:02d}")
        else:
            result = log2_data.get((line_num, idx_num), f"# Missing log2 data for {line_num:03d} {idx_num:02d}")
        result_lines.append(result)
    except Exception as e:
        result_lines.append(f"# Error processing line: {selection} ({e})")

# Save the merged result
with open(output_path, 'w') as f:
    f.write("\n".join(result_lines))

print(f"✅ Merged delta output saved to {output_path}")

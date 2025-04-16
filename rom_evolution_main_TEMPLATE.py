#!/usr/bin/env python3

# === SCRIPT: rom_evolution_main_20250413_1633.py ===
# Master automation to evolve ROMs by comparing two delta logs and generating the next try script.

import re
from datetime import datetime
import subprocess

# === INPUT FILES ===
log1_path = "rom_delta_log_1_20250413_090649.txt"
log2_path = "rom_delta_log_2_20250413_090649.txt"
delta_report_path = "evolved_rom_try_script_output.txt"
selection_output_path = "evolved_try_script.txt"

# === CONFIG ===
delta_pattern = re.compile(r"idx (\d+):.*?\((\d+)\).*?\((\d+)\).*?→ Δ Notch = (\d+)")
idx_per_line = 40  # Assumes 40 indices per line

# Read the delta report
with open(delta_report_path, "r") as f:
    delta_lines = f.readlines()

# Group delta lines by line number and choose lower-delta entry
selection_lines = []
line_num = 1
idx_count = 0

for line in delta_lines:
    match = delta_pattern.search(line)
    if match:
        idx_str, log1_val, log2_val, delta = match.groups()
        idx = int(idx_str)
        delta = int(delta)
        chosen_log = "use_log1" if int(log1_val) <= int(log2_val) else "use_log2"
        if "Δ Notch = 0" in line:
            chosen_log = "# match"

        # Write selection or match comment
        if chosen_log.startswith("use"):
            selection_lines.append(f"{line_num:03d} {idx:02d} {chosen_log}")
        else:
            selection_lines.append(f"# {line.strip()}")

        idx_count += 1
        if idx_count == idx_per_line:
            idx_count = 0
            line_num += 1

# Write new selection file
with open(selection_output_path, "w") as f:
    f.write("\n".join(selection_lines) + "\n")

print(f"✅ Selection file written: {selection_output_path}")

# Auto-run the evolve script
subprocess.run([
    "python3", "evolve_try_script_from_deltas_compared.py"
])

print(f"✅ Evolved try script regenerated using updated selection.")

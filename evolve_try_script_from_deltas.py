#!/usr/bin/env python3
import re

delta_file_1 = "rom_delta_log_1_20250413_090649.txt"
delta_file_2 = "rom_delta_log_2_20250413_090649.txt"
output_file = "evolved_try_script.txt"

def parse_deltas(filename):
    deltas = {}  # {(line_number, idx_number): delta_value}
    with open(filename) as f:
        line_num = 0
        for line in f:
            if line.startswith("Line "):
                line_num = int(re.search(r"Line (\d+):", line).group(1))
            matches = re.findall(r"idx (\d+):.*→ Δ Notch = (\d+)", line)
            for idx_str, delta_str in matches:
                idx = int(idx_str)
                delta = int(delta_str)
                deltas[(line_num, idx)] = delta
    return deltas

delta1 = parse_deltas(delta_file_1)
delta2 = parse_deltas(delta_file_2)

# Evolve by picking the smaller delta from the two
evolved = {}
for key in sorted(set(delta1.keys()) | set(delta2.keys())):
    val1 = delta1.get(key, float('inf'))
    val2 = delta2.get(key, float('inf'))
    evolved[key] = "use_log1" if val1 <= val2 else "use_log2"

# Write output script
with open(output_file, "w") as out:
    for (line, idx), source in sorted(evolved.items()):
        out.write(f"{line:03d} {idx:02d} {source}\n")

print(f"[✓] Evolved try script written to: {output_file}")

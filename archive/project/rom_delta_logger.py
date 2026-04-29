#!/usr/bin/env python3
import sys
import os
from datetime import datetime

def compute_delta_sum(file1, file2):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        b1 = f1.read()
        b2 = f2.read()
        if len(b1) != len(b2):
            print("❌ ROM sizes differ, cannot compute delta.")
            return 0, []

        delta_sum = 0
        diffs = []

        for i in range(len(b1)):
            diff = abs(b1[i] - b2[i])
            delta_sum += diff
            diffs.append((i, b1[i], b2[i], diff))

        return delta_sum, diffs

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: rom_delta_logger.py <rom1> <rom2>")
        sys.exit(1)

    rom1_path = sys.argv[1]
    rom2_path = sys.argv[2]

    delta_sum, diffs = compute_delta_sum(rom1_path, rom2_path)

    # Auto-generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
import os
from datetime import datetime

# Make sure the output directory exists
output_dir = os.path.expanduser("~/delta_logs")
os.makedirs(output_dir, exist_ok=True)

# Auto-timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"delta_log_{timestamp}.txt")

# Write to that file instead
with open(output_path, "w") as f:
    ...

    with open(log_filename, "w") as f:
        f.write(f"Delta Sum: {delta_sum}\n")
        for index, b1, b2, diff in diffs:
            if diff > 0:
                f.write(f"0x{index:04X}: {b1:02X} -> {b2:02X} (Δ {diff})\n")

    print(f"✅ Delta log written to {os.path.abspath(log_filename)} with sum {delta_sum}")

#!/usr/bin/env python3
import sys
import re
from datetime import datetime

def parse_log(path):
    deltas = {}
    with open(path, "r") as f:
        for line in f:
            match = re.match(r"0x([0-9A-Fa-f]+): .*Δ (\d+)", line)
            if match:
                offset = int(match.group(1), 16)
                delta = int(match.group(2))
                deltas[offset] = delta
    return deltas

def main(log1, log2, output_file):
    deltas1 = parse_log(log1)
    deltas2 = parse_log(log2)
    result = {}

    all_offsets = set(deltas1.keys()) | set(deltas2.keys())
    for offset in sorted(all_offsets):
        d1 = deltas1.get(offset, float("inf"))
        d2 = deltas2.get(offset, float("inf"))
        result[offset] = min(d1, d2)

    with open(output_file, "w") as f:
        for offset in sorted(result.keys()):
            value = result[offset]
            # Only use values that are not inf (seen in at least one log)
            if value != float("inf"):
                f.write(f"0x{offset:04X}:{value}\n")

    print(f"✅ Selection file written: {output_file} — {len(result)} entries")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: evolve_try_script_from_deltas_compared.py <log1> <log2> <output>")
        sys.exit(1)

    log1 = sys.argv[1]
    log2 = sys.argv[2]
    output = sys.argv[3]
    main(log1, log2, output)

import sys
import random
import json
import os

WEIGHTS_FILE = "delta_weights.json"

def evolve_try_script(log1, log2, output_file):
    weights = load_weights()
    diffs1 = parse_log(log1)
    diffs2 = parse_log(log2)
    if not diffs1 or not diffs2:
        print("⚠️ Could not load delta logs.")
        return

    final = {}
    for k in set(diffs1.keys()).union(diffs2.keys()):
        v1 = diffs1.get(k, 0)
        v2 = diffs2.get(k, 0)
        trending = v1 - v2
        weights[k] = weights.get(k, 1.0) + trending / 100.0
        final[k] = int(random.choices(range(256), weights=[weights[k]]*256)[0])

    with open(output_file, "w") as out:
        for k, val in final.items():
            out.write(f"{k} {val:02X}\n")
    with open(WEIGHTS_FILE, "w") as w:
        json.dump(weights, w)
    print(f"✅ Selection file written: {output_file}")
    print("📈 Weights updated.")

def load_weights():
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE) as f:
            return json.load(f)
    return {}

def parse_log(path):
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path) as f:
        for line in f:
            if "->" in line:
                parts = line.split()
                try:
                    idx = int(parts[0])
                    delta = abs(int(parts[2], 16) - int(parts[0], 16))
                    out[idx] = delta
                except:
                    continue
    return out

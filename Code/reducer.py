#!/usr/bin/env python3
# Question a — Chiffre d'affaires total par item
# Reducer : additionne tous les coûts par item

import sys

current_item = None
current_total = 0.0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        continue
    item, cost = parts[0], parts[1]
    try:
        cost = float(cost)
    except ValueError:
        continue

    if item == current_item:
        current_total += cost
    else:
        if current_item is not None:
            print(f"{current_item}\t{current_total:.2f}")
        current_item = item
        current_total = cost

# dernier item
if current_item is not None:
    print(f"{current_item}\t{current_total:.2f}")

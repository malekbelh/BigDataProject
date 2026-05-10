#!/usr/bin/env python3
# Question b — Item le plus vendu selon le chiffre d'affaires
# Mapper : identique à la question a (mapper.py)
# Reducer : garde uniquement l'item avec le chiffre d'affaires maximal

import sys

current_item = None
current_total = 0.0
best_item = None
best_total = 0.0

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
            if current_total > best_total:
                best_total = current_total
                best_item = current_item
        current_item = item
        current_total = cost

# dernier item
if current_item is not None:
    if current_total > best_total:
        best_total = current_total
        best_item = current_item

if best_item is not None:
    print(f"{best_item}\t{best_total:.2f}")

#!/usr/bin/env python3
# Question c — Moyenne de vente par Store
# Reducer : calcule la moyenne des ventes pour chaque store

import sys

current_store = None
total = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        continue
    store, cost = parts[0], parts[1]
    try:
        cost = float(cost)
    except ValueError:
        continue

    if store == current_store:
        total += cost
        count += 1
    else:
        if current_store is not None:
            average = total / count
            print(f"{current_store}\t{average:.2f}")
        current_store = store
        total = cost
        count = 1

# dernier store
if current_store is not None:
    average = total / count
    print(f"{current_store}\t{average:.2f}")

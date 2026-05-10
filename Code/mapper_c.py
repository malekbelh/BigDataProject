#!/usr/bin/env python3
# Question c — Moyenne de vente par Store
# Mapper : extrait la paire (store, cost)

import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    fields = line.split('\t')
    if len(fields) < 5:
        continue
    store = fields[2]  # 3ème colonne = store
    cost = fields[4]   # 5ème colonne = cost
    try:
        float(cost)
        print(f"{store}\t{cost}")
    except ValueError:
        continue

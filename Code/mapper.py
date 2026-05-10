#!/usr/bin/env python3
# Question a — Chiffre d'affaires total par item
# Mapper : extrait la paire (item, cost) de chaque ligne
# Format purchases.txt : date\theure\tstore\titem\tcost\tpayment_method

import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    fields = line.split('\t')
    if len(fields) < 5:
        continue
    item = fields[3]   # 4ème colonne = item
    cost = fields[4]   # 5ème colonne = cost
    try:
        float(cost)  # valider que c'est un nombre
        print(f"{item}\t{cost}")
    except ValueError:
        continue

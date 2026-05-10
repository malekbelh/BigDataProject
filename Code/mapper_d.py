#!/usr/bin/env python3
# Question d — Item le plus vendu par Store (en nombre de ventes)
# Mapper : émet (store\titem, 1) pour chaque transaction

import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    fields = line.split('\t')
    if len(fields) < 4:
        continue
    store = fields[2]  # 3ème colonne = store
    item = fields[3]   # 4ème colonne = item
    # clé composée : store + séparateur + item
    print(f"{store}\t{item}\t1")

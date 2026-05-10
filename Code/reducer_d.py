#!/usr/bin/env python3
# Question d — Item le plus vendu par Store (en nombre de ventes)
# Reducer : pour chaque store, retient l'item avec le plus grand nombre de ventes

import sys

# Structure : stocker par store le meilleur item
# Les données arrivent triées par clé (store\titem)

current_store = None
current_item = None
current_count = 0

best_item = None
best_count = 0

def emit_best(store, item, count):
    print(f"{store}\t{item}\t{count}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 3:
        continue
    store, item, count_str = parts
    try:
        count = int(count_str)
    except ValueError:
        continue

    if store == current_store:
        if item == current_item:
            current_count += count
        else:
            # nouvel item dans le même store
            if current_count > best_count:
                best_count = current_count
                best_item = current_item
            current_item = item
            current_count = count
    else:
        # nouveau store
        if current_store is not None:
            # finaliser le dernier item du store précédent
            if current_count > best_count:
                best_count = current_count
                best_item = current_item
            emit_best(current_store, best_item, best_count)
        current_store = store
        current_item = item
        current_count = count
        best_item = item
        best_count = 0

# dernier store
if current_store is not None:
    if current_count > best_count:
        best_count = current_count
        best_item = current_item
    emit_best(current_store, best_item, best_count)

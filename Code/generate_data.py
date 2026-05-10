#!/usr/bin/env python3
# Script de génération des datasets jeux vidéo
# À exécuter dans le container namenode :
# python3 /workspace/Data/generate_data.py

import pandas as pd
import random
from faker import Faker

fake = Faker()
random.seed(42)

# ── PARAMÈTRES ──────────────────────────────────────────
NB_PLAYERS = 5000
NB_GAMES   = 200
NB_SESSIONS = 20000

GENRES  = ["RPG", "FPS", "Sport", "Strategy", "Adventure", "Simulation"]
LEVELS  = ["Beginner", "Mid", "Advanced"]
PLATFORMS = ["PC", "PS5", "Xbox", "Switch"]

# ── TABLE PLAYERS ────────────────────────────────────────
players = []
for i in range(1, NB_PLAYERS + 1):
    players.append({
        "player_id": i,
        "username":  fake.user_name(),
        "age":       random.randint(12, 60),
        "country":   fake.country(),
        "level":     random.choice(LEVELS),
        "platform":  random.choice(PLATFORMS),
    })

df_players = pd.DataFrame(players)
df_players.to_csv("/workspace/Data/players.csv", index=False)
print(f"✅ players.csv généré — {len(df_players)} lignes")

# ── TABLE GAMES ──────────────────────────────────────────
games = []
for i in range(1, NB_GAMES + 1):
    games.append({
        "game_id":   i,
        "title":     fake.catch_phrase(),
        "genre":     random.choice(GENRES),
        "year":      random.randint(2015, 2024),
        "publisher": fake.company(),
    })

df_games = pd.DataFrame(games)
df_games.to_csv("/workspace/Data/games.csv", index=False)
print(f"✅ games.csv généré — {len(df_games)} lignes")

# ── TABLE SESSIONS ───────────────────────────────────────
sessions = []
for i in range(1, NB_SESSIONS + 1):
    level = random.choice(LEVELS)
    # Les advanced ont de meilleures stats
    xp_base     = {"Beginner": 300, "Mid": 1500, "Advanced": 5000}[level]
    quest_base  = {"Beginner": 2,   "Mid": 8,    "Advanced": 25}[level]
    enemy_base  = {"Beginner": 15,  "Mid": 40,   "Advanced": 100}[level]

    sessions.append({
        "session_id": i,
        "player_id":  random.randint(1, NB_PLAYERS),
        "game_id":    random.randint(1, NB_GAMES),
        "duration_min": random.randint(10, 300),
        "xp_gained":  int(random.gauss(xp_base, xp_base * 0.3)),
        "quests_done": max(0, int(random.gauss(quest_base, quest_base * 0.4))),
        "enemies_killed": max(0, int(random.gauss(enemy_base, enemy_base * 0.3))),
        "score":      random.randint(100, 10000),
        "player_level": level,
    })

df_sessions = pd.DataFrame(sessions)
df_sessions.to_csv("/workspace/Data/sessions.csv", index=False)
print(f"✅ sessions.csv généré — {len(df_sessions)} lignes")

# ── CHARGEMENT DANS HDFS ─────────────────────────────────
import os
print("\n📤 Chargement dans HDFS...")
os.system("hdfs dfs -mkdir -p /data/videogames")
os.system("hdfs dfs -put -f /workspace/Data/players.csv  /data/videogames/")
os.system("hdfs dfs -put -f /workspace/Data/games.csv    /data/videogames/")
os.system("hdfs dfs -put -f /workspace/Data/sessions.csv /data/videogames/")
print("✅ Fichiers chargés dans HDFS : /data/videogames/")

#!/usr/bin/env python3
# spark_job.py — Calcul des 3 KPIs jeux vidéo
# Exécution :
# spark-submit --master spark://spark-master:7077 /opt/spark-data/spark_job.py

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ── INITIALISATION SPARK ─────────────────────────────────
spark = SparkSession.builder \
    .appName("VideoGames-KPIs") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("✅ SparkSession démarrée")

# ── CHARGEMENT DES DONNÉES ───────────────────────────────
print("\n📂 Chargement des datasets...")

sessions = spark.read.csv(
    "hdfs://namenode:9000/data/videogames/sessions.csv",
    header=True, inferSchema=True
)
players = spark.read.csv(
    "hdfs://namenode:9000/data/videogames/players.csv",
    header=True, inferSchema=True
)
games = spark.read.csv(
    "hdfs://namenode:9000/data/videogames/games.csv",
    header=True, inferSchema=True
)

print(f"  sessions : {sessions.count()} lignes")
print(f"  players  : {players.count()} lignes")
print(f"  games    : {games.count()} lignes")

# ════════════════════════════════════════════════════════
# KPI 1 — Statistiques moyennes par session
# ════════════════════════════════════════════════════════
print("\n📊 KPI 1 — Statistiques moyennes par session...")

kpi1 = sessions.groupBy("session_id").agg(
    F.avg("xp_gained").alias("avg_xp"),
    F.avg("quests_done").alias("avg_quests"),
    F.avg("enemies_killed").alias("avg_enemies"),
    F.avg("duration_min").alias("avg_duration_min"),
    F.avg("score").alias("avg_score")
)

print("\n=== KPI 1 — Résultats (top 10) ===")
kpi1.orderBy("session_id").show(10)

kpi1.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/results/kpi1_session_stats"
)
print("✅ KPI 1 sauvegardé dans HDFS : /results/kpi1_session_stats")

# ════════════════════════════════════════════════════════
# KPI 2 — Métriques par genre de jeux
#          (jointure sessions + games + players)
# ════════════════════════════════════════════════════════
print("\n📊 KPI 2 — Métriques par genre de jeux...")

# Jointure sessions ↔ games ↔ players
joined = sessions \
    .join(games,   sessions.game_id   == games.game_id,   "inner") \
    .join(players, sessions.player_id == players.player_id, "inner")

kpi2 = joined.groupBy("genre").agg(
    F.count("session_id").alias("nb_sessions"),
    F.countDistinct(sessions.player_id).alias("nb_players"),
    F.avg("score").alias("avg_score"),
    F.avg("duration_min").alias("avg_duration_min"),
    F.avg("xp_gained").alias("avg_xp"),
    F.sum("score").alias("total_score")
).orderBy(F.desc("nb_sessions"))

print("\n=== KPI 2 — Résultats par genre ===")
kpi2.show()

kpi2.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/results/kpi2_genre_metrics"
)
print("✅ KPI 2 sauvegardé dans HDFS : /results/kpi2_genre_metrics")

# ════════════════════════════════════════════════════════
# KPI 3 — Métriques par niveau de joueur
#          (Beginner / Mid / Advanced)
# ════════════════════════════════════════════════════════
print("\n📊 KPI 3 — Métriques par niveau de joueur...")

kpi3 = sessions.groupBy("player_level").agg(
    F.count("session_id").alias("nb_sessions"),
    F.countDistinct("player_id").alias("nb_players"),
    F.avg("xp_gained").alias("avg_xp"),
    F.avg("quests_done").alias("avg_quests"),
    F.avg("enemies_killed").alias("avg_enemies"),
    F.avg("score").alias("avg_score"),
    F.avg("duration_min").alias("avg_duration_min")
).orderBy("player_level")

print("\n=== KPI 3 — Résultats par niveau ===")
kpi3.show()

kpi3.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/results/kpi3_player_level"
)
print("✅ KPI 3 sauvegardé dans HDFS : /results/kpi3_player_level")

# ── FIN ──────────────────────────────────────────────────
print("\n🎉 Tous les KPIs calculés et sauvegardés en Parquet dans HDFS !")
spark.stop()

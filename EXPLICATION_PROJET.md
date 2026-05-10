# Explication complète du projet Big Data — Hadoop + Spark sur Docker

> **Etudiante :** Malek Belhouchet — 2ING2  
> **Cours :** Big Data  
> **Objectif :** Comprendre et présenter le projet à l'oral

---

## 🧠 L'idée générale — Pourquoi ce projet existe ?

Imagine que tu travailles dans une grande entreprise avec des **millions de données** (ventes, logs, transactions...). Un seul ordinateur ne peut pas traiter tout ça efficacement. La solution : **distribuer le travail sur plusieurs machines** qui collaborent ensemble — c'est ce qu'on appelle un **cluster**.

Ce projet met en place un cluster Hadoop distribué entièrement conteneurisé grâce à Docker, puis y exécute des traitements MapReduce et Spark sur des données réelles.

Le projet est divisé en **trois grandes parties** :
- **Partie 1 :** Installation et configuration du cluster Hadoop sur Docker
- **Partie 2 :** Exécution de jobs MapReduce sur le dataset `purchases.txt`
- **Partie 3 :** Intégration de Spark et traitement de données de jeux vidéo

---

## 🐳 Concept clé : Docker

Avant de parler de Hadoop, il faut comprendre **Docker**.

Docker permet de créer des **containers** — des sortes de mini-ordinateurs virtuels isolés qui tournent sur ta vraie machine. Chaque container a son propre système, ses propres programmes, mais ils peuvent communiquer entre eux.

> L'intérêt d'utiliser Docker est de pouvoir simuler un vrai cluster distribué sur une seule machine, avec chaque service isolé dans son propre container.

**En résumé :** au lieu d'avoir 6 vraies machines physiques, on simule 6 machines virtuelles (containers) sur un seul PC.

---

## 🏗️ Partie 1 — Construire le cluster Hadoop

### Qu'est-ce que Hadoop ?

Hadoop est un framework open-source qui permet de :
1. **Stocker** des données sur plusieurs machines → c'est **HDFS** (le système de fichiers distribué)
2. **Traiter** ces données en parallèle → c'est **MapReduce** + **YARN**

---

### L'architecture du cluster

Le cluster est composé de **6 services**, chacun correspondant à un container Docker distinct :

| Service | Port | Rôle |
|---|---|---|
| **Namenode** | 9870 / 9000 | Chef du stockage HDFS — gère les métadonnées de tous les fichiers |
| **Datanode-1** | 9864 | Stocke physiquement les blocs de données (replica 1) |
| **Datanode-2** | 9865 | Stocke physiquement les blocs de données (replica 2) |
| **Resource Manager** | 8088 / 8032 | Gère les ressources CPU/RAM du cluster (YARN) |
| **Node Manager** | 8042 | Exécute les tâches de calcul sur chaque nœud |
| **History Server** | 8188 | Conserve l'historique des jobs exécutés |

**Analogie simple :**
- Le **Namenode** = le bibliothécaire qui sait où est chaque livre, mais ne les stocke pas lui-même
- Les **Datanodes** = les étagères qui contiennent vraiment les livres
- Le **Resource Manager** = le chef de chantier qui distribue le travail
- Le **Node Manager** = les ouvriers qui font le travail
- Le **History Server** = le registre qui garde trace de tout ce qui a été fait

---

### Étape 1 — L'image Docker de base (`base/Dockerfile`)

La première étape consiste à créer une **image Docker de base partagée** par TOUS les containers du cluster.

Cette image contient :
- Java 11
- Hadoop 3.3.5
- Python 3
- Tous les outils nécessaires au fonctionnement du cluster

**Pourquoi une image commune ?**  
Parce que tous les services Hadoop (Namenode, Datanode, etc.) ont besoin de la même installation de Hadoop. En créant une image de base partagée, on évite de réinstaller Hadoop dans chaque container, ce qui économise du temps et de l'espace disque.

Ce fichier est la **recette** que Docker suit pour construire l'image. Il effectue les opérations suivantes dans l'ordre :

```dockerfile
FROM debian:11                  # Part d'un système Linux Debian vierge
RUN apt-get install ...         # Installe Java 11, curl, wget, Python3
# Téléchargement de Hadoop 3.3.5 depuis le site officiel Apache
ENV JAVA_HOME=...               # Configure les variables d'environnement
COPY conf/*.xml ...             # Copie les 4 fichiers de configuration XML
```

---

### Étape 2 — Le script de démarrage (`base/entrypoint.sh`)

Ce script est exécuté **au démarrage de chaque container**. Il charge les configurations d'environnement Hadoop et exécute la commande spécifiée par chaque service.

C'est comme un script de démarrage automatique — quand un container se lance, ce script s'exécute en premier pour tout préparer.

---

### Étape 3 — Les 4 fichiers de configuration XML (`base/conf/`)

Hadoop utilise quatre fichiers XML de configuration. Ces fichiers sont copiés dans l'image de base et donc disponibles dans **tous** les containers du cluster.

#### `core-site.xml` — Configuration générale de Hadoop
C'est le fichier le plus important. Il indique à tous les composants du cluster l'adresse du Namenode (le gestionnaire du système de fichiers distribué HDFS). Grâce au réseau Docker, le nom `namenode` est automatiquement résolu vers le bon container.

```xml
<property>
    <name>fs.defaultFS</name>
    <value>hdfs://namenode:9000</value>
</property>
```

#### `hdfs-site.xml` — Configuration du stockage HDFS
Ce fichier configure le système de fichiers distribué. Les paramètres importants sont :
- Le nombre minimum de Datanodes requis (2)
- Les répertoires de stockage des données
- La désactivation des permissions pour simplifier le développement

#### `mapred-site.xml` — Configuration de MapReduce
Le paramètre principal est `mapreduce.framework.name=yarn`, qui indique que les jobs doivent être exécutés via YARN (et non en mode local standalone).

#### `yarn-site.xml` — Configuration du gestionnaire de ressources
YARN (Yet Another Resource Negotiator) est le composant qui gère l'allocation des ressources (CPU, mémoire) pour les jobs. Ce fichier configure l'adresse du Resource Manager, active l'agrégation des logs, et configure le shuffle MapReduce.

---

### Étape 4 — Les Dockerfiles de chaque service

Chaque service du cluster a son propre dossier contenant un `Dockerfile` et un script `run.sh`. Tous ces Dockerfiles **héritent** de l'image de base créée précédemment :

```dockerfile
FROM hadoop-base:3.3.5-dorian   # Hérite de l'image de base
```

Cela signifie qu'ils ont déjà Hadoop installé et configuré.

**Le Namenode (`namenode/Dockerfile`) :**  
Le Namenode est le 'chef' de HDFS. Il ne stocke pas les données lui-même, mais conserve les métadonnées : il sait quels fichiers existent, où leurs blocs sont stockés sur quel Datanode, etc. Il expose le port 9870 pour son interface web.

**Les Datanodes (`datanode/Dockerfile`) :**  
Les Datanodes stockent physiquement les blocs de données. Le même Dockerfile est utilisé pour créer `datanode-1` et `datanode-2`. Avoir deux Datanodes permet la **redondance des données** (chaque bloc est répliqué sur les deux Datanodes).

**Le History Server (`historyserver/Dockerfile`) :**  
Le History Server conserve l'historique de tous les jobs MapReduce exécutés. Il est utile pour analyser les performances et débugger les jobs. Il utilise le service `timelineserver` de YARN.

---

### Étape 5 — Le fichier `docker-compose.yml`

Le fichier `docker-compose.yml` est le **chef d'orchestre** du cluster. Il définit tous les services, leurs dépendances, leurs ports exposés et leurs volumes. C'est ce fichier qui permet de lancer tout le cluster avec **une seule commande**.

Points clés du `docker-compose.yml` :

| Directive | Rôle |
|---|---|
| `depends_on` | Définit l'ordre de démarrage (les Datanodes attendent le Namenode, etc.) |
| `ports` | Mappe les ports du container vers la machine hôte (9870, 8088, 8188) |
| `volumes` | Partage les dossiers `Code/` et `Data/` entre la machine locale et le Namenode |
| `env_file` | Charge `hadoop.env` qui contient toutes les variables d'environnement partagées |
| réseau auto | Tous les containers communiquent par leur nom (ex: `namenode`, `resourcemanager`) |

Structure des services :

```yaml
version: '3'
services:
  namenode:       (ports 9870, 9000)
  datanode-1:     (port 9864, depends on namenode)
  datanode-2:     (port 9865, depends on namenode)
  resourcemanager:(ports 8032, 8088)
  nodemanager:    (depends on namenode + datanodes)
  historyserver:  (depends on tout le cluster)
```

---

### Étape 6 — Construction et démarrage du cluster

**Construction de l'image de base :**
```bash
docker build -t hadoop-base:3.3.5-dorian base/
```
Cette commande télécharge Debian, installe Java, et télécharge Hadoop 3.3.5 depuis les serveurs Apache. Les 15 étapes du Dockerfile s'exécutent avec succès.

**Démarrage de tous les containers :**
```bash
docker compose up -d
```
Docker construit d'abord les images de chaque service, puis les démarre dans l'ordre défini par `depends_on`. Le flag `-d` signifie "detached mode" (en arrière-plan).

**Vérification du cluster :**
```bash
docker exec -it namenode bash
hdfs dfsadmin -report
```

Le rapport confirme que :
- **Configured Capacity :** 1.97 TB — capacité totale du cluster
- **DFS Remaining :** 1.83 TB — espace disponible
- **Live datanodes (2)** — les deux Datanodes sont connectés et en état Normal
- **DFS Remaining% :** 93.18% — le cluster est quasi vide, prêt à recevoir des données

---

## ⚙️ Partie 2 — MapReduce sur `purchases.txt`

### Qu'est-ce que MapReduce ?

C'est le paradigme de traitement distribué de Hadoop. Il fonctionne en **deux phases** :
- **Map** : chaque worker lit une partie des données et produit des paires `(clé, valeur)`
- **Reduce** : les paires sont regroupées par clé et agrégées (somme, max, moyenne...)

**Analogie :** Imagine que tu veux compter les mots dans 1000 livres. Tu donnes 100 livres à chaque ami (Map), chacun compte ses mots, puis tu centralises et additionnes les résultats (Reduce).

### Le dataset

Le fichier `purchases.txt` contient **6 colonnes** séparées par des tabulations :

```
date | heure | store (ville) | item (catégorie) | cost (prix) | payment_method
```

### Chargement dans HDFS

```bash
# Copie du fichier local vers le container namenode
docker cp purchases.txt namenode:/workspace/Data/

# Connexion au namenode et chargement dans HDFS
docker exec -it namenode bash
hdfs dfs -put /workspace/Data/purchases.txt /root/input/
```

---

### Question a — Chiffre d'affaires total par item

**Logique :**
- `mapper.py` → extrait la paire `(item, cost)` de chaque ligne
- `reducer.py` → additionne tous les coûts par item

```python
# mapper.py — simplifié
for line in sys.stdin:
    data = line.strip().split("\t")
    if len(data) == 6:
        date, time, store, item, cost, payment = data
        print(f"{item}\t{cost}")

# reducer.py — simplifié
# Additionne les coûts pour chaque item
```

**Résultat :** 4 138 476 enregistrements traités → 18 catégories d'items avec leur CA total.

---

### Question b — Item le plus vendu selon le chiffre d'affaires

**Logique :**
- `mapper.py` → identique à la question a (paire item/cost)
- `reducer_b.py` → garde en mémoire **uniquement** l'item avec le chiffre d'affaires maximal

**Résultat :** Les **DVDs** sont l'item générant le plus grand chiffre d'affaires avec **57 649 212 USD** sur l'ensemble du dataset.

---

### Question c — Moyenne de vente par Store

**Logique :**
- `mapper_c.py` → extrait la paire `(store, cost)`
- `reducer_c.py` → calcule la moyenne des ventes pour chaque store en divisant la somme par le nombre de transactions

**Résultat :** 103 stores avec leur moyenne respective (ex: Albuquerque → 249.15$, Chicago → 250.18$...).

---

### Question d — Item le plus vendu par Store (en nombre de ventes)

**Logique :**
- `mapper_d.py` → extrait le triplet `(store, item, 1)` pour chaque transaction
- `reducer_d.py` → groupe par store, puis par item, et retient l'item ayant le plus grand nombre de ventes pour chaque store

**Résultat :** Pour chacun des 103 stores, on sait quel item est le plus populaire (ex: Albuquerque → Baby, Arlington → Video Games...).

---

### Commande d'exécution type (MapReduce Streaming)

```bash
hadoop jar /opt/hadoop-3.3.5/share/hadoop/tools/lib/hadoop-streaming-3.3.5.jar \
  -D mapreduce.map.memory.mb=512 \
  -D mapreduce.reduce.memory.mb=512 \
  -file /workspace/Code/mapper.py   -mapper mapper.py \
  -file /workspace/Code/reducer.py  -reducer reducer.py \
  -input /root/input/purchases.txt  \
  -output /root/mapredoutput
```

> **Hadoop Streaming** permet d'utiliser des scripts Python comme mapper/reducer au lieu de Java.

---

## ⚡ Partie 3 — Intégration de Spark

### Hadoop MapReduce vs Spark — Quelle différence ?

| | MapReduce | Spark |
|---|---|---|
| **Vitesse** | Lent (écrit sur disque entre chaque étape) | Rapide (travaille en mémoire RAM) |
| **Facilité** | Code verbeux | API plus simple (DataFrames) |
| **Usage** | Batch simple | Analyses complexes, ML, streaming |

Cette partie ajoute un cluster Spark au cluster Hadoop existant, génère des datasets de jeux vidéo, et exécute des analyses PySpark pour calculer 3 KPIs.

---

### Ajout de Spark dans `docker-compose.yml`

Trois services Spark ont été ajoutés : un `spark-master` et deux `spark-workers` (`spark-worker-a` et `spark-worker-b`). Ils partagent le même réseau Docker que Hadoop.

```yaml
spark-master:
  build: spark/
  ports: ["9090:8081", "7077:7077"]
  environment:
    - SPARK_WORKLOAD=master

spark-worker-a:
  build: spark/
  depends_on: [spark-master]
  environment:
    - SPARK_MASTER=spark://spark-master:7077
    - SPARK_WORKER_CORES=1
    - SPARK_WORKER_MEMORY=1G
```

---

### Le dossier `spark/`

Le dossier `spark/` a été créé avec deux fichiers :

**`spark/Dockerfile` :**  
Installe Spark 3.4.3 sur l'image de base Hadoop car Spark n'était pas inclus dans l'image de base initiale.

```dockerfile
FROM hadoop-base:3.3.5-dorian
ENV SPARK_MASTER_PORT=7077
ENV SPARK_MASTER_WEBUI_PORT=8081
# Installation de Spark 3.4.3...
ENTRYPOINT ["/bin/bash", "/start-spark.sh"]
```

**`spark/start-spark.sh` :**  
Script qui démarre soit le master soit un worker selon la variable d'environnement `SPARK_WORKLOAD`.

---

### Génération des datasets

Les datasets ont été générés directement dans le container namenode avec **Python (faker + pandas)**. Les données simulent une plateforme de jeux vidéo.

```python
# generate_data.py — simplifié
from faker import Faker
import pandas as pd

# 50 jeux vidéo
games = [{"GameID": ..., "Genre": random.choice(['MMO','FPS','RPG',...]),
          "Publisher": ..., "Rating": ..., "Game_Length": ...}]

# 100 000 sessions de joueurs
players = [{"PlayerID": ..., "GameID": ..., "Level": ...,
            "ExperiencePoints": ..., "QuestsCompleted": ...,
            "EnemiesDefeated": ..., "CurrencyEarned": ...}]
```

Les deux fichiers CSV sont ensuite chargés dans HDFS :
```bash
hdfs dfs -put /workspace/Data/games_data.csv /root/input/
hdfs dfs -put /workspace/Data/players_data.csv /root/input/
```

---

### Le script PySpark (`spark_job.py`)

Le script PySpark calcule **3 KPIs**. Il est créé dans le container `spark-master` et exécuté avec `spark-submit`.

```bash
spark-submit --master spark://spark-master:7077 /spark_job.py
```

---

### Les 3 KPIs calculés

> **KPI** = Key Performance Indicator = Indicateur Clé de Performance.  
> Ce sont des métriques choisies pour mesurer et analyser le comportement des joueurs sur la plateforme de jeux vidéo.

---

#### 🔧 Structure du script PySpark avant les KPIs

Avant de calculer les KPIs, le script initialise une **SparkSession** et charge les deux fichiers CSV depuis HDFS :

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Initialisation de Spark
spark = SparkSession.builder \
    .appName("spark_project") \
    .getOrCreate()

# Lecture des fichiers CSV stockés dans HDFS
games_df = spark.read.csv(
    "hdfs://namenode:9000/root/input/games_data.csv",
    inferSchema=True,
    header=True
)
activities_df = spark.read.csv(
    "hdfs://namenode:9000/root/input/players_data.csv",
    inferSchema=True,
    header=True
)
```

**Pourquoi lire depuis HDFS et pas depuis le disque local ?**  
Parce que Spark tourne dans un container (`spark-master`) qui n'a pas accès direct aux fichiers locaux. HDFS est le système de fichiers partagé accessible par tous les containers du cluster. C'est le point central de stockage.

**Qu'est-ce que `inferSchema=True` ?**  
Spark détecte automatiquement le type de chaque colonne (entier, décimal, texte...) au lieu de tout lire comme du texte brut. Cela permet d'effectuer des calculs mathématiques directement.

---

#### 📊 KPI 1 — Statistiques moyennes globales par session

##### Objectif
Obtenir une **vue d'ensemble** du comportement moyen d'un joueur sur l'ensemble des 100 000 sessions enregistrées. C'est le KPI le plus simple — il donne une baseline (référence) pour comprendre les autres KPIs.

##### Colonnes utilisées (depuis `players_data.csv`)

| Colonne | Description |
|---|---|
| `ExperiencePoints` | Points d'expérience gagnés pendant la session |
| `QuestsCompleted` | Nombre de quêtes terminées pendant la session |
| `EnemiesDefeated` | Nombre d'ennemis vaincus pendant la session |
| `CurrencyEarned` | Monnaie virtuelle gagnée pendant la session |

##### Code PySpark

```python
session_metrics = activities_df.select(
    F.round(F.mean("ExperiencePoints"), 2).alias("Avg_ExperiencePoints"),
    F.round(F.mean("QuestsCompleted"),  2).alias("Avg_QuestsCompleted"),
    F.round(F.mean("EnemiesDefeated"),  2).alias("Avg_EnemiesDefeated"),
    F.round(F.mean("CurrencyEarned"),   2).alias("Avg_CurrencyEarned"),
)
session_metrics.show()
```

##### Explication ligne par ligne

- `activities_df.select(...)` → on sélectionne uniquement les colonnes qui nous intéressent
- `F.mean("ExperiencePoints")` → calcule la **moyenne** de la colonne `ExperiencePoints` sur toutes les 100 000 lignes
- `F.round(..., 2)` → arrondit le résultat à 2 décimales
- `.alias("Avg_ExperiencePoints")` → renomme la colonne dans le résultat final
- Pas de `groupBy` ici → le calcul est **global**, sur tout le dataset d'un coup

##### Résultat obtenu

| Avg_ExperiencePoints | Avg_QuestsCompleted | Avg_EnemiesDefeated | Avg_CurrencyEarned |
|:---:|:---:|:---:|:---:|
| **5067.61** | **9.97** | **25.08** | **2556.52** |

##### Interprétation
- En moyenne, un joueur gagne **5 067 points d'XP** par session
- Il complète environ **10 quêtes** par session
- Il bat environ **25 ennemis** par session
- Il gagne environ **2 556 unités de monnaie** par session

Ces chiffres servent de **référence** : si un genre de jeu ou un niveau de joueur dépasse ces moyennes, c'est qu'il est plus engageant ou plus difficile.

##### Sauvegarde
```python
session_metrics.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/root/sparkoutput/Session_metrics.parquet"
)
```

---

#### 🎮 KPI 2 — Métriques par genre de jeux

##### Objectif
Comparer les performances des joueurs **selon le genre du jeu** auquel ils jouent (FPS, RPG, MMO...). Ce KPI nécessite une **jointure** entre les deux datasets car :
- `players_data.csv` contient les sessions de jeu (avec `GameID`)
- `games_data.csv` contient les informations sur les jeux (avec `GameID` et `Genre`)

Il faut donc **relier** les deux tables via le `GameID` pour savoir à quel genre appartient chaque session.

##### Schéma de la jointure

```
players_data.csv          games_data.csv
─────────────────         ──────────────────
PlayerID                  GameID  ◄──────────┐
GameID  ──────────────────────────────────────┘
SessionID                 Genre
Level                     Publisher
ExperiencePoints          Rating
QuestsCompleted           Game_Length
EnemiesDefeated
CurrencyEarned
```

##### Code PySpark

```python
game_genre_metrics = activities_df.join(
        games_df,
        on="GameID",
        how="inner"           # Garde uniquement les lignes qui ont un GameID en commun
    ) \
    .groupBy("Genre") \       # Regroupe toutes les sessions par genre de jeu
    .agg(
        F.round(F.mean("QuestsCompleted"),  2).alias("Avg_QuestsCompleted"),
        F.round(F.mean("EnemiesDefeated"),  2).alias("Avg_EnemiesDefeated"),
        F.round(F.mean("Game_Length"),      2).alias("Avg_Game_Length"),
    )
game_genre_metrics.show()
```

##### Explication ligne par ligne

- `.join(games_df, on="GameID", how="inner")` → fusionne les deux DataFrames sur la colonne `GameID`. Chaque ligne de `players_data` reçoit les informations du jeu correspondant (dont le `Genre`)
- `.groupBy("Genre")` → regroupe toutes les sessions par genre. Toutes les sessions de jeux FPS sont regroupées ensemble, toutes les RPG ensemble, etc.
- `.agg(...)` → pour chaque groupe (genre), calcule les agrégations demandées
- `F.mean("QuestsCompleted")` → moyenne des quêtes complétées pour toutes les sessions de ce genre
- `F.mean("Game_Length")` → durée moyenne des jeux de ce genre (vient de `games_data.csv`)

##### Résultat obtenu

| Genre | Avg_QuestsCompleted | Avg_EnemiesDefeated | Avg_Game_Length |
|---|:---:|:---:|:---:|
| **Adventure** | 10.02 | 25.06 | **65.05** |
| **FPS** | 10.02 | 25.23 | **66.4** |
| **MMO** | 9.93 | 25.04 | **43.43** |
| **Strategy** | 10.06 | 25.06 | **48.85** |
| **RPG** | 9.89 | 25.03 | **52.66** |

##### Interprétation
- Les jeux **FPS** et **Adventure** ont les durées moyennes les plus longues (~65-66 heures)
- Les **MMO** sont les plus courts (~43 heures) — probablement parce que les joueurs font des sessions plus courtes mais plus fréquentes
- Le nombre de quêtes et d'ennemis est relativement **homogène** entre les genres (~10 quêtes, ~25 ennemis) — ce qui est logique car les données ont été générées aléatoirement
- En production réelle, ces écarts seraient plus marqués et permettraient d'identifier quels genres retiennent le mieux les joueurs

##### Sauvegarde
```python
game_genre_metrics.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/root/sparkoutput/Games_genre_metrics.parquet"
)
```

---

#### 🏆 KPI 3 — Métriques par niveau de joueur

##### Objectif
Segmenter les joueurs en **3 catégories** selon leur niveau et comparer leurs performances. Cela permet de comprendre si les joueurs avancés sont vraiment plus performants que les débutants, et d'adapter le contenu du jeu en conséquence.

##### La segmentation — `withColumn` + `when`

C'est la partie la plus technique de ce KPI. On crée une **nouvelle colonne** `Level_Group` qui classe chaque joueur selon son niveau :

```python
activities_df2 = activities_df.withColumn(
    "Level_Group",                          # Nom de la nouvelle colonne
    F.when(F.col("Level") < 30, "Beginner")
     .when((F.col("Level") >= 30) & (F.col("Level") < 60), "Mid-Level")
     .when(F.col("Level") >= 60, "Advanced")
     .otherwise("Unknown")
)
```

##### Explication de la segmentation

| Condition | Groupe assigné | Signification |
|---|---|---|
| `Level < 30` | **Beginner** | Joueur débutant, peu expérimenté |
| `30 ≤ Level < 60` | **Mid-Level** | Joueur intermédiaire |
| `Level ≥ 60` | **Advanced** | Joueur expérimenté, maîtrise le jeu |

- `F.withColumn("Level_Group", ...)` → ajoute une nouvelle colonne au DataFrame sans modifier les autres
- `F.when(condition, valeur)` → équivalent d'un `IF` en SQL ou d'un `if/elif/else` en Python, mais appliqué sur toutes les lignes en parallèle
- `.otherwise("Unknown")` → valeur par défaut si aucune condition n'est vérifiée (sécurité)

##### Code PySpark complet

```python
player_level_metrics = activities_df2.groupBy("Level_Group") \
    .agg(
        F.round(F.mean("EnemiesDefeated"),  2).alias("Avg_EnemiesDefeated"),
        F.round(F.mean("QuestsCompleted"),  2).alias("Avg_QuestsCompleted"),
    )
player_level_metrics.show()
```

- `.groupBy("Level_Group")` → regroupe les sessions par catégorie de joueur (Beginner / Mid-Level / Advanced)
- `.agg(...)` → calcule les moyennes pour chaque groupe

##### Résultat obtenu

| Level_Group | Avg_EnemiesDefeated | Avg_QuestsCompleted |
|---|:---:|:---:|
| **Advanced** | 25.11 | 9.94 |
| **Mid-Level** | 25.07 | 10.03 |
| **Beginner** | 25.06 | 9.96 |

##### Interprétation
- Les différences entre les groupes sont **très faibles** (~0.05 d'écart) — ce qui est attendu car les données ont été générées aléatoirement avec `random.randint`
- Dans un vrai jeu, on s'attendrait à ce que les joueurs **Advanced** battent beaucoup plus d'ennemis et complètent plus de quêtes que les **Beginners**
- Ce KPI est néanmoins utile en production pour : détecter si les débutants abandonnent trop tôt, ajuster la difficulté par niveau, personnaliser les recommandations de contenu

##### Sauvegarde
```python
player_level_metrics.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/root/sparkoutput/Player_level_metrics.parquet"
)
```

---

#### 📁 Pourquoi sauvegarder en Parquet ?

À la fin du script, les 3 résultats sont sauvegardés en format **Parquet** dans HDFS :

```python
print("=== Sauvegarde dans HDFS ===")
session_metrics.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/root/sparkoutput/Session_metrics.parquet")
game_genre_metrics.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/root/sparkoutput/Games_genre_metrics.parquet")
player_level_metrics.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/root/sparkoutput/Player_level_metrics.parquet")

print("DONE! Tous les fichiers sauvegardés dans HDFS")
spark.stop()
```

**Parquet vs CSV — pourquoi Parquet ?**

| Critère | CSV | Parquet |
|---|---|---|
| **Stockage** | Texte brut, volumineux | Binaire compressé, 5-10x plus petit |
| **Lecture** | Lit toutes les colonnes | Lit uniquement les colonnes nécessaires |
| **Types** | Tout est texte | Préserve les types (int, float, date...) |
| **Performance** | Lent sur gros volumes | Optimisé pour les analyses Big Data |
| **Usage** | Échange de données simple | Stockage analytique en production |

> En résumé : Parquet est le format standard de l'industrie Big Data pour stocker des résultats d'analyses. Il est utilisé par Spark, Hive, Presto, et tous les outils modernes de data engineering.

---

#### 🔄 Flux complet des données pour les KPIs

```
HDFS (/root/input/)
    │
    ├── games_data.csv (50 jeux)
    │       └──────────────────────────────────┐
    │                                          │ JOIN sur GameID
    └── players_data.csv (100 000 sessions)    │
            │                                  │
            ├── KPI 1 ──── select + mean ──────┤ (pas de jointure)
            │                                  │
            ├── KPI 2 ──── join + groupBy ─────┘ (avec games_data)
            │              + agg(mean)
            │
            └── KPI 3 ──── withColumn (segmentation Level)
                           + groupBy + agg(mean)

                                    │
                                    ▼
                        HDFS (/root/sparkoutput/)
                            ├── Session_metrics.parquet
                            ├── Games_genre_metrics.parquet
                            └── Player_level_metrics.parquet
```

---

### Sauvegarde en Parquet dans HDFS

Les résultats sont sauvegardés en format **Parquet** — un format colonnaire optimisé pour les analyses Big Data (compression efficace, lecture rapide).

```python
session_metrics.write.mode("overwrite").parquet("hdfs://namenode:9000/root/sparkoutput/Session_metrics.parquet")
game_genre_metrics.write.mode("overwrite").parquet("hdfs://namenode:9000/root/sparkoutput/Games_genre_metrics.parquet")
player_level_metrics.write.mode("overwrite").parquet("hdfs://namenode:9000/root/sparkoutput/Player_level_metrics.parquet")
```

Vérification dans HDFS :
```bash
hdfs dfs -ls /root/sparkoutput/
# Found 3 items
# /root/sparkoutput/Games_genre_metrics.parquet
# /root/sparkoutput/Player_level_metrics.parquet
# /root/sparkoutput/Session_metrics.parquet
```

---

## 📋 Récapitulatif complet

Toutes les parties du projet ont été réalisées avec succès :

| Partie | Description | Statut |
|---|---|---|
| **1 - Cluster Hadoop** | 6 services Docker (Namenode, 2 Datanodes, RM, NM, HS) | ✅ Terminé |
| **2a - MapReduce** | CA total par item — 18 catégories calculées | ✅ Terminé |
| **2b - MapReduce** | Item le plus vendu — DVDs: 57 649 212 USD | ✅ Terminé |
| **2c - MapReduce** | Moyenne de vente par store — 103 stores | ✅ Terminé |
| **2d - MapReduce** | Item le plus vendu par store — 103 stores | ✅ Terminé |
| **3 - Cluster Spark** | spark-master + spark-worker-a + spark-worker-b | ✅ Terminé |
| **3 - KPI 1** | Statistiques par session (XP, quêtes, ennemis) | ✅ Terminé |
| **3 - KPI 2** | Métriques par genre de jeux (jointure games+players) | ✅ Terminé |
| **3 - KPI 3** | Métriques par niveau de joueur (Beginner/Mid/Advanced) | ✅ Terminé |

**Technologies utilisées :**  
Docker · Hadoop 3.3.5 · HDFS · YARN · MapReduce Streaming Python · Spark 3.4.3 · PySpark · Python 3 · Faker · Pandas · Parquet

---

## 💡 Points clés à retenir pour l'oral

1. **Docker** simule un vrai cluster distribué sur une seule machine
2. **HDFS** stocke les données en blocs répliqués sur plusieurs Datanodes → tolérance aux pannes
3. **YARN** gère les ressources et orchestre l'exécution des jobs
4. **MapReduce** traite les données en deux phases : Map (extraction) → Reduce (agrégation)
5. **Spark** est plus rapide que MapReduce car il travaille en **mémoire RAM**
6. L'architecture en **image de base commune** évite la duplication et facilite la maintenance
7. Le format **Parquet** est optimal pour stocker les résultats d'analyses Big Data

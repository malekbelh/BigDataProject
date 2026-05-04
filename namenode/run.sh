#!/bin/bash

# Formater le namenode si c'est la premiere fois
if [ ! -d "/hadoop/dfs/name/current" ]; then
    hdfs namenode -format
fi

# Demarrer le namenode
hdfs namenode
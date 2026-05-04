#!/bin/bash

: ${HADOOP_HOME:=/opt/hadoop-3.3.5}

$HADOOP_HOME/etc/hadoop/hadoop-env.sh

. $HADOOP_HOME/etc/hadoop/hadoop-env.sh

if [ "$MULTIHOMED_NETWORK" = "1" ]; then
    export HADOOP_OPTS="$HADOOP_OPTS -Dhadoop.security.token.service.useIp=false"
fi

exec $@
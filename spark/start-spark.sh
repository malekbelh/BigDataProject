#!/bin/bash
if [ "$SPARK_WORKLOAD" = "master" ]; then
    $SPARK_HOME/sbin/start-master.sh -h spark-master
    tail -f $SPARK_HOME/logs/*.out
elif [ "$SPARK_WORKLOAD" = "worker" ]; then
    sleep 10
    $SPARK_HOME/sbin/start-worker.sh spark://spark-master:7077
    tail -f $SPARK_HOME/logs/*.out
fi

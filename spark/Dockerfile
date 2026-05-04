FROM hadoop-base:3.3.5-dorian

RUN chmod -R 755 /opt/hadoop-3.3.5/etc/hadoop/

RUN wget -q https://archive.apache.org/dist/spark/spark-3.4.3/spark-3.4.3-bin-hadoop3.tgz \
    && tar -xzf spark-3.4.3-bin-hadoop3.tgz -C /opt/ \
    && rm spark-3.4.3-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark-3.4.3-bin-hadoop3
ENV PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
ENV SPARK_MASTER_PORT=7077
ENV SPARK_MASTER_WEBUI_PORT=8081
ENV SPARK_WORKER_PORT=7000
ENV SPARK_WORKLOAD=master
ENV PYSPARK_PYTHON=python3

COPY start-spark.sh /start-spark.sh
RUN sed -i 's/\r//' /start-spark.sh && chmod +x /start-spark.sh

ENTRYPOINT ["/bin/bash", "/start-spark.sh"]

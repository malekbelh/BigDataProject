FROM debian:11

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    netcat \
    curl \
    gnupg \
    wget

RUN apt-get install -y python3 python3-setuptools python3-pip

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/

ENV HADOOP_VERSION 3.3.5
ENV HADOOP_URL https://www.apache.org/dist/hadoop/common/hadoop-3.3.5/hadoop-3.3.5.tar.gz

RUN curl -O https://dist.apache.org/repos/dist/release/hadoop/common/KEYS
RUN gpg --import KEYS

RUN set -x \
    && curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz \
    && tar -xvf /tmp/hadoop.tar.gz -C /opt/ \
    && rm /tmp/hadoop.tar.gz*

RUN ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop
RUN mkdir /opt/hadoop-$HADOOP_VERSION/logs
RUN mkdir /hadoop-data

ENV HADOOP_HOME=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV PATH $HADOOP_HOME/bin/:$PATH

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

COPY conf/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY conf/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY conf/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
COPY conf/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml
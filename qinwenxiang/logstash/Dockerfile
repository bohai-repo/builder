FROM ubuntu:22.04

# 设置环境变量
ENV CATALINA_HOME /apps/tomcat
ENV PATH $CATALINA_HOME/bin:$PATH

# 安装必要的软件包
RUN apt-get update \
    && apt-get clean \
    && apt-get install -y \
       curl wget openjdk-8-jdk \
    && rm -rf /var/lib/apt/lists/* \
    && useradd tomcat

# 下载并安装Tomcat 8.5.43
ADD apache-tomcat-8.5.88.tar.gz /apps/
RUN mv /apps/apache-tomcat-8.5.88 /apps/tomcat

RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.12.1-linux-x86_64.tar.gz && \
    tar -zxvf filebeat-7.12.1-linux-x86_64.tar.gz && \
    rm filebeat-7.12.1-linux-x86_64.tar.gz && \
    mv filebeat-7.12.1-linux-x86_64 /etc/filebeat/

# 复制配置文件到/apps/tomcat/目录下
ADD catalina.sh /apps/tomcat/bin/catalina.sh
ADD server.xml /apps/tomcat/conf/server.xml
ADD run_tomcat.sh /apps/tomcat/bin/run_tomcat.sh
ADD filebeat.yml /etc/filebeat/filebeat.yml
ADD myapp.tar.gz /data/tomcat/webapps/myapp/
RUN chown -R tomcat.tomcat /data/ /apps/ \
    && chmod +x /apps/tomcat/bin/run_tomcat.sh

# 开放Tomcat的HTTP端口
EXPOSE 8080

# 启动Tomcat
CMD ["/apps/tomcat/bin/run_tomcat.sh"]
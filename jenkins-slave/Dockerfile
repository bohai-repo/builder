FROM jenkins/agent:3107.v665000b_51092-15-jdk17

ARG user=jenkins
ARG AGENT_WORKDIR=/home/${user}/agent

ENV AGENT_WORKDIR=${AGENT_WORKDIR}
RUN mkdir -p /home/${user}/.jenkins && mkdir -p ${AGENT_WORKDIR}

VOLUME /home/${user}/.jenkins
VOLUME ${AGENT_WORKDIR}
WORKDIR /home/${user}

USER root
COPY jenkins-agent /usr/local/bin/jenkins-agent 

RUN chmod +x /usr/local/bin/jenkins-agent \
    && ln -s /usr/local/bin/jenkins-agent /usr/local/bin/jenkins-slave

ENTRYPOINT ["/usr/local/bin/jenkins-agent"]
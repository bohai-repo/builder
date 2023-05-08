FROM debian:buster-slim

ENV GITHUB_PAT ""
ENV GITHUB_TOKEN ""
ENV GITHUB_OWNER ""
ENV GITHUB_REPOSITORY ""
ENV RUNNER_WORKDIR "_work"
ENV RUNNER_LABELS ""
ENV ADDITIONAL_PACKAGES ""

USER root
WORKDIR /root

RUN apt-get update \
    && apt-get install -y \
        curl \
        sudo \
        git \
        jq \
        iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl https://download.docker.com/linux/static/stable/aarch64/docker-docker_version.tgz --output docker-docker_version.tgz \
    && tar xvfz docker-docker_version.tgz \
    && cp docker/* /usr/bin/ \
    && rm -rf docker-docker_version.tgz

ADD actions-runner-linux-arm64-version_key.tar.gz /root
RUN sudo ./bin/installdependencies.sh

COPY entrypoint.sh runsvc.sh ./
RUN sudo chmod u+x ./entrypoint.sh ./runsvc.sh

ENTRYPOINT ["./entrypoint.sh"]

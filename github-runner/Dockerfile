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

COPY entrypoint.sh runsvc.sh ./
ADD docker.tar.gz /usr/bin/
ADD actions-runner-linux-version_key.tar.gz /root

RUN apt-get update \
    && apt-get install -y curl sudo git jq iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && sudo chmod u+x ./entrypoint.sh ./runsvc.sh \
    && sudo ./bin/installdependencies.sh

ENTRYPOINT ["./entrypoint.sh"]
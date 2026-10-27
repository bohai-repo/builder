FROM ubuntu:24.04 AS build

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_ENV=production \
    DSH_HOME=/root/.dsh \
    DSH_TELEMETRY_DISABLED=1 \
    npm_config_audit=false \
    npm_config_fund=false \
    npm_config_update_notifier=false

ARG NODE_VERSION=24.11.1
ARG DSH_VERSION=0.2.1-rc.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      xz-utils \
    && ARCH="$(dpkg --print-architecture)" \
    && case "$ARCH" in \
         amd64) NODE_ARCH=x64 ;; \
         arm64) NODE_ARCH=arm64 ;; \
         *) echo "unsupported arch: $ARCH" >&2; exit 1 ;; \
       esac \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz" \
         | tar -xJ -C /usr/local --strip-components=1 \
    && npm install -g pnpm "@deepseek-ai/dsh@${DSH_VERSION}" --omit=dev \
    && rm -rf /var/lib/apt/lists/* /root/.npm /tmp/*

COPY dsh/plugins.txt /opt/dsh-web/plugins.txt
COPY scripts/bake-profile-web.sh /opt/dsh-web/bake-profile-web.sh
RUN chmod +x /opt/dsh-web/bake-profile-web.sh \
    && mkdir -p /root/.dsh \
    && /opt/dsh-web/bake-profile-web.sh \
    && rm -rf \
         /root/.dsh/profiles \
         /root/.local \
         /root/.npm \
         /root/.cache \
         /tmp/* \
         /usr/local/lib/node_modules/pnpm \
         /usr/local/bin/pnpm /usr/local/bin/pnpx

# --- runtime：精简工具 + 拷贝已烤好的 profile / dsh ---
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_ENV=production \
    DSH_HOME=/root/.dsh \
    DSH_TELEMETRY_DISABLED=1 \
    npm_config_update_notifier=false

ARG NODE_VERSION=24.11.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      bash \
      ca-certificates \
      curl \
      git \
      iproute2 \
      jq \
      openssh-client \
      procps \
      python3 \
      tar \
      xz-utils \
    && ARCH="$(dpkg --print-architecture)" \
    && case "$ARCH" in \
         amd64) NODE_ARCH=x64 ;; \
         arm64) NODE_ARCH=arm64 ;; \
         *) echo "unsupported arch: $ARCH" >&2; exit 1 ;; \
       esac \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz" \
         | tar -xJ -C /usr/local --strip-components=1 \
    && rm -rf /var/lib/apt/lists/* /usr/local/CHANGELOG* /usr/local/README* /usr/local/*.md /tmp/*

WORKDIR /root

COPY --from=build /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sfn /usr/local/lib/node_modules/@deepseek-ai/dsh/lib/bin.js /usr/local/bin/dsh
COPY --from=build /opt/dsh-web/profile-web /opt/dsh-web/profile-web

COPY dsh/cordis.patch.yml /opt/dsh-web/cordis.patch.yml
COPY scripts/entrypoint.sh scripts/dsh-restart scripts/sync-provider.sh /opt/dsh-web/
RUN chmod +x /opt/dsh-web/entrypoint.sh /opt/dsh-web/dsh-restart /opt/dsh-web/sync-provider.sh \
    && mkdir -p /root/.dsh /root \
    && ln -s /opt/dsh-web/dsh-restart /usr/local/bin/dsh-restart \
    && npm cache clean --force \
    && rm -rf /root/.npm /tmp/*

EXPOSE 3080

ENTRYPOINT ["/opt/dsh-web/entrypoint.sh"]
CMD ["--port", "3080"]

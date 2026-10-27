FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_ENV=production \
    DSH_HOME=/root/.dsh \
    DSH_TELEMETRY_DISABLED=1

# 通用基础工具 + Node 24（官方二进制包）
ARG NODE_VERSION=24.11.1
ARG DSH_VERSION=0.2.1-rc.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      bash \
      ca-certificates \
      curl \
      dnsutils \
      git \
      gzip \
      iproute2 \
      iputils-ping \
      jq \
      less \
      netcat-openbsd \
      openssh-client \
      procps \
      python3 \
      tar \
      unzip \
      vim-tiny \
      wget \
      xz-utils \
    && ARCH="$(dpkg --print-architecture)" \
    && case "$ARCH" in \
         amd64) NODE_ARCH=x64 ;; \
         arm64) NODE_ARCH=arm64 ;; \
         *) echo "unsupported arch: $ARCH" >&2; exit 1 ;; \
       esac \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz" \
         | tar -xJ -C /usr/local --strip-components=1 \
    && node -v && npm -v \
    && npm install -g pnpm \
    && pnpm -v \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN npm install --global @deepseek-ai/dsh@${DSH_VERSION} --omit=dev \
    && npm cache clean --force

# cordis patch + 插件清单；构建时 bake 进 /opt/dsh-web/profile-web
COPY dsh/cordis.patch.yml /opt/dsh-web/cordis.patch.yml
COPY dsh/plugins.txt /opt/dsh-web/plugins.txt
COPY scripts/entrypoint.sh scripts/dsh-restart scripts/sync-provider.sh scripts/bake-profile-web.sh /opt/dsh-web/
RUN chmod +x /opt/dsh-web/entrypoint.sh /opt/dsh-web/dsh-restart \
      /opt/dsh-web/sync-provider.sh /opt/dsh-web/bake-profile-web.sh \
    && mkdir -p /root/.dsh /root \
    && /opt/dsh-web/bake-profile-web.sh \
    && ln -s /opt/dsh-web/dsh-restart /usr/local/bin/dsh-restart

EXPOSE 3080

ENTRYPOINT ["/opt/dsh-web/entrypoint.sh"]
CMD ["--port", "3080"]

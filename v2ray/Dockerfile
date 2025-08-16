FROM alpine:latest as openssl-builder
ARG OPENSSL_VERSION="1.1.1w"
RUN apk add --no-cache perl linux-headers make
WORKDIR /build
RUN wget -q https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz \
    && tar xzf openssl-${OPENSSL_VERSION}.tar.gz \
    && cd openssl-${OPENSSL_VERSION} \
    && ./config --prefix=/opt/openssl --openssldir=/opt/openssl no-shared enable-tls1_3 \
    && make -j$(nproc) \
    && make install_sw

FROM alpine:latest as nginx-builder
ARG NGINX_VERSION="1.29.1"
ARG NGINX_ACME_VERSION="0.1.1"
COPY --from=openssl-builder /opt/openssl /opt/openssl

RUN apk add --no-cache \
    build-base pcre2-dev zlib-dev linux-headers \
    curl gd-dev jq perl-dev make

WORKDIR /build
RUN wget -q https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && wget -q https://github.com/nginx/nginx-acme/releases/download/v${NGINX_ACME_VERSION}/nginx-acme-${NGINX_ACME_VERSION}.tar.gz \
    && tar xzf nginx-acme-${NGINX_ACME_VERSION}.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz

RUN cd nginx-${NGINX_VERSION} \
    && ./configure \
        --prefix=/etc/nginx \
        --with-http_ssl_module \
        --with-http_v2_module \
        --with-http_gzip_static_module \
        --with-http_stub_status_module \
        --with-http_sub_module \
        --with-stream \
        --with-stream_ssl_module \
        --with-compat \
        --with-openssl=/opt/openssl \
        --with-openssl-opt='enable-tls1_3' \
        --add-dynamic-module=../nginx-acme-${NGINX_ACME_VERSION} \
        --with-cc-opt="-I/opt/openssl/include" \
        --with-ld-opt="-L/opt/openssl/lib -Wl,-rpath,/opt/openssl/lib" \
    && make -j$(nproc) \
    && make install

FROM alpine:latest
ARG NGINX_VERSION="1.29.1"
ARG V2RAY_CORE_VERSION="4.27.5"
ARG V2RAY_EXPORTER_VERSION="0.0.6"

ENV v2ray_uuid='39c84eb5-6a2b-42d3-ac13-6381a4cca529'
ENV v2ray_path='68ad'
ENV v2ray_port='443'
ENV v2ray_email='demo@gmail.com'
ENV v2ray_domain=''
ENV V2RAY_VMESS_AEAD_FORCED=false

COPY --from=openssl-builder /opt/openssl /opt/openssl
COPY --from=nginx-builder /etc/nginx /etc/nginx

ENV LD_LIBRARY_PATH="/opt/openssl/lib:${LD_LIBRARY_PATH}"
ENV PATH="/etc/nginx/sbin:${PATH}"

RUN apk add --no-cache \
    pcre2 zlib libgcc curl jq tzdata \
    && ln -s /etc/nginx/sbin/nginx /usr/sbin/nginx \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /app/v2ray && cd /app/v2ray \
    && if [ "$(uname -m)" = "x86_64" ]; then export V2RAY_CORE_CPU_PLATFORM="64";export V2RAY_EXPORTER_CPU_PLATFORM="amd64"; elif [ "$(uname -m)" = "aarch64" ]; then export V2RAY_CORE_CPU_PLATFORM="arm64-v8a";export V2RAY_EXPORTER_CPU_PLATFORM="arm64"; else echo "ERROR: Unsupported architecture: $(uname -m)"; exit 1; fi \
    && wget --no-check-certificate -q https://github.com/v2fly/v2ray-core/releases/download/v${V2RAY_CORE_VERSION}/v2ray-linux-${V2RAY_CORE_CPU_PLATFORM}.zip \
    && unzip -q v2ray-linux-${V2RAY_CORE_CPU_PLATFORM}.zip \
    && wget --no-check-certificate -q -O v2ray-exporter https://github.com/wi1dcard/v2ray-exporter/releases/download/v${V2RAY_EXPORTER_VERSION}/v2ray-exporter_linux_${V2RAY_EXPORTER_CPU_PLATFORM} \
    && chmod +x v2ray-exporter \
    && rm -rf \
        vpoint* \
        *.sig \
        *.dat \
        *.zip \
        systemd

COPY entrypoint.sh /app/entrypoint.sh
COPY index.html /etc/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf/nginx.conf
COPY config.json /app/v2ray/config.json

WORKDIR /app
EXPOSE 443 8443
RUN chmod +x /app/entrypoint.sh

RUN echo "load_module /etc/nginx/modules/ngx_http_acme_module.so;" > /etc/nginx/conf.d/acme.conf
CMD ["/app/entrypoint.sh"]
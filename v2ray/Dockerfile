FROM alpine:latest

ARG BUILD_CPU_NUM="2"
ARG NGINX_VERSION="1.21.1"
ARG V2RAY_CORE_VERSION="4.27.5"
ARG V2RAY_EXPORTER_VERSION="0.6.0"

ENV v2ray_uuid='39c84eb5-6a2b-42d3-ac13-6381a4cca529'
ENV v2ray_path='68ad'
ENV v2ray_port='443'
ENV v2ray_email='demo@gmail.com'
ENV v2ray_domain=''
ENV V2RAY_VMESS_AEAD_FORCED=false

USER root
WORKDIR /app

EXPOSE 443
EXPOSE 8443

COPY entrypoint.sh entrypoint.sh
COPY index.html  /etc/nginx/html/index.html
COPY nginx.conf  /etc/nginx/conf/nginx.conf

RUN apk add --no-cache gcc libc-dev \
    make openssl-dev linux-headers \
    pcre-dev zlib-dev perl-dev \
    curl gd-dev jq \
    && wget -q https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && wget -q 'https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1a/openssl-1.1.1a.tar.gz' \
    && tar xzf openssl-1.1.1a.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz && cd nginx-${NGINX_VERSION} \
    && ./configure --prefix=/etc/nginx \
       --with-openssl=../openssl-1.1.1a \
       --with-openssl-opt='enable-tls1_3' \
       --with-http_v2_module --with-http_ssl_module \
       --with-http_gzip_static_module --with-http_stub_status_module \
       --with-http_sub_module --with-stream --with-stream_ssl_module \
    && make -j${BUILD_CPU_NUM} && make -j${BUILD_CPU_NUM} install \
    && ln -s /etc/nginx/sbin/nginx /usr/sbin/ \
    && cd /app/v2ray \
    && if [ "$(uname -m)" = "x86_64" ]; then export V2RAY_CORE_CPU_PLATFORM="64";export V2RAY_EXPORTER_CPU_PLATFORM="amd64"; elif [ "$(uname -m)" = "aarch64" ]; then export V2RAY_CORE_CPU_PLATFORM="arm64-v8a";export V2RAY_EXPORTER_CPU_PLATFORM="arm64"; else echo "ERROR: Unsupported architecture: $(uname -m)"; exit 1; fi \
	&& wget --no-check-certificate -q https://github.com/v2ray/v2ray-core/releases/download/v${V2RAY_CORE_VERSION}/v2ray-linux-${V2RAY_CORE_CPU_PLATFORM}.zip \
    && unzip -q v2ray-linux-${V2RAY_CORE_CPU_PLATFORM}.zip \
    && wget --no-check-certificate -q -O v2ray-exporter https://github.com/wi1dcard/v2ray-exporter/releases/download/v${V2RAY_EXPORTER_VERSION}/v2ray-exporter_linux_${V2RAY_EXPORTER_CPU_PLATFORM} \
    && chmod +x v2ray-exporter /app/entrypoint.sh \
    && rm -rf \
        /app/openssl-1.1.1a* \
        /var/cache/apk/* \
        /app/nginx-${NGINX_VERSION}* \
        /app/v2ray/vpoint* \
        /app/v2ray/*.sig \
        /app/v2ray/*.dat \
        /app/v2ray/*.zip \
        /app/v2ray/systemd

COPY config.json /app/v2ray/config.json

CMD /app/entrypoint.sh
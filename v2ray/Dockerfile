FROM alpine:latest

ARG V2RAY_VERSION="4.27.5"
ARG NGINX_VERSION="1.21.1"

ENV v2ray_uuid '39c84eb5-6a2b-42d3-ac13-6381a4cca529'
ENV v2ray_path '68ad'
ENV v2ray_port '443'
ENV v2ray_email 'demo@gmail.com'
ENV v2ray_domain ''
ENV V2RAY_VMESS_AEAD_FORCED false

USER root
WORKDIR /app

ADD entrypoint.sh entrypoint.sh

RUN apk add --no-cache gcc libc-dev \
    make openssl-dev linux-headers \
    pcre-dev zlib-dev perl-dev \
    curl gd-dev jq

# Nginx
RUN wget 'https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz' \
    && wget 'https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1a/openssl-1.1.1a.tar.gz' \
    && tar xzf openssl-1.1.1a.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz && cd nginx-${NGINX_VERSION} \
    && ./configure --prefix=/etc/nginx \
       --with-openssl=../openssl-1.1.1a \
       --with-openssl-opt='enable-tls1_3' \
       --with-http_v2_module --with-http_ssl_module \
       --with-http_gzip_static_module --with-http_stub_status_module \
       --with-http_sub_module --with-stream --with-stream_ssl_module \
    && make && make install \
    && rm -rf /etc/nginx/html/* \
    && rm -rf /app/openssl-1.1.1a* \
    && rm -rf /var/cache/apk/* \
    && rm -rf /app/nginx-${NGINX_VERSION}* \
    && ln -s /etc/nginx/sbin/nginx /usr/sbin/

# V2ray
RUN mkdir /app/v2ray && cd $_ \
    if [ "$(uname -m)" = "x86_64" ]; then export CPU_PLATFORM="64" ; elif [ "$(uname -m)" = "aarch64" ]; then export CPU_PLATFORM="arm64-v8a" ; fi \
	&& wget --no-check-certificate https://github.com/v2ray/v2ray-core/releases/download/v${V2RAY_VERSION}/v2ray-linux-${CPU_PLATFORM}.zip \
    && unzip v2ray-linux-${CPU_PLATFORM}.zip \
    && rm -rf *.{json,sig,dat,systemd} \
    && chmod +x /app/v2ray/* \
    && chmod +x /app/entrypoint.sh

ADD v2ray_web.tar.gz /etc/nginx/html/
ADD nginx.conf   /etc/nginx/conf/nginx.conf
ADD config.json  /app/v2ray/config.json

CMD /app/entrypoint.sh
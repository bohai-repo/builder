FROM alpine:latest

ENV v2ray_uuid ''
ENV v2ray_path ''
ENV v2ray_email ''
ENV v2ray_domain ''
ENV v2ray_version ''
ENV V2RAY_VMESS_AEAD_FORCED false

USER root
WORKDIR /app
ADD entrypoint.sh entrypoint.sh

RUN apk add --no-cache gcc libc-dev \
    make openssl-dev linux-headers \
    pcre-dev zlib-dev perl-dev \
    curl gd-dev

RUN wget 'http://nginx.org/download/nginx-1.21.1.tar.gz' \
    && wget 'https://file.init.ac/openssl-1.1.1a.tar.gz' \
    && tar xzf openssl-1.1.1a.tar.gz \
    && tar zxf nginx-1.21.1.tar.gz && cd nginx-1.21.1 \
    && ./configure --prefix=/etc/nginx \
       --with-openssl=../openssl-1.1.1a \
       --with-openssl-opt='enable-tls1_3' \
       --with-http_v2_module --with-http_ssl_module \
       --with-http_gzip_static_module --with-http_stub_status_module \
       --with-http_sub_module --with-stream --with-stream_ssl_module \
    && make && make install \
    && rm -rf /etc/nginx/html/index.html && wget 'https://file.init.ac/v2ray-web.zip' && unzip -d /etc/nginx/html v2ray-web.zip \
    && rm -rf /app/openssl-1.1.1a* \
    && rm -rf v2ray-web.zip \
    && rm -rf /var/cache/apk/* \
    && rm -rf /app/nginx-1.21.1* \
    && ln -s /etc/nginx/sbin/nginx /usr/sbin/ \
    && mkdir /app/v2ray && cd $_ \
    && curl -o /app/v2ray/v2ray https://file.init.ac/v2ray-amd64-4.45.0 \
    && chmod +x /app/v2ray/v2ray \
    && chmod +x /app/entrypoint.sh

ADD nginx.conf   /etc/nginx/conf/nginx.conf
ADD config.json  /app/v2ray/config.json

CMD /app/entrypoint.sh
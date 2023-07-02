FROM alpine:latest
  
USER root
WORKDIR /app

EXPOSE 80
EXPOSE 443

RUN apk add --no-cache gcc libc-dev \
    make openssl-dev linux-headers \
    pcre-dev zlib-dev perl-dev \
    curl gd-dev \
    && wget 'http://nginx.org/download/nginx-1.21.1.tar.gz' \
    && wget 'https://file.init.ac/openssl-1.1.1a.tar.gz' \
    && tar xzf openssl-1.1.1a.tar.gz \
    && tar zxf nginx-1.21.1.tar.gz && cd nginx-1.21.1 \
    && ./configure --prefix=/app/nginx \
       --with-openssl=../openssl-1.1.1a \
       --with-openssl-opt='enable-tls1_3' \
       --with-http_v2_module --with-http_ssl_module \
       --with-http_gzip_static_module --with-http_stub_status_module \
       --with-http_sub_module --with-stream --with-stream_ssl_module \
    && make && make install \
    && rm -rf /app/openssl-1.1.1a* \
    && rm -rf /var/cache/apk/* \
    && rm -rf /app/nginx-1.21.1* \
    && ln -s /app/nginx/sbin/nginx /usr/sbin/

ADD nginx.conf  /app/nginx/conf/nginx.conf

CMD ["nginx" "-g" "daemon off;"]
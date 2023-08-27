FROM php:7.2-apache

ENV VIRTUAL_HOST site.local
ENV UPSTREAM_NAME web-site

RUN apt-get update
RUN apt-get install -y \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        libxslt-dev \
    && docker-php-ext-install -j$(nproc) iconv \
    && docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ \
    && docker-php-ext-install -j$(nproc) gd \
    && docker-php-ext-install mysqli pdo pdo_mysql xsl

# RUN pecl install xdebug
# RUN docker-php-ext-enable xdebug
# RUN echo ';xdebug.scream=1' >> cxdebug.ini \
#     && echo 'xdebug.remote_enable=1' >> /usr/local/etc/php/conf.d/xdebug.ini \
#     && echo 'xdebug.remote_autostart=1' >> /usr/local/etc/php/conf.d/xdebug.ini \
#     && echo 'xdebug.remote_connect_back=1' >> /usr/local/etc/php/conf.d/xdebug.ini \
#     && echo 'xdebug.remote_port=9000' >> /usr/local/etc/php/conf.d/xdebug.ini \
#     && echo 'xdebug.remote_mode=req' >> /usr/local/etc/php/conf.d/xdebug.ini \
#     && echo 'xdebug.remote_handler=dbgp' >> /usr/local/etc/php/conf.d/xdebug.ini \
#     && echo 'xdebug.remote_log=/tmp/php5-xdebug.log' >> /usr/local/etc/php/conf.d/xdebug.ini

RUN a2enmod rewrite

EXPOSE 80
# EXPOSE 9000

VOLUME /var/www/html/
COPY conf.d/php.ini /usr/local/etc/php/
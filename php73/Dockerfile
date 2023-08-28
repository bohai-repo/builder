FROM alpine:3.7

ENV PHP_VERSION=7.3.29 PHP_DIR=/usr/local/php/ PATH=$PATH:/usr/local/php/bin/:/usr/local/php/sbin/ TZ=Asia/Shanghai LANG=C.UTF-8

# RUN  sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
# RUN  sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN  CONFIG="\
		--prefix=/usr/local/php \
		--with-config-file-path=/usr/local/php/etc \
		--with-gd \
		--with-mysqli \
		--with-pdo-mysql  \
		--with-libxml-dir \
		--with-png-dir \
		--with-jpeg-dir \
		--with-zlib \
		--with-freetype-dir \
		--with-bz2 \
		--with-curl \
		--with-openssl \
		--with-mhash \
		--with-gettext \
		--with-xmlrpc \
		--enable-soap \
		--enable-mbstring=all \
		--enable-sockets \
		--enable-shared \
		--enable-zip \
		--enable-xml \
		--enable-fpm \
		--enable-inline-optimization \
		--enable-pcntl \
		--enable-bcmath \
		--enable-calendar \
		--with-mysqli=mysqlnd \
		--with-pdo-mysql=mysqlnd \
		--enable-shmop \
		--enable-sysvsem \
		--enable-mbregex \
		--enable-short-tags \
		--enable-intl \
		--enable-ftp \
		--enable-intl \
		--with-gdbm \
		--with-gmp \
		--with-iconv=/usr/local/libiconv/ \
	" \
	&& apk add  --no-cache --virtual mypacks \
		autoconf \	
		file \
		g++ \
		gcc \
		make \
		pkgconf \
		re2c \
		coreutils \
	&& apk add --no-cache \	
		libc-dev \
		dpkg \
		dpkg-dev \
		curl-dev \
		libedit-dev \
		libxml2-dev \
		libressl-dev \
		sqlite-dev \
		gettext-dev \
		bzip2-dev \
		jpeg-dev \
		libpng-dev \
		freetype-dev \
		libmcrypt-dev \
		tzdata \
		bash \
		gmp-dev \
		gdbm-dev \
		icu-dev \
	&& wget -c --tries=0 --no-check-certificate https://www.php.net/distributions/php-7.3.29.tar.gz -O /tmp/php-7.3.29.tar.gz \
	&& wget -c --tries=0 --no-check-certificate https://pecl.php.net/get/redis-4.2.0.tgz -O /tmp/redis-4.2.0.tgz \
	&& wget -c --tries=0 --no-check-certificate http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.15.tar.gz -O /tmp/libiconv-1.15.tar.gz \
	&& wget -c --tries=0 --no-check-certificate https://file.init.ac/libzip-1.2.0.tar.gz -O /tmp/libzip-1.2.0.tar.gz \
	&& wget -c --tries=0 --no-check-certificate http://pecl.php.net/get/mcrypt-1.0.2.tgz -O /tmp/mcrypt-1.0.2.tgz \
	&& wget -c --tries=0 --no-check-certificate https://ftp.openssl.org/source/old/1.0.2/openssl-1.0.2q.tar.gz -O /tmp/openssl-1.0.2q.tar.gz \
	&& wget -c --tries=0 --no-check-certificate https://pecl.php.net/get/solr-2.4.0.tgz -O /tmp/solr-2.4.0.tgz \
	&& wget -c --tries=0 --no-check-certificate http://pecl.php.net/get/memcached-3.1.3.tgz -O /tmp/memcached-3.1.3.tgz \
	&& cd /tmp \
	&& for tar in *.tar.gz;  do tar xvf $tar -C /tmp; done \
	&& for tar in *.tgz;  do tar xvf $tar -C /tmp; done \
	&& cd /tmp/libzip-1.2.0/ \
	&& ./configure \
	&& make \
	&& make install \
	&& cd /tmp/libiconv-1.15/ \
	&& ./configure --prefix=/usr/local/libiconv/ \
	&& make \
	&& make install \
	&& cd /tmp/php-7.3.29 \
	&& ./configure $CONFIG \
	&& make \
	&& make install \
	&& cp -p /usr/local/php/etc/php-fpm.conf.default /usr/local/php/etc/php-fpm.conf \
	&& sed -i 's/;daemonize = yes/daemonize = no/g' /usr/local/php/etc/php-fpm.conf \
	&& cd /tmp/php-7.3.29/ext/ftp/ \
	&& /usr/local/php/bin/phpize \
	&& ./configure --with-php-config=/usr/local/php/bin/php-config --enable-ftp \
	&& make \
	&& make install \
	&& cd /tmp/redis-4.2.0 \
	&& /usr/local/php/bin/phpize \
	&& ./configure --with-php-config=/usr/local/php/bin/php-config \
	&& make \
	&& make install \
	&& cd /tmp/solr-2.4.0 \
	&& /usr/local/php/bin/phpize \
	&& ./configure --with-php-config=/usr/local/php/bin/php-config \
	&& make \
	&& make install \
	&& cd /tmp/pecl-memcache \
	&& /usr/local/php/bin/phpize \
	&& ./configure --with-php-config=/usr/local/php/bin/php-config \
	&& make \
	&& make install \
	&& cd /tmp/mcrypt-1.0.2 \
	&& /usr/local/php/bin/phpize \
	&& ./configure --with-php-config=/usr/local/php/bin/php-config \
	&& make \
	&& make install \
	&& wget -c --tries=0 https://getcomposer.org/download/1.8.0/composer.phar -O /usr/sbin/composer \
	&& chmod +x /usr/sbin/composer \
	&& rm -rf /tmp/* \
	&& ln -s /usr/local/php/sbin/php-fpm /usr/sbin/php-fpm \
	&& apk del mypacks

EXPOSE 9000
COPY conf.d/php.ini /usr/local/php/etc/
COPY conf.d/php-fpm.conf /usr/local/php/etc/

# ADD start.sh /start.sh
# RUN chmod +x /start.sh
# CMD ["/start.sh"]

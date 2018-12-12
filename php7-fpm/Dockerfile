FROM php:7.2-fpm-alpine

RUN apk upgrade --update \
  && apk add --no-cache freetype-dev libpng-dev libjpeg-turbo-dev libxml2-dev make \
  && docker-php-ext-install pdo_mysql opcache gd soap zip pcntl

RUN docker-php-source extract \
  && apk add --no-cache --virtual .phpize-deps-configure $PHPIZE_DEPS \
  && pecl install apcu \
  && docker-php-ext-enable apcu \
  && apk del .phpize-deps-configure \
  && docker-php-source delete

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer
ENV COMPOSER_ALLOW_SUPERUSER=1
RUN composer global require "hirak/prestissimo:^0.3" --prefer-dist --no-progress --no-suggest --classmap-authoritative \
  && composer clear-cache
ENV PATH="${PATH}:/root/.composer/vendor/bin"

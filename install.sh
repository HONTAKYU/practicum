#!/bin/bash

apt-get update \
apt-get upgrade \
apt-get install git zlib1g-dev apache2-dev libcurl4-gnutls-dev libpcre3 libpcre3-dev autoconf libtool libxml2-dev libxml2 default-jre default-jdk \
\
wget https://nginx.org/download/nginx-1.13.5.tar.gz \
gunzip -c nginx-1.13.5.tar.gz | tar xvf - \
wget https://www.modsecurity.org/tarball/2.9.2/modsecurity-2.9.2.tar.gz \
gunzip -c modsecurity-2.9.2.tar.gz | tar xvf – \
\
cd modsecurity-* \
./configure --enable-standalone-module \
make \
cd ../nginx-* \
./configure --add-module=../modsecurity-2.9.2/nginx/modsecurity \
make \
make install \
cd ../modsecurity-* \
cp modsecurity.conf-recommended /usr/local/nginx/conf/ \
cp unicode.mapping /usr/local/nginx/conf/ \
cd /usr/local/nginx/conf/ \
mv modsecurity.conf-recommended modsecurity.conf \
git clone https://github.com/SpiderLabs/owasp-modsecurity-crs \
cd owasp-modsecurity-crs \
mv crs-setup.conf.example crs-setup.conf \
cd rules/ \
mv REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf \
mv RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf \
cd ../.. \
mv ~/nginx.conf . \
mv ~/modesec_includes.conf . \
mv ~/nginx.service /lib/systemd/system/nginx/service \
ln -s /usr/local/nginx/sbin/nginx /bin/nginx \
systemctl daemon-reload \

#download webgoat
cd ../.. \
wget https://github.com/WebGoat/WebGoat/releases/download/7.1/webgoat-container-7.1-exec.jar \




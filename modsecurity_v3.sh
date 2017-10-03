#!/bin/bash

#install necessary libs
set -ex
apt-get update 
apt-get upgrade 
apt-get install sudo wget vim git zlib1g-dev apache2-dev libcurl4-gnutls-dev libpcre3 libpcre3-dev autoconf libtool libxml2-dev libxml2 autopoint bison dh-autoreconf doxygen flex geoip-bin libbison-dev libclang1-3.6 libfl-dev libgeoip-dev libllvm3.6v5 libobjc-5-dev libobjc4 libpcre++-dev libpcre++0v5 libyajl-dev libyajl2 default-jre default-jdk 

#Download, install nginx and modsecurity v3 source files
git clone https://github.com/SpiderLabs/ModSecurity
cd ModSecurity/
git checkout -b v3/master origin/v3/master
mv ../ltmain.sh .
./build.sh
git submodule init
git submodule update #[for bindings/python, others/libinjection, test/test-cases/secrules-language-tests]
./configure
make
make install
cd ..
git clone https://github.com/SpiderLabs/ModSecurity-nginx.git
wget https://nginx.org/download/nginx-1.13.5.tar.gz 
gunzip -c nginx-1.13.5.tar.gz | tar xvf - 

#install nginx with modsecurity openWAF and CRS

# nginx path prefix: "/usr/local/nginx"
# nginx binary file: "/usr/local/nginx/sbin/nginx"
# nginx modules path: "/usr/local/nginx/modules"
# nginx configuration prefix: "/usr/local/nginx/conf"
# nginx configuration file: "/usr/local/nginx/conf/nginx.conf"
# nginx pid file: "/usr/local/nginx/logs/nginx.pid"
# nginx error log file: "/usr/local/nginx/logs/error.log"
# nginx http access log file: "/usr/local/nginx/logs/access.log"
# nginx http client request body temporary files: "client_body_temp"
# nginx http proxy temporary files: "proxy_temp"
# nginx http fastcgi temporary files: "fastcgi_temp"
# nginx http uwsgi temporary files: "uwsgi_temp"
# nginx http scgi temporary files: "scgi_temp"
cd nginx-* 
./configure --add-module=../ModSecurity-nginx
make
make install
cd ../ModSecurity
cp modsecurity.conf-recommended /usr/local/nginx/conf/ 
cd /usr/local/nginx/conf/ 
mv modsecurity.conf-recommended modsecurity.conf 
git clone https://github.com/SpiderLabs/owasp-modsecurity-crs 
cd owasp-modsecurity-crs 
mv crs-setup.conf.example crs-setup.conf 
cd rules/ 
mv REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf 
mv RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf 
cd ../.. 
mv ~/practicum/nginx.conf . 
mv ~/practicum/modsec_includes.conf . 
mv ~/practicum/nginx.service /lib/systemd/system/ 

#start nginx service
ln -s /usr/local/nginx/sbin/nginx /bin/nginx 
systemctl daemon-reload 
systemctl start nginx

#download webgoat
cd ../.. 
wget https://github.com/WebGoat/WebGoat/releases/download/7.1/webgoat-container-7.1-exec.jar 

# download node.js v8, npm (not necessary needed for now), docker and juiceshop
# start juice-shop in backgroud on port 3000
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
apt-get install -y nodejs
apt install docker.io
service docker start
docker pull bkimminich/juice-shop
docker run -d -p 3000:3000 bkimminich/juice-shop


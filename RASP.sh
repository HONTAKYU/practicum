#!/bin/bash

#General installation of Nginx 1.10.x, Docker, and Juice-shop
set -ex
apt-get update 
apt-get upgrade 

#Install nginx and run
apt-get install nginx
mv nginx_RASP.conf /etc/nginx/nginx.conf

#Install docker and juice-shop
apt install docker.io
service docker start
docker pull bkimminich/juice-shop
docker run -d -p 3000:3000 bkimminich/juice-shop

service nginx restart
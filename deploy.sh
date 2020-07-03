#!/usr/bin/env bash

add-apt-repository ppa:certbot/certbot

apt install build-essential
apt install uwsgi
apt install uwsgi-plugin-python3
apt install python3-dev
apt install python-certbot-nginx

pip3 install filelock
pip3 install schedule
pip3 install flask
pip3 install uwsgi

systemctl stop klumba_operator_bot
rm -f  /etc/systemd/system/klumba_operator_bot.service
cp -f ./klumba_operator_bot.service /etc/systemd/system/
systemctl start klumba_operator_bot
systemctl enable klumba_operator_bot

systemctl stop wsgi_client_photos
rm -f  /etc/systemd/system/wsgi_client_photos.service
cp -f ./wsgi_client_photos.service /etc/systemd/system/
systemctl start wsgi_client_photos
systemctl enable wsgi_client_photos

unlink /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/client_photos_backend.conf
rm -f /etc/nginx/sites-available/client_photos_backend.conf
cp ./client_photos_backend.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/client_photos_backend.conf /etc/nginx/sites-enabled/client_photos_backend.conf

certbot --nginx -d services.klumba71.ru -d www.services.klumba71.ru

# UNSAFE, temporary deployment
chmod -R 777 /root

systemctl daemon-reload
sleep 10
systemctl restart nginx
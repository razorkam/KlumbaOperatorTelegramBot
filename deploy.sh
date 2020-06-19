#!/usr/bin/env bash

pip3 install filelock
pip3 install schedule

systemctl stop klumba_operator_bot
rm -f  /etc/systemd/system/klumba_operator_bot.service
cp -f ./klumba_operator_bot.service /etc/systemd/system/
systemctl start klumba_operator_bot
systemctl enable klumba_operator_bot
systemctl daemon-reload
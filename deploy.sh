#!/usr/bin/env bash

systemctl stop klumba_operator_bot
rm -f  /etc/systemd/system/klumba_operator_bot.service
cp -f ./klumba_operator_bot.service /etc/systemd/system/
systemctl start klumba_operator_bot
systemctl enable klumba_operator_bot
systemctl daemon-reload
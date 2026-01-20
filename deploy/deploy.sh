#!/bin/bash

cd /home/ubuntu/KMDMC_ERP
source venv/bin/activate

git pull origin main

cd src
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn

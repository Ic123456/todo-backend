#!usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python Core/manage.py collectstatic --no-input
python Core/manage.py migrate
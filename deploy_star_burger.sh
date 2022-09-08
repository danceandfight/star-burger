#!/bin/bash

set -e
cd /opt/star-burger
git stash
git pull

commithash=$(git rev-parse --verify HEAD)
source .env
pip install -r requirements.txt
echo Python requirements updated

npm install --dev
echo Node requirements updated
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo Frontend is ready
python3 manage.py collectstatic --noinput
echo Static files collected
python3 manage.py migrate --noinput
echo Migrations applied
sudo systemctl daemon-reload
echo Reload systemd files
sudo systemctl restart star-burger.service
echo Django service restarted
sudo systemctl reload nginx.service
echo Nginx reloaded
curl -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
-H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' \
-d '{"environment": "production", "revision": "$commithash", "rollbar_name": "pavel", "local_username": "pavel-ci", "comment": "", "status": "succeeded"}'
echo $(git status)
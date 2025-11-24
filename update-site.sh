#! /usr/bin/bash

source "/home/dustiestgolf/venv/bin/activate"

pushd "/home/dustiestgolf/alexkaufman.live"

git fetch
git reset --hard origin/main
flask --app alexkaufmanlive update-db

# Touch WSGI file to reload the web app
touch /var/www/alexkaufman_live_wsgi.py

popd

#! /usr/bin/bash

source "/home/dustiestgolf/.virtualenvs/base/bin/activate"

pushd "/home/dustiestgolf/md-webapp"
pushd "/home/dustiestgolf/md-webapp/alexkaufmanlive/content"

git fetch
git reset --hard origin/main
popd

git fetch
git reset --hard origin/main
flask --app alexkaufmanlive update-db
popd

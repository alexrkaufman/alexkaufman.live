#! /usr/bin/bash

source "/home/dustiestgolf/.virtualenvs/base/bin/activate"

pushd "/home/dustiestgolf/alexkaufmanlive"

git fetch
git reset --hard origin/main
flask --app alexkaufmanlive update-db
popd

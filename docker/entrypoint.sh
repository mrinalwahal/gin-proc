#!/usr/bin/env bash

set -eu

cd /app/backend
python3 server.py &
bpid=$!

cd /app/frontend
DEBUG=1 npm start &
fpid=$!

stopservices() {
    echo "Stopping services"
    kill ${bpid}
    kill ${fpid}
}

trap stopservices SIGINT

wait ${bpid} ${fpid}
echo "Done"

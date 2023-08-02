#!/usr/bin/env bash
set -eu
org=kclhi-ca
orgname=kclhi

openssl genpkey -algorithm RSA -out "$orgname".key
openssl req -x509 -key "$orgname".key -days 365 -out "$orgname".crt \
    -subj "/CN=$org/O=$org"

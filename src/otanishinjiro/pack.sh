#!/bin/bash
set -e; cd "$(dirname "$0")"
python3 build.py --noindex >/dev/null
rm -rf dist prod && mkdir -p dist
(cd out && zip -qr ../dist/otanishinjiro_限定公開用.zip index.html img)
python3 build.py >/dev/null
mkdir -p prod/otanishinjiro && cp -r out/index.html out/img prod/otanishinjiro/ && cp 設置手順.txt prod/
(cd prod && zip -qr ../dist/otanishinjiro_本番設置用.zip otanishinjiro 設置手順.txt)
echo done; ls -la dist

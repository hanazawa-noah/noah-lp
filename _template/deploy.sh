#!/bin/bash
# 確認用サイト(GitHub Pages)へ反映。 usage: GH_TOKEN=xxx ./deploy.sh
set -e; cd "$(dirname "$0")"
python3 build.py --noindex --out out/index.html >/dev/null
rm -rf gh && git clone -q "https://x-access-token:${GH_TOKEN}@github.com/hanazawa-noah/noah-lp.git" gh
rm -rf gh/wo2 && mkdir -p gh/wo2 && cp -r out/index.html out/img gh/wo2/
python3 build.py >/dev/null
cd gh && git config user.email lp@noah.local && git config user.name "NOAH LP bot" && git add -A && (git commit -qm "update wo2 $(date +%F_%H%M)" && git push -q) || echo "no changes"
echo "https://hanazawa-noah.github.io/noah-lp/wo2/"

#!/bin/bash
# 確認用サイト(GitHub Pages)へ反映。 usage: ./deploy.sh wo2
set -e; cd "$(dirname "$0")"; S="${1:?slug}"
(cd "src/$S" && python3 build.py --noindex --out out/index.html >/dev/null)
rm -rf "$S"; mkdir -p "$S"; cp -r "src/$S/out/index.html" "src/$S/out/img" "$S/"
(cd "src/$S" && python3 build.py >/dev/null)
git add -A && git commit -qm "update $S $(date +%F_%H%M)" || true
git push
echo "https://hanazawa-noah.github.io/noah-lp/$S/"

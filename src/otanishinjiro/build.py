#!/usr/bin/env python3
# 大谷晋二郎プロジェクトLP: source.html -> out/index.html
# 画像はHTML内に埋め込み済み。--noindex で確認用(noindexあり)、なしで本番用(noindexなし)
import argparse, os, re, shutil
ap = argparse.ArgumentParser()
ap.add_argument('--noindex', action='store_true')
ap.add_argument('--out', default='out/index.html')
a = ap.parse_args()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h = open('source.html', encoding='utf-8').read()
NOINDEX = '<meta name="robots" content="noindex, nofollow"><!-- 仮公開用: 本公開時にこの行を削除 -->\n'
h = h.replace(NOINDEX, '')
if a.noindex:
    h = h.replace('<meta name="viewport"', NOINDEX + '<meta name="viewport"', 1)
os.makedirs('out/img', exist_ok=True)
open(a.out, 'w', encoding='utf-8').write(h)
for f in ('ogp.jpg', 'favicon.png'):
    shutil.copy('assets/' + f, 'out/img/' + f)
print('built', a.out, 'noindex=' + str(a.noindex))

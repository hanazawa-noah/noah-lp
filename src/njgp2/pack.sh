#!/bin/bash
# data.json/build.py から 3形態の納品物を dist/ に生成
set -e
cd "$(dirname "$0")"
python3 build.py >/dev/null
python3 - <<'EOF'
import re,base64,io,os
from PIL import Image
h=open('out/index.html',encoding='utf-8').read()
def uri(p,maxw,q):
    im=Image.open('out/'+p)
    if im.width>maxw: im=im.resize((maxw,round(im.height*maxw/im.width)),Image.LANCZOS)
    buf=io.BytesIO()
    if p.endswith(('.png','.webp')): im.save(buf,'WEBP',quality=(92 if 'logo' in p or 'badge' in p else 70),method=6); mt='image/webp'
    else: im.convert('RGB').save(buf,'JPEG',quality=q,optimize=True,subsampling=0); mt='image/jpeg'
    return f'data:{mt};base64,'+base64.b64encode(buf.getvalue()).decode()
h=re.sub(r' srcset="[^"]+" sizes="[^"]+"','',h)
h=re.sub(r'<source media="\(max-width:900px\)"[^>]+>','',h)  # プレビューは横KVのみ
plan={'img/kv.jpg':(1000,64),'img/logo_white.webp':(999,0),'img/noah_badge.png':(999,0),'img/bracket_960.jpg':(900,64)}
h=h.replace('href="img/bracket.jpg"','href="#bracket"')  # 拡大リンクはプレビューでは無効
for p in sorted(set(re.findall(r'img/p_\w+\.webp',h))): plan[p]=(210,0)
for p in sorted(set(re.findall(r'img/vs_\w+_960\.jpg',h))): plan[p]=(480,58)
for p in sorted(set(re.findall(r'img/goods_\w+\.webp',h))): plan[p]=(180,0)
for p in sorted(set(re.findall(r'img/news_\d+_960\.jpg',h))): plan[p]=(440,55)
for p,(w,q) in plan.items(): h=h.replace(f'"{p}"',f'"{uri(p,w,q)}"')
h=h.replace('<meta name="viewport"','<meta name="robots" content="noindex,nofollow"><meta name="viewport"')
open('njgp2_preview.html','w',encoding='utf-8').write(h); print('preview',os.path.getsize('njgp2_preview.html')//1024,'KB')
EOF
python3 build.py --noindex >/dev/null
rm -rf dist prod out/index.html.bak && mkdir -p dist && (cd out && zip -qr ../dist/njgp2_限定公開用.zip index.html img)
python3 build.py >/dev/null
mkdir -p prod/njgp2 && cp -r out/index.html out/img prod/njgp2/ && cp 設置手順.txt prod/
(cd prod && zip -qr ../dist/njgp2_本番設置用.zip njgp2 設置手順.txt)
zip -qj dist/njgp2_ソース_data_build.zip data.json build.py prep_img.py shot.py pack.sh 設置手順.txt
cp njgp2_preview.html dist/ && ls -la dist

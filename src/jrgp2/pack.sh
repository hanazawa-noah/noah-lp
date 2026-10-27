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
for p,(w,q) in plan.items(): h=h.replace(f'"{p}"',f'"{uri(p,w,q)}"')
h=h.replace('<meta name="viewport"','<meta name="robots" content="noindex,nofollow"><meta name="viewport"')
open('jrgp2_preview.html','w',encoding='utf-8').write(h); print('preview',os.path.getsize('jrgp2_preview.html')//1024,'KB')
EOF
python3 build.py --noindex >/dev/null
rm -rf dist prod out/index.html.bak && mkdir -p dist && (cd out && zip -qr ../dist/jrgp2_限定公開用.zip index.html img)
python3 build.py >/dev/null
mkdir -p prod/jrgp2026 && cp -r out/index.html out/img prod/jrgp2026/ && cp 設置手順.txt prod/
(cd prod && zip -qr ../dist/jrgp2_本番設置用.zip jrgp2026 設置手順.txt)
zip -qj dist/jrgp2_ソース_data_build.zip data.json build.py prep_img.py shot.py pack.sh 設置手順.txt
cp jrgp2_preview.html dist/ && ls -la dist

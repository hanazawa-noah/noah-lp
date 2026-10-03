#!/bin/bash
# data.json/build.py から 3形態の納品物を生成して /mnt/user-data/outputs へ
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
    if p.endswith(('.png','.webp')): im.save(buf,'WEBP',quality=92,method=6); mt='image/webp'
    else: im.convert('RGB').save(buf,'JPEG',quality=q,optimize=True,subsampling=0); mt='image/jpeg'
    return f'data:{mt};base64,'+base64.b64encode(buf.getvalue()).decode()
h=re.sub(r' srcset="[^"]+" sizes="[^"]+"','',h)
plan={'img/kv.jpg':(1920,88),'img/kv_sp_crop.jpg':(1080,88),'img/logo_wo2_s.webp':(640,0),'img/noah_badge.png':(999,0),'img/neo_high.png':(999,0)}
for p in sorted(set(re.findall(r'img/match_[\w\-]+_sm\.jpg',h))): plan[p]=(960,82)
for p in sorted(set(re.findall(r'img/video_[\w\-]+\.jpg',h))): plan[p]=(1280,82)
for p,(w,q) in plan.items(): h=h.replace(f'"{p}"',f'"{uri(p,w,q)}"')
h=h.replace('<meta name="viewport"','<meta name="robots" content="noindex,nofollow"><meta name="viewport"')
open('wo2_preview.html','w',encoding='utf-8').write(h); print('preview',os.path.getsize('wo2_preview.html')//1024,'KB')
EOF
python3 build.py --noindex >/dev/null
rm -rf dist prod && mkdir -p dist && (cd out && zip -qr ../dist/wo2_限定公開用.zip index.html img)
python3 build.py >/dev/null
mkdir -p prod/wo2026 && cp -r out/index.html out/img prod/wo2026/ && cp 設置手順.txt prod/
(cd prod && zip -qr ../dist/wo2_本番設置用.zip wo2026 設置手順.txt)
zip -qj dist/wo2_ソース_data_build.zip data.json build.py pack.sh 設置手順.txt
cp wo2_preview.html dist/ && mkdir -p /mnt/user-data/outputs && cp dist/* /mnt/user-data/outputs/ && ls -la /mnt/user-data/outputs

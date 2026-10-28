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
    if p.endswith(('.png','.webp')): im.save(buf,'WEBP',quality=92,method=6); mt='image/webp'
    else: im.convert('RGB').save(buf,'JPEG',quality=q,optimize=True,subsampling=0); mt='image/jpeg'
    return f'data:{mt};base64,'+base64.b64encode(buf.getvalue()).decode()
h=re.sub(r' srcset="[^"]+" sizes="[^"]+"','',h)
plan={'img/kv.jpg':(1200,70),'img/logo_gold_s.webp':(320,0),'img/logo_gold.webp':(560,0),'img/noah_badge.png':(999,0),'img/venue_960.jpg':(640,72),'img/pv_poster.jpg':(800,70)}
h=re.sub(r'<video class="video__mp4" src="[^"]+"','<video class="video__mp4"',h)  # 動画はプレビューに埋め込めないので外す
for p in sorted(set(re.findall(r'img/match_[\w\-]+_sm\.jpg',h))): plan[p]=(960,82)
for p in sorted(set(re.findall(r'img/video_[\w\-]+\.jpg',h))): plan[p]=(1280,82)
for p,(w,q) in plan.items(): h=h.replace(f'"{p}"',f'"{uri(p,w,q)}"')
h=h.replace('<meta name="viewport"','<meta name="robots" content="noindex,nofollow"><meta name="viewport"')
open('nye2026_preview.html','w',encoding='utf-8').write(h); print('preview',os.path.getsize('nye2026_preview.html')//1024,'KB')
EOF
python3 build.py --noindex >/dev/null
rm -rf dist prod out/index.html.bak && mkdir -p dist && (cd out && zip -qr ../dist/nye2026_限定公開用.zip index.html img)
python3 build.py >/dev/null
mkdir -p prod/nye2026 && cp -r out/index.html out/img prod/nye2026/ && cp 設置手順.txt prod/
(cd prod && zip -qr ../dist/nye2026_本番設置用.zip nye2026 設置手順.txt)
zip -qj dist/nye2026_ソース_data_build.zip data.json unannounced.json build.py prep_img.py shot.py pack.sh 設置手順.txt
# LP誘導バナー: data.json に "banner" があれば作る(tools/make_banner.py)
if grep -q '"banner"' data.json; then python3 ../../tools/make_banner.py nye2026 && cp banner/*.jpg dist/; fi
cp nye2026_preview.html dist/ && ls -la dist

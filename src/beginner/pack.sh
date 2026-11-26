#!/bin/bash
# data.json/build.py から 3形態の納品物(プレビューHTML・限定公開用ZIP・本番設置用ZIP)とバナー一式を dist/ に生成
set -e
cd "$(dirname "$0")"
python3 build.py >/dev/null
python3 -X utf8 - <<'EOF'
import re,base64,io,os
from PIL import Image
h=open('out/index.html',encoding='utf-8').read()
def uri(p):
    im=Image.open('out/'+p); keep='logo' in p or 'lockup' in p or 'badge' in p or 'favicon' in p
    maxw=999 if keep else (760 if p in('img/mv.webp','img/view_2.webp') else 300)
    if im.width>maxw: im=im.resize((maxw,round(im.height*maxw/im.width)),Image.LANCZOS)
    buf=io.BytesIO()
    if keep: im.save(buf,'PNG',optimize=True); mt='image/png'
    else: im.convert('RGB').save(buf,'WEBP',quality=52,method=6); mt='image/webp'
    return f'data:{mt};base64,'+base64.b64encode(buf.getvalue()).decode()
h=re.sub(r' srcset="[^"]+" sizes="[^"]+"','',h)
h=re.sub(r'<source [^>]*srcset="img/[^>]+>','',h)  # プレビューは1サイズだけ
for p in sorted(set(re.findall(r'"(img/[\w\-.]+\.(?:webp|png|jpg))"',h))):
    if 'ogp' in p: continue
    h=h.replace(f'"{p}"',f'"{uri(p)}"')
h=h.replace('<meta name="viewport"','<meta name="robots" content="noindex,nofollow"><meta name="viewport"',1)
open('beginner_preview.html','w',encoding='utf-8').write(h); print('preview',os.path.getsize('beginner_preview.html')//1024,'KB')
EOF
python3 build.py --noindex >/dev/null
rm -rf dist prod && mkdir -p dist && (cd out && zip -qr ../dist/beginner_限定公開用.zip index.html img)
python3 build.py >/dev/null
mkdir -p prod/beginner && cp -r out/index.html out/img prod/beginner/ && cp 設置手順.txt prod/
(cd prod && zip -qr ../dist/beginner_本番設置用.zip beginner 設置手順.txt)
zip -qj dist/beginner_ソース_data_build.zip data.json build.py prep_img.py prep_photos.py prep_rules.py shot.py make_kokuchi.py sns_icons.svg pack.sh 設置手順.txt
python3 -X utf8 make_kokuchi.py  # LP誘導バナー(360×80/720×160)と告知バナー(1920×1080)
cp beginner_preview.html dist/ && ls -la dist

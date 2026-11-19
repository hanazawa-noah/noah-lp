#!/usr/bin/env python3
"""依頼者支給の写真(uploads/1〜16)とサイン会写真から out/img/ を作る。
usage: python prep_photos.py [サイン会写真フォルダ]
サイン会写真(共有ドライブ NOAH試合写真 2026/06/25・07/05 後楽園 試合前サイン会)は重いのでリポジトリに置かない
"""
import sys, os
from PIL import Image, ImageOps
OUT = 'out/img/'
def save(im, name, w, q=80, ratio=None, cx=.5, cy=.5):
    im = ImageOps.exif_transpose(im).convert('RGB')
    if ratio:  # ratio=幅/高さ に中心(cx,cy)基準で切り抜く
        W, H = im.size
        if W / H > ratio: nw = int(H * ratio); x0 = int((W - nw) * cx); im = im.crop((x0, 0, x0 + nw, H))
        else: nh = int(W / ratio); y0 = int((H - nh) * cy); im = im.crop((0, y0, W, y0 + nh))
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(OUT + name + '.webp', 'WEBP', quality=q, method=6)
    print(name, im.size, os.path.getsize(OUT + name + '.webp') // 1024, 'KB')
U = lambda n: Image.open(f'uploads/{n}')
save(U('1.jpg'), 'mv', 1477, 80)                 # メインビジュアル(満員の後楽園ホール・南側後方から)
save(U('1.jpg'), 'mv_s', 800, 76)
save(U('2.jpg'), 'view_east', 1200, 80)          # 東側の席からの見え方
for n in (3, 13, 5, 6, 4, 12):                   # 試合写真ギャラリー
    save(U(f'{n}.jpg'), f'ph_{n}', 960, 78, ratio=3 / 2)
save(U('14.webp'), 'sign_info', 1200, 82)        # サイン会告知の例(11.9 後楽園)
save(U('15.jpg'), 'en_sns', 1200, 82)            # 撮影OK
if len(sys.argv) > 1:
    d = sys.argv[1]
    save(Image.open(d + '/_B8A4083.JPG'), 'sg_1', 800, 78, ratio=3 / 2)
    save(Image.open(d + '/_B8A7659.JPG'), 'sg_2', 800, 78, ratio=3 / 2)
    im = Image.open(d + '/_B8A7693.JPG'); W, H = im.size
    save(im.crop((0, int(H * .2), int(W * .9), H)), 'sg_3', 800, 78, ratio=3 / 2, cx=0, cy=1)  # ファンの顔が入らないように

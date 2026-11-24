#!/usr/bin/env python3
"""ルール説明(RULE1〜5)の写真を、依頼者支給の「初心者ページ用素材」(2026-11-24 ZIP)から作る。
usage: python -X utf8 prep_rules.py <ZIPを展開した「初心者ページ用素材」フォルダ>
元写真は重い(110MB)のでリポジトリに置かない。prep_img.py(パンフの切り抜き)を回し直したら、このあとに実行する。
支給が無かった項目(タッグマッチ／急所攻撃／イス・凶器／髪をつかむ)はパンフの写真のまま。
"""
import sys, os, glob
from PIL import Image, ImageOps
SRC, OUT = sys.argv[1], 'out/img/'
# 出力名: (フォルダ名の一部, ファイル名の一部, 幅/高さ, 仕上がり幅, 切り抜きの横位置 0=左〜1=右)
PICK = {
    'r1_heavy':  ('ヘビー級', 'B8A9982', 5 / 4, 640, .5),
    'r1_junior': ('ジュニアヘビー級', 'B8A1814', 5 / 4, 640, .3),
    'r2_single': ('シングル', 'B8A4277', 5 / 4, 640, .6),
    'r3_rope':   ('ロープブレイク', 'B8A2910', 16 / 10, 900, .5),
    'r4_2':      ('パンチ', 'B8A0980', 1, 480, .35),
    'r4_5':      ('かきむしり', 'B8A1771', 1, 480, .6),
    'r4_6':      ('レフェリー暴行', 'B8A6776', 1, 480, .39),
    'r4_7':      ('介入', 'B8A3357', 1, 480, .5, (.40, .07, .97, .925)),  # 最後は先に切り出す範囲(左,上,右,下 の割合)
    'r5_1':      ('カウント', 'B8A9318', 1, 480, .1),
    'r5_2':      ('ギブアップ', 'B8A2118', 1, 480, .75),
    'r5_3':      ('リングアウト', 'B8A2124', 1, 480, .9),
    'r5_4':      ('KO', 'B8A1262', 1, 480, .5),
    'r5_5':      ('レフェリーストップ', 'B8A6261', 1, 480, 0),
    'r5_6':      ('ノーコンテスト', 'B8A9017', 1, 480, .35),
}
files = glob.glob(SRC + '/**/*.JPG', recursive=True)
for name, (_, key, ratio, w, cx, *box) in PICK.items():
    f = [p for p in files if key in os.path.basename(p)]
    assert len(f) == 1, (name, key, f)
    im = ImageOps.exif_transpose(Image.open(f[0])).convert('RGB'); W, H = im.size
    if box: a, b, c, d = box[0]; im = im.crop((int(W * a), int(H * b), int(W * c), int(H * d))); W, H = im.size
    if W / H > ratio: nw = int(H * ratio); x0 = int((W - nw) * cx); im = im.crop((x0, 0, x0 + nw, H))
    else: nh = int(W / ratio); y0 = (H - nh) // 2; im = im.crop((0, y0, W, y0 + nh))
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(OUT + name + '.webp', 'WEBP', quality=80, method=6)
    print(name, im.size, os.path.getsize(OUT + name + '.webp') // 1024, 'KB')

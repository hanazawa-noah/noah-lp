#!/usr/bin/env python3
"""パンフ広告(P04-05 BEGINNER)の素材から out/img/ を作る。
usage: python3 prep_img.py <p04_bg.psd> <p05_bg.psd> <A4見開き.ai>
元データ(PSD/AI)は重いのでリポジトリには置かない(デザイナー支給ZIPを展開して指定する)
"""
import sys, numpy as np, fitz
from psd_tools import PSDImage
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
p04, p05, ai = sys.argv[1:4]
OUT = 'out/img/'
# 写真の位置(PSD内のピクセル座標: x0,y0,x1,y1)
BOX = {
 'p04': {'r1_heavy': (3, 3, 607, 483), 'r1_junior': (661, 3, 1268, 483), 'r2_single': (3, 1016, 552, 1547), 'r2_tag': (603, 1091, 1265, 1547),
         'r3_rope': (3, 1939, 855, 2544), 'r4_1': (1488, 345, 1910, 808), 'r4_2': (1969, 345, 2389, 808), 'r4_3': (1488, 925, 1910, 1387),
         'r4_4': (1969, 925, 2389, 1387), 'r4_5': (1488, 1504, 1910, 1967), 'r4_6': (1969, 1504, 2389, 1967), 'r4_7': (1731, 2084, 2153, 2544)},
 'p05': {'r5_1': (3, 3, 441, 415), 'r5_2': (3, 545, 441, 1002), 'r5_3': (3, 1131, 441, 1629), 'r5_4': (3, 1759, 441, 2174), 'r5_5': (3, 2304, 441, 2802),
         'r5_6': (3, 2931, 441, 3379), 'en_oshi': (1258, 53, 1839, 505), 'en_goods': (896, 760, 1481, 1213), 'en_site': (1258, 2883, 1839, 3335)},
}
for tag, f in (('p04', p04), ('p05', p05)):
    im = PSDImage.open(f).topil().convert('RGB')
    for name, (x0, y0, x1, y1) in BOX[tag].items():
        c = im.crop((x0 + 3, y0 + 3, x1 - 3, y1 - 3))  # 縁の白にじみを落とす
        c.save(OUT + name + '.webp', 'WEBP', quality=80, method=6)
        print(name, c.size)
# ロゴ(バッジ+PRO WRESTLING NOAH)と動画撮影OK・NOAH'S ARKはAIのベクターから書き出す(pt座標)
doc = fitz.open(ai, filetype='pdf'); pg = doc[0]
def clip(name, rect, zoom, alpha=False, trim=False):
    pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=fitz.Rect(*rect), alpha=alpha)
    im = Image.frombytes('RGBA' if alpha else 'RGB', (pix.width, pix.height), pix.samples)
    if trim:
        a = np.asarray(im.convert('RGB')).astype(int); bg = a[2, 2]
        m = (abs(a - bg).sum(axis=2) > 24); ys, xs = np.where(m)
        im = im.crop((xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)); print(name, 'bg', tuple(bg))
    im.save(OUT + name, quality=90) if name.endswith('.webp') else im.save(OUT + name)
    print(name, im.size)
clip('noah_lockup.png', (44, 106, 206, 136), 5, trim=True)
clip('en_sns.webp', (1015.0, 410.2, 1136.5, 503.0), 5)
clip('en_fc.webp', (941.0, 555.5, 1061.5, 649.0), 5)

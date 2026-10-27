#!/usr/bin/env python3
"""uploads/ の素材から out/img/ の画像を作る(素材を差し替えたら再実行)
- kv_h.jpg  -> kv.jpg(1920w q88) / kv_1280.jpg / kv_960.jpg / ogp.jpg(1200x630)
- kv_v.jpg  -> kv_sp.jpg(1125w q86) / kv_sp_750.jpg  ※スマホは縦KV
- kv_h.jpg の選手タイル(8×2)を切り出し -> p_<id>.webp
- bracket.jpg -> bracket.jpg(1920w q88) / bracket_960.jpg、左上ロゴを白抜きにして logo_white.webp
- vs_*.jpg  -> vs_*.jpg(1920w q88) / vs_*_960.jpg(960w q84)
"""
import glob, os
from PIL import Image, ImageOps

def jpg(im, path, w, q):
    if im.width != w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(path, 'JPEG', quality=q, optimize=True, progressive=True)

kv = Image.open('uploads/kv_h.jpg').convert('RGB')
jpg(kv, 'out/img/kv.jpg', 1920, 88); jpg(kv, 'out/img/kv_1280.jpg', 1280, 84); jpg(kv, 'out/img/kv_960.jpg', 960, 84)
kv.resize((1200, 675), Image.LANCZOS).crop((0, 22, 1200, 652)).save('out/img/ogp.jpg', 'JPEG', quality=86, optimize=True)
kvv = Image.open('uploads/kv_v.jpg').convert('RGB')
jpg(kvv, 'out/img/kv_sp.jpg', 1125, 86); jpg(kvv, 'out/img/kv_sp_750.jpg', 750, 84)

# 選手タイル: 横KVの並び(トーナメント表と同じ順)
ORDER = ['fujimura', 'bushi', 'lykos2', 'alejandro', 'namiki', 'sato', 'odashima', 'masaoka',
         'kondo', 'yohey', 'tadasuke', 'hi69', 'akeem', 'lykos1', 'mensore', 'bane']
for i, pid in enumerate(ORDER):
    x, y = 64 + (i % 8) * 226, (205, 487)[i // 8]
    kv.crop((x, y, x + 210, y + 265)).save(f'out/img/p_{pid}.webp', 'WEBP', quality=86, method=6)

br = Image.open('uploads/bracket.jpg').convert('RGB')
jpg(br, 'out/img/bracket.jpg', 1920, 88); jpg(br, 'out/img/bracket_960.jpg', 960, 84)

# ロゴ: トーナメント表左上の黒ロゴを形だけ取り出して白で塗る(横KVの白ロゴと同じ扱い)。
# マルハンのロゴは色を変えられないので切り出さず、「マルハン presents」は文字で出す
lg = br.crop((60, 112, 385, 170)).convert('L')
a = lg.point(lambda p: 255 if p < 70 else (0 if p > 130 else round((130 - p) * 255 / 60)))
a = a.crop(a.getbbox())
white = Image.new('RGBA', a.size, (255, 255, 255, 255)); white.putalpha(a)
white.save('out/img/logo_white.webp', 'WEBP', quality=92, method=6)
print('logo', white.size)

for f in sorted(glob.glob('uploads/vs_*.jpg')):
    n = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGB')
    jpg(im, f'out/img/{n}.jpg', 1920, 88); jpg(im, f'out/img/{n}_960.jpg', 960, 84)
print('ok')

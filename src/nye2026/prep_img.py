#!/usr/bin/env python3
"""uploads/ の素材から out/img/ の画像を作る(素材を差し替えたら再実行)
- uploads/kv.webp   -> kv.jpg(1920w q88) / kv_960.jpg(960w q84) / ogp.jpg(1200x630)
- uploads/logo.png  -> 透過部分(alpha)を型にして金色で塗った logo_gold.webp / logo_gold_s.webp
"""

from PIL import Image

kv = Image.open('uploads/kv.webp').convert('RGB')
kv.resize((1920, 1080), Image.LANCZOS).save('out/img/kv.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
kv.resize((960, 540), Image.LANCZOS).save('out/img/kv_960.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
kv.resize((1280, 720), Image.LANCZOS).save('out/img/kv_1280.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
o = kv.resize((1200, 675), Image.LANCZOS).crop((0, 26, 1200, 656))
o.save('out/img/ogp.jpg', 'JPEG', quality=86, optimize=True)

# ロゴ: 白塗り(形だけ取り出す)→ MVのロゴと同じ金色を上から貼る。(容量を抑えるため質感はつけない)
logo = Image.open('uploads/logo.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
a = logo.getchannel('A')
w, h = logo.size
grad = Image.new('RGB', (1, h))
top, bot = (247, 202, 92), (214, 154, 52)
for y in range(h):
    t = y / (h - 1)
    grad.putpixel((0, y), tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
gold = grad.resize((w, h))
gold.putalpha(a)
for name, tw in [('logo_gold', 1200), ('logo_gold_s', 480)]:
    gold.resize((tw, round(h * tw / w)), Image.LANCZOS).save(f'out/img/{name}.webp', 'WEBP', quality=90, method=6)
print('logo', gold.size, '->', [(n, tw, round(h * tw / w)) for n, tw in [('logo_gold', 1200), ('logo_gold_s', 480)]])

# 会場写真: 左右の黒帯を切り落として 1510w前後(q88) と 960w(q84)
v = Image.open('uploads/venue.jpg').convert('RGB')
v = v.crop(v.convert('L').point(lambda p: 255 if p > 12 else 0).getbbox())
v.save('out/img/venue.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
v.resize((960, round(v.height * 960 / v.width)), Image.LANCZOS).save('out/img/venue_960.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
print('venue', v.size)

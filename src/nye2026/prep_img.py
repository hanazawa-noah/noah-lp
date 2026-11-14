#!/usr/bin/env python3
"""uploads/ の素材から out/img/ の画像を作る(素材を差し替えたら再実行)
- uploads/kv_main_16-9.jpg(及川さんMV) -> kv.jpg(1920w q88) / kv_1280 / kv_960 / ogp.jpg(1200x630)
- uploads/kv_main_3-4.jpg -> kv_sp.jpg(960x1280) スマホ用の縦MV
- uploads/abema_kv.png    -> bc_abema.jpg(放送情報のABEMA用ビジュアル)
- uploads/logo.png  -> 透過部分(alpha)を型にしてMVロゴと同じピンクで塗った logo_pink.webp / logo_pink_s.webp
"""

from PIL import Image

kv = Image.open('uploads/kv_main_16-9.jpg').convert('RGB')
kv.resize((1920, 1080), Image.LANCZOS).save('out/img/kv.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
kv.resize((960, 540), Image.LANCZOS).save('out/img/kv_960.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
kv.resize((1280, 720), Image.LANCZOS).save('out/img/kv_1280.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
o = kv.resize((1200, 675), Image.LANCZOS).crop((0, 26, 1200, 656))
o.save('out/img/ogp.jpg', 'JPEG', quality=86, optimize=True)
Image.open('uploads/kv_main_3-4.jpg').convert('RGB').resize((960, 1280), Image.LANCZOS).save('out/img/kv_sp.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
ab = Image.open('uploads/abema_kv.png').convert('RGB')
ab.resize((960, round(ab.height * 960 / ab.width)), Image.LANCZOS).save('out/img/bc_abema.jpg', 'JPEG', quality=86, optimize=True, progressive=True)
print('abema', ab.size)

# ロゴ: 白塗り(形だけ取り出す)→ MVのロゴと同じピンク(上が白っぽく下が濃い)を上から貼る。(容量を抑えるため質感はつけない)
logo = Image.open('uploads/logo.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
a = logo.getchannel('A')
w, h = logo.size
grad = Image.new('RGB', (1, h))
top, bot = (250, 232, 240), (206, 126, 154)
for y in range(h):
    t = y / (h - 1)
    grad.putpixel((0, y), tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
gold = grad.resize((w, h))
gold.putalpha(a)
for name, tw in [('logo_pink', 1200), ('logo_pink_s', 480)]:
    gold.resize((tw, round(h * tw / w)), Image.LANCZOS).save(f'out/img/{name}.webp', 'WEBP', quality=90, method=6)
print('logo', gold.size, '->', [(n, tw, round(h * tw / w)) for n, tw in [('logo_pink', 1200), ('logo_pink_s', 480)]])

# 会場写真: 左右の黒帯を切り落として 1510w前後(q88) と 960w(q84)
v = Image.open('uploads/venue.jpg').convert('RGB')
v = v.crop(v.convert('L').point(lambda p: 255 if p > 12 else 0).getbbox())
v.save('out/img/venue.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
v.resize((960, round(v.height * 960 / v.width)), Image.LANCZOS).save('out/img/venue_960.jpg', 'JPEG', quality=84, optimize=True, progressive=True)
print('venue', v.size)

# バナー用ロゴ: デザイナーのベクターデータ(PSDのリンク元 .ai)を高解像度で書き出し、LPと同じピンクで塗る
import fitz
pix = fitz.open('uploads/logo_vector.ai')[0].get_pixmap(dpi=300, alpha=True)
va = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples).getchannel('A')
va = va.crop(va.getbbox())
vw, vh = va.size
vg = Image.new('RGB', (1, vh))
for y in range(vh):
    t = y / (vh - 1)
    vg.putpixel((0, y), tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
vg = vg.resize((vw, vh)); vg.putalpha(va)
vg.resize((1400, round(vh * 1400 / vw)), Image.LANCZOS).save('uploads/banner_logo_pink.png')
print('banner logo', vg.size)

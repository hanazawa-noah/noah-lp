#!/usr/bin/env python3
"""確認用スクショ(PC 1440 / SP 390)を撮り、OGP画像(out/img/ogp.jpg)も作る。
usage: python3 shot.py [スクショ出力フォルダ]
"""
import sys, os, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image

dst = sys.argv[1] if len(sys.argv) > 1 else 'shots'
os.makedirs(dst, exist_ok=True)
url = pathlib.Path('out/index.html').resolve().as_uri()
SCROLL = 'async()=>{document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}scrollTo(0,0)}'
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, step in [('pc', 1440, 900, 1500), ('sp', 390, 844, 1700)]:
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg.goto(url); pg.wait_for_timeout(1800)
        pg.screenshot(path=f'{dst}/{name}_top.png')
        pg.evaluate(SCROLL); pg.wait_for_timeout(800)
        pg.add_style_tag(content='.topwrap{position:static!important}')
        pg.screenshot(path=f'{dst}/{name}_full.png', full_page=True)
        im = Image.open(f'{dst}/{name}_full.png')
        for k, y in enumerate(range(0, im.height, step)):  # 長いので分割しても保存
            im.crop((0, y, im.width, min(y + step, im.height))).save(f'{dst}/{name}_{k:02d}.png')
        over = pg.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
        print(name, im.size, 'h-overflow', over)
        pg.close()
    # OGP: ヒーローの文字部分を 1200x630 で
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    pg.goto(url); pg.wait_for_timeout(1500)
    pg.add_style_tag(content='.topwrap{display:none}.hero{padding-top:64px}.hero__lead{display:none}.hero__ph{margin-top:44px}.wrap{width:1080px}')
    pg.wait_for_timeout(300)
    pg.screenshot(path=f'{dst}/ogp.png')
    Image.open(f'{dst}/ogp.png').convert('RGB').save('out/img/ogp.jpg', quality=84, optimize=True)
    b.close()
print('ok', dst)

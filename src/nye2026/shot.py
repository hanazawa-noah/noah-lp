#!/usr/bin/env python3
"""確認用スクショ(PC 1440 / SP 390)と、文字メインビジュアルからOGP画像(1200x630)を作る。
usage: python3 shot.py [スクショ出力フォルダ]
"""
import sys, os, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image

dst = sys.argv[1] if len(sys.argv) > 1 else 'shots'
os.makedirs(dst, exist_ok=True)
url = pathlib.Path('out/index.html').resolve().as_uri()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h in [('pc', 1440, 900), ('sp', 390, 844)]:
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1 if name == 'pc' else 2)
        pg.goto(url); pg.wait_for_timeout(500)
        pg.screenshot(path=f'{dst}/{name}_top.png')
        pg.screenshot(path=f'{dst}/{name}_full.png', full_page=True)
        pg.close()
    pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.goto(url); pg.add_style_tag(content='.topwrap{display:none}.mv{min-height:630px!important}')
    pg.wait_for_timeout(300)
    pg.locator('.mv').screenshot(path=f'{dst}/ogp.png')
    b.close()
im = Image.open(f'{dst}/ogp.png').convert('RGB')
im.crop((0, 0, 1200, 630)).save('out/img/ogp.jpg', 'JPEG', quality=86, optimize=True)
print('ok', dst)

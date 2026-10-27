#!/usr/bin/env python3
"""確認用スクショ(PC 1440 / SP 390)を撮る。
usage: python3 shot.py [スクショ出力フォルダ]
"""
import sys, os, pathlib
from playwright.sync_api import sync_playwright

dst = sys.argv[1] if len(sys.argv) > 1 else 'shots'
os.makedirs(dst, exist_ok=True)
url = pathlib.Path('out/index.html').resolve().as_uri()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h in [('pc', 1440, 900), ('sp', 390, 844)]:
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1 if name == 'pc' else 2)
        pg.goto(url); pg.wait_for_timeout(1500)
        pg.screenshot(path=f'{dst}/{name}_top.png')
        pg.evaluate('async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}scrollTo(0,0)}'); pg.wait_for_timeout(800)
        pg.screenshot(path=f'{dst}/{name}_full.png', full_page=True)
        pg.close()
    b.close()
print('ok', dst)

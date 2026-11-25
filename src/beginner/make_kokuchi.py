#!/usr/bin/env python3
"""告知用バナー(1920×1080)を作る。LPのヒーローと同じ色・書体・写真でそろえる。
usage: python -X utf8 make_kokuchi.py
出力: dist/beginner_告知バナー_1920x1080.jpg(「特設ページ公開」ラベルあり)と _ラベルなし.jpg
文字は data.json の site から取る。写真は uploads/1.jpg(メインビジュアルの元写真)。
"""
import json, os, pathlib, html
from playwright.sync_api import sync_playwright
from PIL import Image

D = json.load(open('data.json', encoding='utf-8'))
S, T = D['site'], D['theme']
e = html.escape
here = pathlib.Path('.').resolve()
u = lambda p: (here / p).as_uri()
l12, l3 = S['sub'].split('|')                     # 初めての後楽園ホール / 観戦の楽しみ方
name = S['mv']['name']; assert l12.endswith(name)  # 3行に分ける: 初めての / 後楽園ホール / 観戦の楽しみ方
l1, l2 = l12[:-len(name)], name
lead = S['lead'].split('|')[0]                    # チケットの買い方から…ご案内します。
WAKABA = '<svg class="wakaba" viewBox="0 0 24 32"><path d="M0 0l12 8v24L0 22z" fill="#FCC800"/><path d="M24 0L12 8v24l12-10z" fill="#3BAA34"/></svg>'

def page(label):
    lab = f'<p class="lab">{e(label)}</p>' if label else ''
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden}}
body{{background:{T['paper']};color:{T['ink']};font-family:'Noto Sans JP',sans-serif;font-weight:900;display:flex;border-bottom:18px solid {T['blue']}}}
.tx{{flex:1;min-width:0;padding:0 56px 0 84px;display:flex;flex-direction:column;justify-content:center}}
.lab{{align-self:flex-start;font-size:32px;letter-spacing:.14em;line-height:1;background:{T['yellow']};color:{T['blue']};border:4px solid {T['blue']};border-radius:999px;padding:15px 32px 17px;margin-bottom:34px}}
h1{{font-size:98px;line-height:1.26;letter-spacing:.03em;white-space:nowrap}}
h1 span{{display:block}}
.wakaba{{display:inline-block;width:.62em;height:.82em;vertical-align:-.06em;margin-left:.18em}}
.row{{display:flex;align-items:center;gap:28px;margin-top:40px;padding:22px 0;border-top:3px solid {T['ink']};border-bottom:3px solid {T['ink']}}}
.row img{{height:42px;width:auto}}
.row b{{font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:38px;letter-spacing:.08em;line-height:1;white-space:nowrap}}
.lead{{font-weight:700;font-size:31px;line-height:1.75;word-break:auto-phrase;letter-spacing:.03em;margin-top:34px}}
.ph{{flex:none;align-self:center;width:900px;height:860px;position:relative;margin-right:64px;border:5px solid {T['blue']};border-radius:30px;overflow:hidden;background:{T['blue']}}}
.ph img{{position:absolute;height:124%;width:auto;left:50%;top:-5%;transform:translateX(-50%);display:block}}
.cap{{position:absolute;left:0;bottom:0;display:flex;align-items:center;gap:20px;background:{T['blue']};color:#fff;padding:18px 36px 20px 28px;border-top-right-radius:30px}}
.cap small{{font-size:21px;letter-spacing:.12em;line-height:1;background:{T['yellow']};color:{T['blue']};border-radius:999px;padding:11px 20px 12px}}
.cap b{{font-size:42px;letter-spacing:.1em;line-height:1.2}}
.cap i{{font-family:'Barlow Condensed',sans-serif;font-style:normal;font-weight:700;font-size:27px;letter-spacing:.1em;line-height:1;opacity:.9}}
</style></head><body>
<div class="tx">{lab}
<h1><span>{e(l1)}</span><span>{e(l2)}</span><span>{e(l3)}{WAKABA}</span></h1>
<div class="row"><img src="{u('out/img/noah_lockup.png')}" alt=""><b>{e(S['en'])}</b></div>
<p class="lead">{e(lead)}</p>
</div>
<figure class="ph"><img src="{u('uploads/1.jpg')}" alt=""><figcaption class="cap"><small>{e(S['mv']['label'])}</small><b>{e(S['mv']['name'])}</b><i>{e(S['mv']['en'])}</i></figcaption></figure>
</body></html>'''

def page_small():
    """小さく表示する場所用(横480〜640pxくらいに縮んでも読める)。文字はタイトルとNOAHロゴだけ。"""
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden}}
body{{background:{T['paper']};color:{T['ink']};font-family:'Noto Sans JP',sans-serif;font-weight:900;display:flex}}
.tx{{flex:1;min-width:0;padding:0 40px 0 76px;display:flex;flex-direction:column;justify-content:center}}
h1{{font-size:156px;line-height:1.2;letter-spacing:.01em;white-space:nowrap}}
h1 span{{display:block}}
h1 .hl{{color:{T['blue']}}}
.wakaba{{display:inline-block;width:.62em;height:.82em;vertical-align:-.06em;margin-left:.16em}}
.logo{{height:84px;width:auto;align-self:flex-start;margin-top:52px}}
.ph{{flex:none;width:650px;height:1080px;position:relative;overflow:hidden;border-left:14px solid {T['blue']};background:{T['blue']}}}
.ph img{{position:absolute;height:132%;width:auto;left:50%;top:-10%;transform:translateX(-50%);display:block}}
</style></head><body>
<div class="tx">
<h1><span>{e(l1)}{WAKABA}</span><span class="hl">{e(l2)}</span><span>{e(l3)}</span></h1>
<img class="logo" src="{u('out/img/noah_lockup.png')}" alt="">
</div>
<figure class="ph"><img src="{u('uploads/1.jpg')}" alt=""></figure>
</body></html>'''

os.makedirs('dist', exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, src in [('beginner_告知バナー_1920x1080', page('特設ページ公開')), ('beginner_告知バナー_1920x1080_ラベルなし', page('')),
                      ('beginner_告知バナー_1920x1080_小さく表示用', page_small())]:
        tmp = pathlib.Path('dist/_kokuchi.html'); tmp.write_text(src, encoding='utf-8')
        pg = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
        pg.goto(tmp.resolve().as_uri()); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1200)
        over = pg.evaluate('(()=>{const r=document.querySelector(".ph").getBoundingClientRect().left-40;return [...document.querySelectorAll(".tx *")].filter(x=>x.getBoundingClientRect().right>r).map(x=>x.className||x.tagName)})()')
        pg.screenshot(path='dist/_kokuchi.png'); pg.close()
        Image.open('dist/_kokuchi.png').convert('RGB').save(f'dist/{name}.jpg', quality=93, optimize=True, subsampling=0)
        print(name, os.path.getsize(f'dist/{name}.jpg') // 1024, 'KB', 'はみ出し', over)
    b.close()
os.remove('dist/_kokuchi.html'); os.remove('dist/_kokuchi.png')

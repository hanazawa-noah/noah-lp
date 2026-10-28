#!/usr/bin/env python3
"""LP誘導バナー(360×80 と 2倍の 720×160)を作る。 usage: python3 tools/make_banner.py njgp2
src/<slug>/data.json の "banner" を読み、src/<slug>/banner/<slug>_banner_360x80.jpg と _720x160.jpg を出す。

"banner": {
  "bg":    背景(CSSのbackground。LPのKVに合わせる),
  "color": 文字色(省略時 #fff),
  "logo":  協賛ロゴ画像(src/<slug>/ からのパス。省略可。公式データをそのまま書き出したもの。改変禁止),
  "logo_suffix": ロゴの後ろに付ける文字(例 "pres."),
  "logo_color":  ロゴ横の文字色(省略時 color),
  "sponsor_text": ロゴが無いときの1段目の文字(例 "マルハン presents"。省略可),
  "title": 2段目(大会名・英字),
  "sub":   3段目の日付(例 "11.9(月)〜11.28(土)"。数字と曜日は自動で書体を分ける),
  "cta":   3段目の誘導文(例 "特設サイトはこちら")
  "event_logo": 大会ロゴ(白抜きPNG。指定すると「ロゴ大きめ」レイアウトになり、title/sub は使わない),
  "cta_lines": ロゴレイアウト時の右ボタンの文言(行ごとの配列。例 ["特設サイト", "はこちら ▶"])
}
※ スマホでは小さく表示されるので、ロゴがある大会は event_logo 版を基本にする
"""
import base64, html, json, pathlib, re, sys
from playwright.sync_api import sync_playwright

slug = sys.argv[1]
src = pathlib.Path(__file__).resolve().parent.parent / 'src' / slug
B = json.load(open(src / 'data.json', encoding='utf-8'))['banner']
esc = html.escape
GRAIN = ('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22%3E%3Cfilter id=%22n%22%3E'
         '%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%22.9%22 numOctaves=%222%22 stitchTiles=%22stitch%22/%3E'
         '%3CfeColorMatrix values=%220 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .55 0%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22/%3E%3C/svg%3E')

def img_uri(path): return 'data:image/png;base64,' + base64.b64encode((src / path).read_bytes()).decode()
if B.get('logo'):
    top = f'<p class="p"><img src="{img_uri(B["logo"])}" alt="">{esc(B.get("logo_suffix", ""))}</p>'
elif B.get('sponsor_text'):
    top = f'<p class="p">{esc(B["sponsor_text"])}</p>'
else:
    top = ''
# 日付: 「11.9」は英字書体で大きく、「(月)」は小さく
sub = re.sub(r'(\d+\.\d+)', r'<b>\1</b>', esc(B['sub']))
sub = re.sub(r'(\([^)]*\))', r'<i>\1</i>', sub)
C = B.get('color', '#fff')

HTML = f'''<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=block" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:360px;height:80px;overflow:hidden}}
.b{{position:relative;width:360px;height:80px;background:{B['bg']};color:{C};display:flex;flex-direction:column;justify-content:center;align-items:center;text-shadow:0 1px 6px rgba(0,0,0,.35)}}
.b::before{{content:"";position:absolute;inset:0;background:rgba(8,12,30,.18)}}
.b::after{{content:"";position:absolute;inset:0;background:url("{GRAIN}");opacity:.22;mix-blend-mode:overlay}}
.p,.t,.s{{position:relative;z-index:1;white-space:nowrap}}
.p{{display:flex;align-items:flex-end;gap:4px;font-family:Montserrat,'Yu Gothic',Meiryo,sans-serif;font-weight:800;font-size:9px;line-height:1;margin-bottom:4px;color:{B.get('logo_color', C)};text-shadow:none}}
.p img{{height:13px;width:auto;display:block}}
.t{{font-family:Montserrat,'Arial Black',sans-serif;font-weight:800;font-size:22px;letter-spacing:.01em;line-height:1}}
.s{{font-family:'Yu Gothic',Meiryo,sans-serif;font-weight:700;font-size:15px;margin-top:6px;line-height:1;letter-spacing:.02em}}
.s b{{font-family:Montserrat,sans-serif;font-weight:800;font-size:16px}}
.s i{{font-style:normal;font-size:11px}}
</style>
<div class="b">{top}<p class="t">{esc(B['title'])}</p>
<p class="s">{sub}　{esc(B['cta'])} ▶</p></div>'''
if B.get('event_logo'):
    # ロゴ大きめレイアウト: 左に協賛ロゴ+大会ロゴ、右に白いボタン
    HTML = HTML.split('<div class="b">')[0].split('</style>')[0] + f'''
.b{{flex-direction:row;justify-content:space-between;padding:0 10px 0 12px}}
.lg{{position:relative;z-index:1;display:flex;flex-direction:column;align-items:flex-start;gap:6px}}
.lg .p{{margin:0;font-size:12px;gap:5px}}
.lg .p img{{height:19px}}
.ev{{width:246px;height:auto;display:block;filter:drop-shadow(0 1px 4px rgba(0,0,0,.35))}}
.cta{{position:relative;z-index:1;background:#fff;color:#0c1226;text-shadow:none;border-radius:4px;padding:6px 7px;font-family:'Yu Gothic',Meiryo,sans-serif;font-weight:700;font-size:12.5px;line-height:1.3;text-align:center;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.25)}}
</style>
<div class="b"><div class="lg">{top}<img class="ev" src="{img_uri(B['event_logo'])}" alt=""></div>
<p class="cta">{'<br>'.join(esc(x) for x in B.get('cta_lines', [B['cta'] + ' ▶']))}</p></div>'''

out = src / 'banner'
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for scale, size in [(1, '360x80'), (2, '720x160')]:
        pg = b.new_page(viewport={'width': 360, 'height': 80}, device_scale_factor=scale)
        pg.set_content(HTML, wait_until='networkidle'); pg.evaluate('document.fonts.ready')
        # はみ出しチェック(文字が長すぎると横からはみ出す)
        if pg.evaluate("[...document.querySelectorAll('.p,.t,.s,.lg,.cta')].some(e=>e.getBoundingClientRect().right>360||e.scrollWidth>350)"):
            print('※ 文字が長すぎてバナーからはみ出しています。title/sub/cta を短くしてください')
        pg.screenshot(path=str(out / f'{slug}_banner_{size}.jpg'), type='jpeg', quality=92)
    b.close()
print('banner ok:', out)

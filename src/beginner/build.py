#!/usr/bin/env python3
"""初めてのNOAH観戦ガイド(後楽園ホール編) LP builder: data.json -> out/index.html
usage: python3 build.py [--noindex] [--out PATH]
デザインは 2026.10.25 パンフ P04-05「FIRST-TIME VIEWING GUIDE」を踏襲(紙色の地+青枠+黄色の斜めバッジ)
画像は prep_img.py がデザイナー支給データから out/img/ に作る
"""
import json, html, urllib.parse, argparse
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--noindex', action='store_true')
ap.add_argument('--out', default='out/index.html')
args = ap.parse_args()

D = json.load(open('data.json', encoding='utf-8'))
S, T, EV, TK, GD, SG, DY, RL, EN, FQ = D['site'], D['theme'], D['events'], D['tickets'], D['goods'], D['sign'], D['day'], D['rules'], D['enjoy'], D['faq']
esc = html.escape
GTM = 'GTM-KQF9WVX'
title = S['title']

def ext(u): return '' if u.startswith('#') else ' target="_blank" rel="noopener"'
def arrow(u): return '' if u.startswith('#') else ' ↗'
def map_url(q): return 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(q)

def img(name, alt='', cls='', sizes=None, eager=False):
    """out/img/<name>.webp を実寸の width/height 付きで出す"""
    fn = name if '.' in name else name + '.webp'
    w, h = Image.open('out/img/' + fn).size
    c = f' class="{cls}"' if cls else ''
    lz = '' if eager else ' loading="lazy"'
    return f'<img{c} src="img/{fn}" alt="{esc(alt)}" width="{w}" height="{h}"{lz}>'

NAV = [('schedule', '大会日程'), ('ticket', 'チケット'), ('goods', 'グッズ'), ('sign', 'サイン会'), ('day', '当日・アクセス'), ('rules', 'ルール'), ('enjoy', '楽しみ方'), ('faq', 'Q&A')]
def nav_links(): return ''.join(f'<a href="#{i}">{t}</a>' for i, t in NAV)

# 初心者マーク(パンフの見出しに付いているもの)
WAKABA = '<svg class="wakaba" viewBox="0 0 24 32" aria-hidden="true"><path d="M0 0l12 8v24L0 22z" fill="#FCC800"/><path d="M24 0L12 8v24l12-10z" fill="#3BAA34"/></svg>'

def badge(word, no=''):  # 黄色の斜めバッジ(RULE 1 など)
    n = f'<b>{esc(no)}</b>' if no else ''
    return f'<span class="bdg" aria-hidden="true"><i>{esc(word)}</i>{n}</span>'

def bar(ja, sub, step=''):  # 青い帯の見出し
    b = badge('STEP', step) if step else ''
    return f'<div class="bar">{b}<h2 class="bar__t"><span>◎</span>{esc(ja)}</h2><p class="bar__s">{esc(sub)}</p></div>'

def card_hd(ja, en, bdg=''):
    return f'<div class="card__hd"><h3 class="card__ja">{esc(ja)}</h3><span class="card__en">{esc(en)}</span>{bdg}</div>'

def li(xs, cls='notes'): return f'<ul class="{cls}">' + ''.join(f'<li>{esc(x)}</li>' for x in xs) + '</ul>'

# ---------- sections ----------
def quick():
    return ''.join(f'''
        <li><a class="qk" href="{q['href']}"><span class="qk__no">{esc(q['no'])}</span><span class="qk__b"><b>{esc(q['t'])}</b><small>{esc(q['x'])}</small></span><span class="qk__ar">↓</span></a></li>''' for q in D['quick'])

def events():
    out = ''
    for e in EV['list']:
        out += f'''
        <li class="ev" data-date="{e['date']}">
          <p class="ev__d"><span class="ev__md">{esc(e['md'])}</span><span class="ev__dow">{esc(e['dow'])}</span><em class="ev__next">NEXT</em></p>
          <p class="ev__t">{esc(e['title'])}</p>
          <p class="ev__tm">開場 <b>{esc(e['open'])}</b>／試合開始 <b>{esc(e['start'])}</b></p>
          <a class="btn btn--line ev__btn" href="{esc(e['url'])}" target="_blank" rel="noopener">チケット・大会詳細 ↗</a>
        </li>'''
    return out

def playguides():
    return ''.join(f'''
          <a class="pg" href="{esc(p['url'])}" target="_blank" rel="noopener"><span class="pg__n">{esc(p['name'])}</span><span class="pg__s">{esc(p['store'])}</span><b class="btn btn--pri">チケットを購入する ↗</b></a>''' for p in TK['playguides'])

def price():
    P = TK['price']
    rows = ''.join(f'<tr><th>{esc(a)}{f"<small>{esc(c)}</small>" if c else ""}</th><td>{esc(b)}</td></tr>' for a, b, c in P['rows'])
    return f'''<p class="pr__ex">{esc(P['ex'])}</p><table class="pr"><tbody>{rows}</tbody></table><p class="pr__note">{esc(P['note'])}</p>
          <p class="pr__btn"><a class="btn btn--line" href="{esc(P['url'])}" target="_blank" rel="noopener">各大会の席種・座席図を見る ↗</a></p>'''

def tips():
    return ''.join(f'<li><b>{esc(t["t"])}</b><span>{esc(t["x"])}</span></li>' for t in TK['tips'])

def shop_items():
    return ''.join(f'''
            <li><a class="gd" href="{esc(i['url'])}" target="_blank" rel="noopener">{img(i['img'], i['name'])}<span class="gd__n">{esc(i['name'])}</span><span class="gd__p">{esc(i['price'])}</span></a></li>''' for i in GD['shop']['items'])

def steps(xs):
    return ''.join(f'<li><span class="st__no">{k + 1}</span><b>{esc(s["t"])}</b><span>{esc(s["x"])}</span></li>' for k, s in enumerate(xs))

def flow():
    return ''.join(f'<li><span class="fl__tm">{esc(f["time"])}</span><b>{esc(f["t"])}</b><span>{esc(f["x"])}</span></li>' for f in DY['flow'])

def rules():
    r1, r2, r3, r4, r5 = (RL[k] for k in ('r1', 'r2', 'r3', 'r4', 'r5'))
    def hd(r, n): return card_hd(r['ja'], r['en'], badge('RULE', str(n)))
    c1 = ''.join(f'''<figure class="wc"><figcaption><b>{esc(i['name'])}<span class="wc__ar">→</span></b><em class="wc__tag wc__tag--{i['arrow']}">{esc(i['tag'])}</em></figcaption>{img(i['img'], i['name'])}{f'<small>{esc(i["cap"])}</small>' if i.get('cap') else ''}</figure>''' for i in r1['items'])
    c2 = ''.join(f'''<figure class="mf"><figcaption><b>{esc(i['name'])}</b><span>{esc(i['x'])}</span></figcaption>{img(i['img'], i['name'])}</figure>''' for i in r2['items'])
    c4 = ''.join(f'''<figure class="vi"><figcaption>・{esc(i['name'])}</figcaption>{img(i['img'], i['name'])}</figure>''' for i in r4['items'])
    c5 = ''.join(f'''<div class="wl"><div class="wl__tx"><h4>{esc(i['name'])}</h4><p>{i['x']}</p></div>{img(i['img'], i['name'])}</div>''' for i in r5['items'])
    return f'''
      <div class="rl">
        <div class="rl__col">
          <article class="card">{hd(r1, 1)}<div class="card__bd wcs">{c1}</div></article>
          <article class="card">{hd(r2, 2)}<div class="card__bd mfs">{c2}</div></article>
          <article class="card">{hd(r3, 3)}<div class="card__bd rb"><div class="rb__ph"><b>{esc(r3['name'])}</b>{img(r3['img'], r3['name'])}</div><div class="pt"><span class="pt__lab">POINT !</span><p>{esc(r3['point'])}</p></div></div></article>
        </div>
        <article class="card rl__r4">{hd(r4, 4)}<div class="card__bd"><div class="pt pt--top"><span class="pt__lab">POINT !</span><p>{esc(r4['point'])}</p></div><div class="vis">{c4}</div></div></article>
        <article class="card rl__r5">{hd(r5, 5)}<div class="card__bd wls">{c5}</div></article>
      </div>'''

def enjoy():
    out = ''
    for k, i in enumerate(EN['items']):
        note = f'<small>※{esc(i["note"])}</small>' if i.get('note') else ''
        out += f'''
        <article class="ej{' ej--alt' if k % 2 else ''}"><h3 class="ej__t"><em>{esc(i['t'][0])}</em>{esc(i['t'][1])}</h3>
          <div class="ej__bd">{img(i['img'], i['t'][0].strip('“”'))}<p>{esc(i['x'])}{note}</p></div>
          <a class="btn btn--line ej__btn" href="{esc(i['url'])}"{ext(i['url'])}>{esc(i['btn'])}{arrow(i['url'])}</a></article>'''
    return out

def faq():
    return ''.join(f'<details class="fq"><summary><span>Q</span>{esc(i["q"])}</summary><p>{esc(i["a"])}</p></details>' for i in FQ['items'])

def footer_links(): return ''.join(f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])}</a></li>' for l in D['footer_links'])

noindex = '<meta name="robots" content="noindex,nofollow">\n  ' if args.noindex else ''
desc = f"{S['sub']}。チケットの買い方、グッズの事前購入、サイン会の参加方法、プロレスのルールまで。後楽園ホールで初めてNOAHを観戦する方へのご案内。プロレスリング・ノア。"
V = DY['venue']

# ---------- CSS ----------
CSS = f'''
:root{{--paper:{T['paper']};--ink:{T['ink']};--bl:{T['blue']};--sky:{T['sky']};--yl:{T['yellow']};--line:rgba(35,25,22,.16);--max:1120px;
--ff-en:'Barlow Condensed','DIN Condensed','Helvetica Neue',Helvetica,Arial,sans-serif;
--ff-ja:'Hiragino Kaku Gothic ProN','Hiragino Sans','Noto Sans JP',Meiryo,sans-serif;--ff-hd:'Noto Sans JP','Hiragino Kaku Gothic ProN','Hiragino Sans',Meiryo,sans-serif;}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%;scroll-padding-top:84px}}
body{{background:var(--paper);color:var(--ink);font-family:var(--ff-ja);font-weight:600;font-size:15px;line-height:1.85;letter-spacing:.03em;overflow-x:hidden}}
img{{max-width:100%;height:auto;display:block}}
a{{color:inherit;text-decoration:none}}
ul,ol{{list-style:none}}
table{{border-collapse:collapse;width:100%}}
.wrap{{width:min(100% - 40px,var(--max));margin:0 auto}}
.sec{{padding:72px 0}}
.sec__lead{{font-size:16px;line-height:1.9;margin:0 0 30px}}
h1,h2,h3,h4,b,.sec__lead,.hero__lead,.qk small,.ev__t,.bar__s,.pt p,.gd__n,.last__s{{word-break:auto-phrase}}
.wakaba{{display:inline-block;width:.62em;height:.82em;vertical-align:-.06em;margin-left:.2em}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:50px;padding:10px 26px;border-radius:999px;font-family:var(--ff-hd);font-weight:900;font-size:15px;letter-spacing:.06em;line-height:1.4;text-align:center;transition:.2s}}
.btn--pri{{background:var(--bl);color:#fff}}
.btn--pri:hover,.pg:hover .btn--pri{{background:var(--sky)}}
.btn--line{{background:#fff;color:var(--bl);border:2px solid var(--bl)}}
.btn--line:hover{{background:var(--bl);color:#fff}}
.btn--yl{{background:var(--yl);color:var(--ink);border:3px solid var(--bl)}}
.btn--yl:hover{{transform:translateY(-2px)}}
.notes li{{position:relative;padding-left:1.3em;font-size:13px;line-height:1.8;font-weight:500}}
.notes li::before{{content:"※";position:absolute;left:0}}

/* 黄色の斜めバッジ */
.bdg{{display:inline-flex;align-items:baseline;gap:.08em;font-family:var(--ff-en);font-style:italic;font-weight:800;font-size:40px;line-height:1;color:var(--yl);-webkit-text-stroke:7px var(--bl);paint-order:stroke fill;text-shadow:3px 3px 0 var(--bl);transform:rotate(-7deg);letter-spacing:.01em;white-space:nowrap}}
.bdg i{{font-style:inherit}}
.bdg b{{font-size:1.45em;font-weight:800}}

/* 青帯の見出し */
.bar{{position:relative;display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 22px;background:var(--bl);color:#fff;border-radius:16px;padding:14px 26px 15px;margin-bottom:34px}}
.bar .bdg{{position:absolute;right:18px;top:-30px;font-size:44px;text-shadow:3px 3px 0 var(--bl),0 0 0 #fff;filter:drop-shadow(2px 0 0 #fff) drop-shadow(-2px 0 0 #fff) drop-shadow(0 2px 0 #fff) drop-shadow(0 -2px 0 #fff)}}
.bar__t{{font-family:var(--ff-hd);font-weight:900;font-size:clamp(21px,2.5vw,28px);letter-spacing:.06em;line-height:1.4}}
.bar__t span{{margin-right:.15em}}
.bar__s{{font-size:14px;font-weight:700}}

/* 青枠のカード */
.card{{position:relative;background:#fff;border:3px solid var(--bl);border-radius:18px}}
.card + .card{{margin-top:26px}}
.card__hd{{position:relative;display:flex;align-items:center;gap:14px;padding:14px 26px 12px;border-bottom:2px solid var(--bl)}}
.card__ja{{font-family:var(--ff-hd);font-weight:900;font-size:20px;color:var(--bl);letter-spacing:.16em;line-height:1.4}}
.card__en{{font-family:var(--ff-en);font-weight:700;font-size:17px;letter-spacing:.08em;padding-left:14px;border-left:3px solid var(--ink);line-height:1.1}}
.card__hd .bdg{{position:absolute;right:14px;top:-20px}}
.card__bd{{padding:24px 26px 26px}}

/* header */
.topwrap{{position:sticky;top:0;z-index:100;background:var(--paper);border-bottom:3px solid var(--bl)}}
.header{{display:flex;align-items:center;justify-content:space-between;gap:16px;height:66px}}
.header__logo{{display:flex;align-items:center;gap:12px;flex:none}}
.header__logo img{{height:26px;width:auto}}
.header__nav{{display:flex;gap:18px;font-family:var(--ff-hd);font-weight:700;font-size:13px;white-space:nowrap}}
.header__nav a{{padding:4px 0;border-bottom:2px solid transparent}}
.header__nav a:hover{{border-color:var(--bl);color:var(--bl)}}
.header__cta{{min-height:40px;padding:6px 20px;font-size:13px;flex:none}}
.spnav{{display:none}}

/* hero */
.hero{{padding:52px 0 28px}}
.hero__en{{font-family:var(--ff-en);font-weight:800;font-size:min(9.1vw,104px);line-height:.95;letter-spacing:.01em;white-space:nowrap}}
.hero__row{{display:flex;align-items:center;gap:10px 30px;margin-top:22px;padding:14px 0;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}}
.hero__row img{{height:36px;width:auto;flex:none}}
.hero__ja{{font-family:var(--ff-hd);font-weight:900;font-size:clamp(20px,3vw,34px);letter-spacing:.08em;line-height:1.35}}
.hero__lead{{font-size:16px;line-height:2;margin-top:26px}}
.hero__ph{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:30px}}
.hero__ph img{{width:100%;aspect-ratio:4/3;object-fit:cover}}
.quick{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:34px}}
.qk{{display:flex;align-items:center;gap:14px;height:100%;padding:16px 18px;background:var(--bl);color:#fff;border-radius:16px;transition:.2s}}
.qk:hover{{background:var(--sky);transform:translateY(-2px)}}
.qk__no{{flex:none;display:flex;align-items:center;justify-content:center;width:46px;height:46px;border-radius:50%;background:var(--yl);color:var(--bl);font-family:var(--ff-en);font-style:italic;font-weight:800;font-size:30px;line-height:1;padding-right:3px}}
.qk__b{{flex:1;display:flex;flex-direction:column;gap:2px}}
.qk__b b{{font-family:var(--ff-hd);font-weight:900;font-size:18px;letter-spacing:.06em;line-height:1.4}}
.qk__b small{{font-size:12px;font-weight:600;line-height:1.5;opacity:.92}}
.qk__ar{{flex:none;font-weight:900}}

/* schedule */
.evs{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}
.ev{{display:flex;flex-direction:column;gap:6px;background:#fff;border:3px solid var(--bl);border-radius:16px;padding:18px 20px 20px}}
.ev[hidden]{{display:none}}
.ev__d{{display:flex;align-items:center;gap:10px}}
.ev__md{{font-family:var(--ff-en);font-weight:800;font-size:50px;line-height:1;color:var(--bl)}}
.ev__dow{{font-family:var(--ff-hd);font-weight:900;font-size:13px;line-height:1;background:var(--bl);color:#fff;border-radius:999px;padding:6px 10px}}
.ev__next{{display:none;margin-left:auto;font-family:var(--ff-en);font-style:italic;font-weight:800;font-size:22px;color:var(--yl);-webkit-text-stroke:5px var(--bl);paint-order:stroke fill;transform:rotate(-7deg)}}
.ev.is-next .ev__next{{display:block}}
.ev__t{{font-family:var(--ff-hd);font-weight:900;font-size:15px;line-height:1.55;flex:1}}
.ev__tm{{font-size:13px}}
.ev__tm b{{font-family:var(--ff-en);font-size:19px;font-weight:700;letter-spacing:.04em}}
.ev__btn{{margin-top:8px;min-height:44px;font-size:14px;padding:8px 14px}}
.more{{text-align:center;margin-top:30px}}

/* ticket */
.pgs{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}
.pg{{display:flex;flex-direction:column;gap:8px;padding:20px;background:var(--paper);border-radius:12px}}
.pg__n{{font-family:var(--ff-hd);font-weight:900;font-size:20px;line-height:1.4}}
.pg__s{{flex:1;font-size:13px;line-height:1.7;font-weight:500}}
.pg .btn{{margin-top:6px}}
.tk2{{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:26px;margin-top:26px}}
.tk2 .card + .card{{margin-top:0}}
.pr__ex{{display:inline-block;font-size:12px;font-weight:700;border:1px solid var(--ink);padding:1px 10px;margin-bottom:8px}}
.pr th,.pr td{{padding:9px 4px;border-bottom:1px solid var(--line);font-size:15px;text-align:left;font-weight:700}}
.pr th small{{font-size:11px;font-weight:700;color:#fff;background:var(--sky);border-radius:999px;padding:2px 9px;margin-left:8px;vertical-align:1px}}
.pr td{{text-align:right;font-family:var(--ff-hd);font-weight:900;font-size:17px;white-space:nowrap}}
.pr__note{{font-size:12.5px;font-weight:500;line-height:1.75;margin-top:12px}}
.pr__btn{{margin-top:14px}}
.pr__btn .btn{{width:100%;font-size:14px}}
.tips li{{padding:14px 0;border-bottom:1px dashed var(--bl)}}
.tips li:first-child{{padding-top:0}}
.tips li:last-child{{border:0;padding-bottom:0}}
.tips b{{display:block;font-family:var(--ff-hd);font-weight:900;font-size:16px;color:var(--bl);line-height:1.5;margin-bottom:2px}}
.tips span{{font-size:13.5px;font-weight:500;line-height:1.8}}
.tk__notes{{margin-top:22px}}

/* goods */
.lab{{display:inline-block;font-family:var(--ff-hd);font-weight:900;font-size:12px;letter-spacing:.1em;background:var(--yl);border:2px solid var(--bl);color:var(--bl);border-radius:999px;padding:1px 14px;margin-bottom:8px}}
.gds__tx{{font-size:14.5px;line-height:1.9}}
.gds{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:20px}}
.gd{{display:flex;flex-direction:column;gap:4px;height:100%;transition:.2s}}
.gd:hover{{transform:translateY(-3px)}}
.gd img{{width:100%;aspect-ratio:1;object-fit:cover;border:1px solid var(--line);border-radius:10px;background:#fff}}
.gd__n{{font-size:13px;font-weight:700;line-height:1.5;margin-top:4px;flex:1}}
.gd__p{{font-family:var(--ff-en);font-weight:700;font-size:21px;line-height:1.2;color:var(--bl)}}
.gds__ft{{display:flex;flex-wrap:wrap;align-items:center;gap:12px 22px;margin-top:22px}}
.gds__ft small{{font-size:12.5px;font-weight:500}}
.vn{{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,6fr);gap:28px;align-items:start}}
.vn img{{width:100%;border-radius:10px}}
.chk{{margin-top:12px}}
.chk li{{position:relative;padding:7px 0 7px 30px;font-size:14px;line-height:1.7;border-bottom:1px dashed var(--bl)}}
.chk li::before{{content:"";position:absolute;left:4px;top:13px;width:14px;height:8px;border-left:3px solid var(--bl);border-bottom:3px solid var(--bl);transform:rotate(-45deg)}}
.vn .notes{{margin-top:10px}}

/* sign / steps */
.sts{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;counter-reset:s}}
.sts li{{position:relative;display:flex;flex-direction:column;gap:4px;background:var(--paper);border-radius:12px;padding:30px 16px 18px;margin-top:20px}}
.st__no{{position:absolute;left:14px;top:-20px;display:flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:50%;background:var(--yl);border:3px solid var(--bl);color:var(--bl);font-family:var(--ff-en);font-style:italic;font-weight:800;font-size:26px;line-height:1;padding-right:2px}}
.sts b{{font-family:var(--ff-hd);font-weight:900;font-size:15.5px;line-height:1.5;color:var(--bl)}}
.sts span:last-child{{font-size:13px;font-weight:500;line-height:1.75}}
.sg2{{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:28px;margin-top:28px;align-items:start}}
.exm{{border:2px dashed var(--bl);border-radius:12px;padding:18px 20px}}
.exm__t{{font-family:var(--ff-hd);font-weight:900;font-size:16px;line-height:1.5;margin-bottom:8px}}
.exm dl{{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;font-size:14px}}
.exm dt{{font-size:12px;font-weight:700;color:#fff;background:var(--bl);border-radius:999px;padding:1px 12px;align-self:center;text-align:center}}
.exm dd{{font-family:var(--ff-hd);font-weight:900;font-size:17px}}
.sg__btn{{text-align:center;margin-top:26px}}

/* day */
.fls{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}
.fls li{{position:relative;display:flex;flex-direction:column;gap:2px;background:var(--paper);border-radius:12px;padding:16px 18px 18px}}
.fls li + li::before{{content:"";position:absolute;left:-13px;top:50%;border-style:solid;border-width:9px 0 9px 11px;border-color:transparent transparent transparent var(--bl);transform:translateY(-50%)}}
.fl__tm{{font-family:var(--ff-en);font-weight:800;font-size:34px;line-height:1.1;color:var(--bl)}}
.fls li:nth-child(2) .fl__tm{{font-family:var(--ff-hd);font-weight:900;font-size:22px;line-height:1.7}}
.fls b{{font-family:var(--ff-hd);font-weight:900;font-size:17px;line-height:1.5}}
.fls span:last-child{{font-size:13px;font-weight:500;line-height:1.75}}
.fl__note{{margin-top:14px}}
.ac{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:20px 30px;align-items:center}}
.ac__n{{font-family:var(--ff-hd);font-weight:900;font-size:24px;line-height:1.4}}
.ac__a{{font-size:14px}}
.ac ul{{margin-top:8px}}
.ac li{{position:relative;padding-left:18px;font-size:15px;font-weight:700;line-height:1.8}}
.ac li::before{{content:"";position:absolute;left:0;top:.62em;width:10px;height:10px;border-radius:50%;background:var(--bl)}}
.mns{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}}
.mns b{{display:block;font-family:var(--ff-hd);font-weight:900;font-size:16px;color:var(--bl);line-height:1.5;margin-bottom:4px}}
.mns span{{font-size:13.5px;font-weight:500;line-height:1.8}}

/* rules */
.rl{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:34px 26px;margin-top:44px}}
.rl .card + .card{{margin-top:34px}}
.rl__r4,.rl__r5{{margin-top:0!important}}
.rl__r5{{grid-column:1/-1}}
.pt__lab{{display:inline-block;font-family:var(--ff-en);font-weight:700;font-size:14px;letter-spacing:.08em;line-height:1;border:2px solid var(--ink);padding:3px 8px}}
.pt p{{font-family:var(--ff-hd);font-weight:900;font-size:15.5px;line-height:1.9;color:var(--bl);letter-spacing:.08em;margin-top:8px}}
.pt--top{{padding-bottom:14px;margin-bottom:18px;border-bottom:1px solid var(--ink)}}
.wcs,.mfs{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.wc figcaption{{display:flex;flex-direction:column;align-items:flex-start;gap:4px;font-family:var(--ff-hd);font-weight:900;font-size:15px;margin-bottom:10px}}
.wc__ar{{font-weight:900;margin-left:6px}}
.wc__tag{{font-style:normal;font-family:var(--ff-hd);font-weight:900;font-size:17px;color:#fff;background:var(--bl);border-radius:999px;padding:0 12px;line-height:1.7;white-space:nowrap}}
.wc__tag--up::after{{content:"↑";margin-left:2px}}
.wc__tag--down::after{{content:"↓";margin-left:2px}}
.wc img,.mf img{{width:100%;aspect-ratio:5/4;object-fit:cover}}
.wc small{{display:block;font-size:12px;font-weight:500;margin-top:6px}}
.mf{{display:flex;flex-direction:column}}
.mf figcaption{{flex:1;display:flex;flex-direction:column;gap:2px;margin-bottom:10px}}
.mf b{{font-family:var(--ff-hd);font-weight:900;font-size:16px;border-bottom:1px solid var(--ink);padding-bottom:2px}}
.mf span{{font-size:13px;font-weight:700;line-height:1.7}}
.rb{{display:grid;grid-template-columns:1fr;gap:16px}}
.rb__ph img{{width:100%;aspect-ratio:16/10;object-fit:cover}}
.rl__col{{display:flex;flex-direction:column}}
.rl__col>.card:last-child{{flex:1}}
.rb__ph b{{display:block;font-family:var(--ff-hd);font-weight:900;font-size:16px;margin-bottom:8px}}
.rb .pt{{border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);padding:16px 0}}
.vis{{display:grid;grid-template-columns:1fr 1fr;gap:18px 16px}}
.vi figcaption{{font-family:var(--ff-hd);font-weight:900;font-size:13.5px;line-height:1.5;margin-bottom:6px;min-height:2.9em;display:flex;align-items:flex-end}}
.vi img{{width:100%;aspect-ratio:1;object-fit:cover}}
.vi:last-child{{grid-column:1/-1;width:calc(50% - 8px);margin:0 auto}}
.wls{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px 30px}}
.wl{{display:grid;grid-template-columns:minmax(0,1fr) 46%;gap:14px;align-items:start}}
.wl h4{{font-family:var(--ff-hd);font-weight:900;font-size:17px;color:var(--sky);line-height:1.5;border-bottom:1px solid var(--ink);padding-bottom:4px;margin-bottom:8px}}
.wl p{{font-size:13px;font-weight:500;line-height:1.85}}
.wl p b{{font-family:var(--ff-hd);font-weight:900;font-size:14px}}
.wl img{{width:100%;aspect-ratio:1;object-fit:cover}}

/* enjoy(青地) */
.enjoy{{background:var(--bl);padding:76px 0 84px}}
.enjoy__t{{display:flex;align-items:center;justify-content:center;gap:18px;color:#fff;font-family:var(--ff-hd);font-weight:900;font-size:clamp(22px,3.2vw,34px);letter-spacing:.06em;line-height:1.4;margin-bottom:36px;text-align:center}}
.enjoy__t::before,.enjoy__t::after{{content:"";flex:none;width:44px;height:3px;background:#fff;transform:rotate(48deg)}}
.enjoy__t::after{{transform:rotate(-48deg)}}
.ejs{{display:flex;flex-wrap:wrap;justify-content:center;gap:22px}}
.ej{{display:flex;flex-direction:column;width:calc((100% - 44px)/3);background:#fff;border-radius:10px;padding:20px 22px 22px}}
.ej--alt{{background:var(--paper)}}
.ej__t{{font-family:var(--ff-hd);font-weight:900;font-size:19px;line-height:1.5;text-align:center;letter-spacing:.06em;border-bottom:3px solid var(--bl);padding-bottom:6px;margin-bottom:16px}}
.ej__t em{{font-style:normal;font-size:1.25em}}
.ej__bd{{flex:1}}
.ej__bd img{{width:100%;aspect-ratio:4/3;object-fit:cover;border:1px solid var(--line)}}
.ej__bd p{{font-size:13.5px;font-weight:500;line-height:1.9;margin-top:12px}}
.ej__bd small{{display:block;font-size:12px;margin-top:6px}}
.ej__btn{{margin-top:16px;min-height:44px;font-size:14px}}

/* faq */
.fqs{{background:#fff;border:3px solid var(--bl);border-radius:18px;padding:6px 26px}}
.fq{{border-bottom:1px dashed var(--bl)}}
.fq:last-child{{border:0}}
.fq summary{{position:relative;display:flex;align-items:baseline;gap:12px;cursor:pointer;list-style:none;padding:16px 34px 16px 0;font-family:var(--ff-hd);font-weight:900;font-size:16px;line-height:1.6}}
.fq summary::-webkit-details-marker{{display:none}}
.fq summary span{{flex:none;font-family:var(--ff-en);font-style:italic;font-weight:800;font-size:26px;line-height:1;color:var(--bl)}}
.fq summary::after{{content:"＋";position:absolute;right:0;top:50%;transform:translateY(-50%);color:var(--bl);font-weight:900}}
.fq[open] summary::after{{content:"－"}}
.fq p{{font-size:14px;font-weight:500;line-height:1.9;padding:0 0 18px 34px}}

/* last cta */
.last{{padding:20px 0 80px;text-align:center}}
.last__t{{font-family:var(--ff-hd);font-weight:900;font-size:clamp(22px,3.4vw,36px);line-height:1.5;letter-spacing:.06em}}
.last__s{{font-size:15px;margin-top:8px}}
.last__b{{display:flex;flex-wrap:wrap;justify-content:center;gap:14px;margin-top:26px}}
.last__b .btn{{min-height:60px;min-width:270px;font-size:17px}}

/* footer */
.footer{{border-top:3px solid var(--bl);padding:48px 0 40px;text-align:center}}
.footer__logo{{width:min(300px,74%);margin:0 auto 24px}}
.footer__links{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 26px;font-size:13px;margin-bottom:22px}}
.footer__links a{{white-space:nowrap;border-bottom:1px solid transparent}}
.footer__links a:hover{{border-color:var(--ink)}}
.footer__copy{{font-family:var(--ff-en);font-size:13px;letter-spacing:.1em}}

.sp{{display:none}}
@media (max-width:1180px){{.header__nav{{gap:13px;font-size:12px}}}}
/* ---- SP ---- */
@media (max-width:900px){{
  html{{scroll-padding-top:104px}}
  body{{font-size:14px}}
  .sp{{display:inline}}
  .wrap{{width:min(100% - 32px,var(--max))}}
  .sec{{padding:52px 0}}
  .sec__lead{{font-size:14.5px;margin-bottom:24px}}
  .header{{height:54px}}
  .header__logo img{{height:20px}}
  .header__nav{{display:none}}
  .header__cta{{min-height:36px;padding:4px 16px;font-size:12px}}
  .spnav{{display:flex;gap:20px;overflow-x:auto;white-space:nowrap;padding:0 16px 9px;font-family:var(--ff-hd);font-weight:700;font-size:13px;scrollbar-width:none}}
  .spnav::-webkit-scrollbar{{display:none}}
  .bdg{{font-size:30px;-webkit-text-stroke-width:6px}}
  .bar{{flex-direction:column;gap:0;border-radius:14px;padding:12px 18px 13px;margin-bottom:26px}}
  .bar .bdg{{right:8px;top:-34px;font-size:30px}}
  .bar__s{{font-size:12.5px}}
  .card{{border-radius:16px}}
  .card__hd{{padding:12px 16px 10px;gap:10px}}
  .card__ja{{font-size:16.5px;letter-spacing:.1em}}
  .card__en{{font-size:14px;padding-left:10px}}
  .card__hd .bdg{{right:8px;top:-18px}}
  .card__bd{{padding:18px 16px 20px}}
  .hero{{padding:30px 0 16px}}
  .hero__en{{font-size:19.5vw;white-space:normal}}
  .hero__row{{flex-direction:column;align-items:flex-start;margin-top:16px;padding:12px 0}}
  .hero__row img{{height:26px}}
  .hero__lead{{font-size:14.5px;line-height:1.95;margin-top:18px}}
  br.pc{{display:none}}
  .hero__ph{{grid-template-columns:1fr 1fr;gap:8px;margin-top:22px}}
  .quick{{grid-template-columns:1fr;gap:10px;margin-top:22px}}
  .qk{{padding:12px 16px}}
  .qk__no{{width:40px;height:40px;font-size:26px}}
  .qk__b b{{font-size:16.5px}}
  .evs{{grid-template-columns:1fr;gap:12px}}
  .ev{{padding:14px 16px 16px}}
  .ev__md{{font-size:42px}}
  .pgs{{grid-template-columns:1fr;gap:12px}}
  .pg{{padding:16px}}
  .pg__n{{font-size:18px}}
  .tk2{{grid-template-columns:1fr;gap:22px;margin-top:22px}}
  .gds{{grid-template-columns:1fr 1fr;gap:16px 12px}}
  .gds__ft .btn{{width:100%}}
  .vn{{grid-template-columns:1fr;gap:16px}}
  .sts{{grid-template-columns:1fr;gap:0}}
  .sts li{{padding:26px 16px 16px}}
  .sg2{{grid-template-columns:1fr;gap:20px;margin-top:22px}}
  .sg__btn .btn{{width:100%}}
  .fls{{grid-template-columns:1fr;gap:16px}}
  .fls li + li::before{{left:50%;top:-14px;transform:translateX(-50%) rotate(90deg)}}
  .ac{{grid-template-columns:1fr}}
  .ac .btn{{width:100%}}
  .ac__n{{font-size:21px}}
  .mns{{grid-template-columns:1fr;gap:16px}}
  .rl{{grid-template-columns:1fr;gap:30px;margin-top:36px}}
  .rl .card + .card{{margin-top:30px}}
  .wcs,.mfs{{gap:12px}}
  .wc figcaption{{font-size:13.5px}}
  .wc__tag{{font-size:14px;padding:0 9px}}
  .mf b{{font-size:14.5px}}
  .mf span{{font-size:12px}}
  .rb{{gap:14px}}
  .pt p{{font-size:14.5px;letter-spacing:.04em}}
  .vis{{gap:14px 12px}}
  .vi figcaption{{font-size:12.5px}}
  .wls{{grid-template-columns:1fr;gap:22px}}
  .wl{{grid-template-columns:minmax(0,1fr) 40%}}
  .enjoy{{padding:56px 0 60px}}
  .enjoy__t{{gap:10px;margin-bottom:26px}}
  .enjoy__t::before,.enjoy__t::after{{width:28px}}
  .ejs{{gap:16px}}
  .ej{{width:100%;padding:18px 16px 18px}}
  .fqs{{padding:4px 16px;border-radius:16px}}
  .fq summary{{font-size:14.5px;padding:14px 28px 14px 0;gap:10px}}
  .fq p{{font-size:13.5px;padding-left:0}}
  .last{{padding:8px 0 60px}}
  .last__b .btn{{width:100%;min-width:0}}
  .footer__links{{gap:8px 18px;font-size:12px}}
}}
'''

# ---------- HTML ----------
HTML = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {noindex}<title>{esc(title)}｜プロレスリング・ノア</title>
  <meta name="description" content="{esc(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}｜プロレスリング・ノア">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:site_name" content="{esc(S['short'])}｜プロレスリング・ノア">
  <meta property="og:url" content="{esc(S['lp_url'])}">
  <meta property="og:image" content="{esc(S['lp_url'])}img/ogp.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@noah_ghc">
  <meta name="theme-color" content="{T['blue']}">
  <link rel="icon" href="img/noah_badge.png">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,700;0,800;1,800&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{GTM}');</script>
  <!-- End Google Tag Manager -->
  <style>{CSS}</style>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->

<div class="topwrap">
  <header class="header wrap">
    <a href="#top" class="header__logo">{img('noah_lockup.png', 'PRO WRESTLING NOAH', eager=True)}</a>
    <nav class="header__nav">{nav_links()}</nav>
    <a class="btn btn--pri header__cta" href="#ticket">チケット購入</a>
  </header>
  <nav class="spnav">{nav_links()}</nav>
</div>

<main id="top">
  <section class="hero">
    <div class="wrap">
      <p class="hero__en">FIRST-TIME <br class="sp">VIEWING GUIDE</p>
      <div class="hero__row">{img('noah_lockup.png', 'PRO WRESTLING NOAH', eager=True)}<h1 class="hero__ja">{esc(S['sub'])}{WAKABA}</h1></div>
      <p class="hero__lead">{esc(S['lead']).replace('|', '<br class="pc">')}</p>
      <div class="hero__ph">{img('r1_junior', 'ジュニアヘビー級の空中戦', eager=True)}{img('en_oshi', '声援を送る観客', eager=True)}{img('r2_tag', 'タッグマッチ', eager=True)}{img('r3_rope', 'ロープブレイク', eager=True)}</div>
      <ol class="quick">{quick()}
      </ol>
    </div>
  </section>

  <section id="schedule" class="sec">
    <div class="wrap">
      {bar('後楽園ホールの大会日程', 'まずは行きたい大会を選ぼう！')}
      <p class="sec__lead">{esc(EV['lead'])}</p>
      <ul class="evs">{events()}
      </ul>
      <p class="more"><a class="btn btn--line" href="{esc(EV['more_url'])}" target="_blank" rel="noopener">この先の日程・ほかの会場を見る ↗</a></p>
    </div>
  </section>

  <section id="ticket" class="sec">
    <div class="wrap">
      {bar('チケットを買おう', 'チケットは各プレイガイドで販売中！', '1')}
      <p class="sec__lead">{esc(TK['lead'])}</p>
      <article class="card">{card_hd('プレイガイド', 'PLAY GUIDE')}
        <div class="card__bd"><div class="pgs">{playguides()}
        </div></div>
      </article>
      <div class="tk2">
        <article class="card">{card_hd(TK['price']['title'], 'PRICE')}
          <div class="card__bd">{price()}</div>
        </article>
        <article class="card">{card_hd('知っておくと便利', 'TIPS')}
          <div class="card__bd"><ul class="tips">{tips()}</ul></div>
        </article>
      </div>
      {li(TK['notes'], 'notes tk__notes')}
    </div>
  </section>

  <section id="goods" class="sec">
    <div class="wrap">
      {bar('グッズを用意しよう', 'グッズは事前に買って行ける！', '2')}
      <p class="sec__lead">{esc(GD['lead'])}</p>
      <article class="card">{card_hd(GD['shop']['title'], GD['shop']['en'])}
        <div class="card__bd">
          <span class="lab">{esc(GD['shop']['label'])}</span>
          <p class="gds__tx">{esc(GD['shop']['text'])}</p>
          <ul class="gds">{shop_items()}
          </ul>
          <div class="gds__ft"><a class="btn btn--pri" href="{esc(GD['shop']['url'])}" target="_blank" rel="noopener">{esc(GD['shop']['btn'])} ↗</a><small>※{esc(GD['shop']['note'])}</small></div>
        </div>
      </article>
      <article class="card">{card_hd(GD['venue']['title'], 'AT THE VENUE')}
        <div class="card__bd vn">{img(GD['venue']['img'], '会場のグッズ売店')}
          <div><span class="lab">{esc(GD['venue']['label'])}</span>
            <p class="gds__tx">{esc(GD['venue']['text'])}</p>
            {li(GD['venue']['points'], 'chk')}
            {li([GD['venue']['note']])}
          </div>
        </div>
      </article>
    </div>
  </section>

  <section id="sign" class="sec">
    <div class="wrap">
      {bar('サイン会に参加しよう', 'グッズを買うと、選手のサインがもらえる！', '3')}
      <p class="sec__lead">{esc(SG['lead'])}</p>
      <article class="card">{card_hd('参加の流れ', 'HOW TO JOIN')}
        <div class="card__bd">
          <ol class="sts">{steps(SG['steps'])}</ol>
          <div class="sg2">
            <div class="exm"><span class="lab">{esc(SG['example']['label'])}</span><p class="exm__t">{esc(SG['example']['title'])}</p><dl>{''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in SG['example']['rows'])}</dl></div>
            {li(SG['notes'])}
          </div>
          <p class="sg__btn"><a class="btn btn--pri" href="{esc(SG['url'])}" target="_blank" rel="noopener">{esc(SG['btn'])} ↗</a></p>
        </div>
      </article>
    </div>
  </section>

  <section id="day" class="sec">
    <div class="wrap">
      {bar('当日の流れとアクセス', '会場は水道橋駅・後楽園駅から徒歩約3分！')}
      <p class="sec__lead">{esc(DY['lead'])}</p>
      <article class="card">{card_hd('当日の流れ', 'TIMELINE')}
        <div class="card__bd"><ol class="fls">{flow()}</ol>{li([DY['flow_note']], 'notes fl__note')}</div>
      </article>
      <article class="card">{card_hd('アクセス', 'ACCESS')}
        <div class="card__bd ac">
          <div><p class="ac__n">{esc(V['name'])}</p><p class="ac__a">{esc(V['addr'])}</p><ul>{''.join(f'<li>{esc(x)}</li>' for x in V['access'])}</ul></div>
          <a class="btn btn--pri" href="{map_url(V['map'])}" target="_blank" rel="noopener">Googleマップで見る ↗</a>
        </div>
      </article>
      <article class="card">{card_hd('観戦マナー', 'MANNERS')}
        <div class="card__bd"><ul class="mns">{''.join(f'<li><b>{esc(m["t"])}</b><span>{esc(m["x"])}</span></li>' for m in DY['manners'])}</ul></div>
      </article>
    </div>
  </section>

  <section id="rules" class="sec">
    <div class="wrap">
      {bar(RL['title'], RL['sub'])}{rules()}
    </div>
  </section>

  <section id="enjoy" class="enjoy">
    <div class="wrap">
      <h2 class="enjoy__t">{esc(EN['title'])}</h2>
      <div class="ejs">{enjoy()}
      </div>
    </div>
  </section>

  <section id="faq" class="sec">
    <div class="wrap">
      {bar('よくある質問', '気になることは、ここでチェック！')}
      <div class="fqs">{faq()}</div>
      <p class="more"><a class="btn btn--line" href="{esc(FQ['url'])}" target="_blank" rel="noopener">公式サイトのQ&amp;Aをもっと見る ↗</a></p>
    </div>
  </section>

  <section class="last">
    <div class="wrap">
      <p class="last__t">さあ、後楽園ホールへ。{WAKABA}</p>
      <p class="last__s">はじめての一歩は、チケットから。</p>
      <div class="last__b"><a class="btn btn--yl" href="#schedule">大会日程を見る</a><a class="btn btn--pri" href="#ticket">チケットを買う</a></div>
    </div>
  </section>
</main>

<footer class="footer">
  <div class="wrap">
    {img('noah_lockup.png', 'PRO WRESTLING NOAH', 'footer__logo')}
    <ul class="footer__links">{footer_links()}</ul>
    <p class="footer__copy">&copy; CyberFight Inc. All Rights Reserved.</p>
  </div>
</footer>
<script>
/* 終わった大会を隠し、次の大会に NEXT を付ける */
(function(){{var n=new Date(),t=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2),f=0;
document.querySelectorAll('.ev[data-date]').forEach(function(e){{if(e.dataset.date<t){{e.hidden=true}}else if(!f){{e.classList.add('is-next');f=1}}}});}})();
</script>
</body>
</html>
'''
open(args.out, 'w', encoding='utf-8').write(HTML)
print('wrote', args.out, len(HTML.encode()), 'bytes', '(noindex)' if args.noindex else '')

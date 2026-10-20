#!/usr/bin/env python3
"""NOAH "THE NEW YEAR" EVE 2026 LP builder: data.json (+ unannounced.json) -> out/index.html
usage: python3 build.py [--noindex] [--out PATH]
"""
import json, os, html, urllib.parse, argparse, random, math

ap = argparse.ArgumentParser()
ap.add_argument('--noindex', action='store_true')
ap.add_argument('--out', default='out/index.html')
args = ap.parse_args()

D = json.load(open('data.json', encoding='utf-8'))
U = json.load(open('unannounced.json', encoding='utf-8')) if os.path.exists('unannounced.json') else {}
E, T, TK, KV = D['event'], D['theme'], D['tickets'], D.get('kv', {})
esc = html.escape
GTM = 'GTM-KQF9WVX'
map_q = E.get('venue_map', E['venue'])
map_url = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(map_q + ' ' + E['address'])
BC = U.get('broadcast', {}) if U.get('broadcast', {}).get('show') else None
TS = U.get('title_sponsor', {}) if U.get('title_sponsor', {}).get('show') else None
title = (TS['name'] + ' Presents ' if TS else '') + E['title']

def catch_html():
    s = esc(E['catch'])
    for k, v in E.get('catch_ruby', {}).items():
        s = s.replace(esc(k), f'<ruby>{esc(k)}<rt>{esc(v)}</rt></ruby>')
    return s

# ---------- 花火・金粒子の背景(SVG、毎回同じ形になるよう乱数固定) ----------
def fireworks_svg():
    r = random.Random(1231)
    W, H = 1600, 900
    g = []
    bursts = [(250, 210, 170, T['gold2']), (1330, 170, 200, T['gold1']), (1180, 640, 120, T['red']),
              (420, 700, 110, T['gold1']), (800, 90, 90, T['red']), (1500, 480, 80, T['gold2']), (90, 470, 70, T['red'])]
    for cx, cy, rad, col in bursts:
        n = 40
        for i in range(n):
            a = 2 * math.pi * i / n + r.uniform(-.04, .04)
            r1, r2 = rad * r.uniform(.18, .32), rad * r.uniform(.75, 1.0)
            x1, y1, x2, y2 = cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a)
            g.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="{r.uniform(1,2.2):.1f}" stroke-linecap="round" opacity="{r.uniform(.25,.6):.2f}"/>')
            g.append(f'<circle cx="{cx + rad*1.08*math.cos(a):.0f}" cy="{cy + rad*1.08*math.sin(a):.0f}" r="{r.uniform(1.2,2.6):.1f}" fill="{col}" opacity="{r.uniform(.4,.85):.2f}"/>')
    for _ in range(260):
        col = r.choice([T['gold1'], T['gold2'], T['gold2'], '#fff3c4'])
        g.append(f'<circle cx="{r.uniform(0,W):.0f}" cy="{r.uniform(0,H):.0f}" r="{r.uniform(.6,2.0):.1f}" fill="{col}" opacity="{r.uniform(.15,.7):.2f}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">{"".join(g)}</svg>'
    return 'data:image/svg+xml,' + urllib.parse.quote(svg)

def dust_svg():
    r = random.Random(77)
    g = ''.join(f'<circle cx="{r.uniform(0,400):.0f}" cy="{r.uniform(0,400):.0f}" r="{r.uniform(.5,1.4):.1f}" fill="{T["gold2"]}" opacity="{r.uniform(.1,.45):.2f}"/>' for _ in range(40))
    return 'data:image/svg+xml,' + urllib.parse.quote(f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">{g}</svg>')

# ---------- partials ----------
def nav_links():
    items = [('info', '大会情報')]
    if D['matches'].get('show'): items.insert(0, ('match', '対戦カード'))
    if BC: items.append(('broadcast', '放送情報'))
    if D.get('news'): items.append(('news', 'ニュース'))
    items.append(('ticket', 'チケット'))
    if D.get('videos'): items.append(('movie', '動画'))
    items.append(('access', 'アクセス'))
    return ''.join(f'<a href="#{i}">{t}</a>' for i, t in items)

def sec_head(ja, en):
    return f'<div class="sec__head"><h2 class="sec__ja">{ja}</h2><p class="sec__en">{en}</p></div>'

def hero():
    alt = f"{esc(title)} {esc(E['date_ja'])} {esc(E['venue'])}"
    bar = f'''
    <div class="hero__bar"><div class="wrap">
      <div class="hero__date">{esc(E['date_label'])}<small>{esc(E['dow'])}</small></div>
      <div class="hero__venue">{esc(E['venue'])}</div>
      <div class="hero__time">開場<b>{esc(E['open'])}</b> ／ 開始<b>{esc(E['start'])}</b></div>
    </div></div>'''
    if KV.get('pc'):
        srcset = f' srcset="{KV["pc_1280"]} 1280w, {KV["pc"]} 1920w" sizes="100vw"' if KV.get('pc_1280') else ''
        return f'''
  <section class="hero">
    <img class="hero__img hero__img--pc" src="{KV['pc']}"{srcset} alt="{alt}" width="1920" height="1080" fetchpriority="high">
    <img class="hero__img hero__img--sp" src="{KV.get('sp') or KV['pc']}" alt="{alt}" width="1080" height="1200" fetchpriority="high">{bar}
  </section>'''
    return f'''
  <section class="hero">
    <div class="mv" role="img" aria-label="{alt}">
      <div class="mv__in">
        <p class="mv__kicker">PRO WRESTLING NOAH</p>
        <p class="mv__noah gold">NOAH</p>
        <h1 class="mv__title gold"><span>&ldquo;THE NEW YEAR&rdquo;</span><span>EVE 2026</span></h1>
        <p class="mv__date">{esc(E['date_label'])} <small>{esc(E['dow'])}</small><span class="mv__sep"></span>{esc(E['venue'].split('・')[-1])}</p>
      </div>
    </div>{bar}
  </section>'''

def broadcast_section():
    if not BC: return ''
    return f'''
  <section id="broadcast" class="sec">
    <div class="wrap">
      {sec_head('放送情報', 'LIVE STREAMING')}
      <div class="bc">
        <div><p class="bc__title"><b>{esc(BC['name'])}</b> で{esc(BC['note'])}</p><p class="bc__note">{esc(E['date_ja'])}　試合開始 {esc(E['start'])}</p></div>
        <a class="btn btn--pri" href="{esc(BC['url'])}" target="_blank" rel="noopener">{esc(BC['btn'])} ↗</a>
      </div>
    </div>
  </section>'''

def news_section():
    N = D.get('news') or []
    if not N: return ''
    items = ''.join(f'''
      <li class="news__item"><a href="{esc(n['url'])}" target="_blank" rel="noopener"><time>{esc(n['date'])}</time><span class="news__title">{esc(n['title'])}</span><span class="news__arrow">→</span></a></li>''' for n in N)
    return f'''
  <section id="news" class="sec sec--alt">
    <div class="wrap">{sec_head('ニュース', 'NEWS')}<ul class="news">{items}</ul></div>
  </section>'''

def seat_rows():
    out = ''
    for s in TK['seats']:
        hot = '<span class="tag">残りわずか</span>' if '残りわずか' in s['note'] else ''
        note = s['note'].replace('残りわずか／', '').replace('残りわずか', '')
        out += f'''
          <tr><th>{esc(s['name'])}{hot}{('<small>※'+esc(note)+'</small>') if note else ''}</th><td>{esc(s['adv'])}</td><td>{esc(s['door'])}</td></tr>'''
    return out

def sales_rows():
    out = ''
    for s in TK['sales']:
        lab = f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])} ↗</a>' if s.get('url') else esc(s['label'])
        out += f'''
          <li><span class="sale__label">{lab}</span><span class="sale__date">{esc(s['date'])}</span>{('<span class="sale__note">'+esc(s['note'])+'</span>') if s.get('note') else ''}</li>'''
    return out

def playguides():
    return ''.join(f'''
        <a class="pg" href="{esc(p['url'])}" target="_blank" rel="noopener"><span class="pg__name">{esc(p['name'])}</span><span class="pg__note">{esc(p['note'])}</span><span class="pg__go">チケットを購入する ↗</span></a>''' for p in TK['playguides'])

def li(xs): return ''.join(f'<li>{esc(x)}</li>' for x in xs)

def video_section():
    V = D.get('videos') or []
    if not V: return ''
    cards = ''
    for v in V:
        vid = esc(v['id'])
        cards += f'''
      <div class="video"><button class="video__frame" type="button" data-id="{vid}" aria-label="動画を再生"><img src="img/video_{vid}.jpg" alt="{esc(v.get('title','') or '動画')}" loading="lazy" width="1280" height="720"><span class="video__play"></span></button>{'<p class="video__title">'+esc(v['title'])+'</p>' if v.get('title') else ''}</div>'''
    return f'''
  <section id="movie" class="sec sec--alt">
    <div class="wrap">{sec_head('動画', 'MOVIE')}<div class="videos">{cards}</div></div>
  </section>
  <script>document.querySelectorAll('.video__frame[data-id]').forEach(function(b){{b.addEventListener('click',function(){{var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0';f.title='YouTube video';f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';f.allowFullscreen=true;b.replaceWith(f);f.className='video__iframe';}});}});</script>'''

def footer_links():
    return ''.join(f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])}</a></li>' for l in D['footer_links'])

def sns_links():
    return ''.join(f'<a href="{esc(x["url"])}" target="_blank" rel="noopener">{esc(x["label"])} ↗</a>' for x in D.get('sns', []) if x.get('url'))

noindex = '<meta name="robots" content="noindex,nofollow">\n  ' if args.noindex else ''
desc = f"{E['catch']} ─ {E['date_ja']} {E['venue']}。プロレスリング・ノア「{E['title']}」特設サイト。"
official_btn = f'<a class="btn btn--ghost" href="{esc(E["official_url"])}" target="_blank" rel="noopener">公式大会ページ ↗</a>' if E.get('official_url') else ''
credits_ts = f'<dt>特別協賛</dt><dd class="main">{esc(TS["name"])}</dd>' if TS else ''

# ---------- CSS ----------
G = f"linear-gradient(180deg,{T['gold2']} 0%,#fff1c2 38%,{T['gold1']} 62%,#a97c22 100%)"
CSS = f'''
:root{{--bg:{T['bg']};--bg2:{T['bg2']};--g1:{T['gold1']};--g2:{T['gold2']};--red:{T['red']};--gold:{G};--tx:#F7F3E8;--tx2:#C4C8CF;--line:rgba(212,167,58,.32);--max:1100px;
--ff-en:'Helvetica Neue',Helvetica,Arial,sans-serif;--ff-ja:'Hiragino Kaku Gothic ProN','Hiragino Sans',Meiryo,'Noto Sans JP',sans-serif;}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{background:var(--bg) url("{dust_svg()}");color:var(--tx);font-family:var(--ff-ja);font-weight:600;line-height:1.7;letter-spacing:.02em;overflow-x:hidden}}
img{{max-width:100%;height:auto;display:block}}
a{{color:inherit;text-decoration:none}}
ul{{list-style:none}}
.gold{{background:var(--gold);-webkit-background-clip:text;background-clip:text;color:transparent}}
.wrap{{width:min(100% - 40px,var(--max));margin:0 auto}}
.sec{{padding:88px 0}}
.sec--alt{{background:linear-gradient(180deg,rgba(17,35,58,.85),rgba(13,27,42,.6))}}
.sec__head{{text-align:center;margin-bottom:44px}}
.sec__ja{{font-weight:700;font-size:clamp(24px,3.4vw,34px);letter-spacing:.14em;line-height:1.2;background:var(--gold);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sec__en{{font-family:var(--ff-en);font-weight:700;font-size:12px;color:var(--tx2);margin-top:8px;letter-spacing:.3em}}
.sec__head::after{{content:"";display:block;width:72px;height:3px;background:linear-gradient(90deg,var(--g1) 0 70%,var(--red) 70%);margin:18px auto 0}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:12px 28px;border-radius:6px;font-weight:700;font-size:15px;letter-spacing:.06em;transition:.2s;white-space:nowrap}}
.btn--pri{{background:linear-gradient(180deg,var(--g2),var(--g1));color:#1a1206;box-shadow:0 4px 18px rgba(212,167,58,.25)}}
.btn--pri:hover{{filter:brightness(1.1)}}
.btn--ghost{{border:2px solid var(--g1);color:var(--tx)}}
.btn--ghost:hover{{background:rgba(212,167,58,.12)}}

/* header */
.topwrap{{position:sticky;top:0;z-index:100;background:rgba(9,19,31,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.header{{display:flex;align-items:center;justify-content:space-between;gap:16px;height:64px}}
.header__logo{{display:flex;align-items:center;gap:10px;font-family:var(--ff-en);font-weight:700;letter-spacing:.08em;font-size:14px;white-space:nowrap}}
.header__logo img{{height:36px;width:auto}}
.header__nav{{display:flex;gap:26px;font-weight:700;font-size:14px;letter-spacing:.08em}}
.header__nav a{{position:relative;padding:4px 0}}
.header__nav a::after{{content:"";position:absolute;left:0;bottom:-2px;width:0;height:2px;background:var(--g1);transition:.25s}}
.header__nav a:hover::after{{width:100%}}
.header__cta{{min-height:40px;padding:8px 20px;font-size:13px}}
.spnav{{display:none}}

/* hero */
.hero{{position:relative;background:#050b13}}
.hero__img{{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}}
.hero__img--pc{{max-width:1920px;margin:0 auto}}
.hero__img--sp{{display:none}}
.mv{{position:relative;min-height:min(78vh,760px);display:flex;align-items:center;justify-content:center;text-align:center;overflow:hidden;
background:url("{fireworks_svg()}") center/cover no-repeat,radial-gradient(ellipse at 50% 120%,rgba(184,64,42,.35),transparent 55%),radial-gradient(ellipse at 50% 40%,#16304d 0%,{T['bg']} 55%,#050b13 100%)}}
.mv::after{{content:"";position:absolute;inset:auto 0 0 0;height:120px;background:linear-gradient(180deg,transparent,rgba(5,11,19,.7))}}
.mv__in{{position:relative;z-index:1;padding:60px 20px}}
.mv__kicker{{font-family:var(--ff-en);font-weight:700;letter-spacing:.5em;font-size:13px;color:var(--tx2)}}
.mv__noah{{font-family:var(--ff-en);font-weight:800;font-size:clamp(40px,7vw,84px);letter-spacing:.2em;line-height:1;margin-top:18px;padding-left:.2em}}
.mv__title{{font-family:var(--ff-en);font-weight:800;line-height:1.02;margin-top:10px;filter:drop-shadow(0 0 24px rgba(240,199,94,.28))}}
.mv__title span{{display:block}}
.mv__title span:first-child{{font-size:clamp(34px,7.4vw,96px);letter-spacing:.02em}}
.mv__title span:last-child{{font-size:clamp(28px,5.2vw,68px);letter-spacing:.18em;margin-top:6px}}
.mv__date{{display:inline-flex;align-items:center;gap:14px;margin-top:30px;font-family:var(--ff-en);font-weight:700;font-size:clamp(16px,2vw,22px);letter-spacing:.1em;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:10px 22px}}
.mv__date small{{color:var(--g2);font-size:.7em}}
.mv__sep{{width:6px;height:6px;border-radius:50%;background:var(--red)}}
.hero__bar{{background:linear-gradient(90deg,rgba(212,167,58,.16),rgba(13,27,42,0) 50%,rgba(184,64,42,.16));border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}
.hero__bar .wrap{{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:12px 36px;padding:16px 0}}
.hero__date{{font-family:var(--ff-en);font-weight:700;font-size:28px;letter-spacing:.06em;line-height:1}}
.hero__date small{{font-size:14px;margin-left:8px;color:var(--g2)}}
.hero__venue{{font-size:18px;font-weight:700}}
.hero__time{{font-size:14px;color:var(--tx2)}}
.hero__time b{{color:var(--tx);margin-left:4px}}

/* catch */
.catchsec{{padding:76px 0 12px;background:radial-gradient(ellipse at 50% 0%,rgba(212,167,58,.16),transparent 62%)}}
.catch{{text-align:center}}
.catch__ja{{font-weight:800;font-size:clamp(30px,6vw,64px);letter-spacing:.14em;line-height:1.5;background:var(--gold);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 22px rgba(240,199,94,.25))}}
.catch__ja ruby{{ruby-position:over}}
.catch__ja rt{{font-size:.34em;letter-spacing:.2em;color:var(--g2);-webkit-text-fill-color:var(--g2)}}
.catch__line{{display:block;width:120px;height:2px;margin:22px auto 0;background:linear-gradient(90deg,transparent,var(--g1),var(--red),var(--g1),transparent)}}

/* info */
.infogrid{{display:grid;grid-template-columns:1.1fr .9fr;gap:28px}}
.card{{background:rgba(17,35,58,.9);border:1px solid var(--line);border-radius:10px;padding:30px}}
.card__title{{font-weight:700;letter-spacing:.2em;font-size:13px;color:var(--g2);margin-bottom:16px}}
.card__title small{{font-family:var(--ff-en);color:var(--tx2);font-size:10px;margin-left:10px}}
.datecard__d{{font-family:var(--ff-en);font-weight:700;font-size:54px;letter-spacing:.04em;line-height:1}}
.datecard__d small{{font-size:16px;color:var(--g2);margin-left:10px}}
.datecard__v{{font-size:22px;margin:12px 0 4px}}
.datecard__a{{color:var(--tx2);font-size:14px}}
.datecard__t{{display:flex;gap:28px;margin:18px 0 22px;padding-top:18px;border-top:1px solid var(--line)}}
.datecard__t div span{{display:block;font-size:12px;letter-spacing:.2em;color:var(--tx2)}}
.datecard__t div b{{font-family:var(--ff-en);font-size:26px}}
.datecard__btns{{display:flex;gap:12px;flex-wrap:wrap}}
.cre dl{{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;font-size:14px}}
.cre dt{{color:var(--g2);white-space:nowrap;font-weight:700;letter-spacing:.1em;font-size:13px;padding-top:2px}}
.cre dd{{color:var(--tx2);line-height:1.8}}
.cre dd.main{{color:var(--tx);font-size:16px}}
.cre dd a{{color:var(--tx);border-bottom:1px solid var(--g1)}}

/* broadcast */
.bc{{display:flex;align-items:center;justify-content:space-between;gap:24px;background:rgba(17,35,58,.9);border:1px solid var(--line);border-radius:10px;padding:30px 34px}}
.bc__title{{font-size:24px}}
.bc__title b{{font-family:var(--ff-en)}}
.bc__note{{color:var(--tx2);font-size:14px;margin-top:6px}}

/* news */
.news{{border-top:1px solid var(--line)}}
.news__item a{{display:flex;align-items:center;gap:22px;padding:22px 6px;border-bottom:1px solid var(--line)}}
.news__item time{{font-family:var(--ff-en);color:var(--g2);font-weight:700;white-space:nowrap}}
.news__title{{flex:1;font-size:15px}}
.news__arrow{{color:var(--g1)}}

/* tickets */
.tk__status{{text-align:center;margin-bottom:34px}}
.tk__status span{{display:inline-block;background:linear-gradient(180deg,var(--g2),var(--g1));color:#1a1206;font-weight:700;padding:6px 24px;border-radius:999px;letter-spacing:.12em;font-size:14px}}
.tk__h{{font-size:18px;letter-spacing:.1em;margin:0 0 14px;padding-left:14px;border-left:4px solid var(--g1)}}
.tk__block{{margin-bottom:44px}}
.price{{width:100%;border-collapse:collapse;background:rgba(17,35,58,.9);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:15px}}
.price th,.price td{{padding:14px 18px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}}
.price thead th{{background:rgba(212,167,58,.14);color:var(--g2);font-size:13px;letter-spacing:.15em}}
.price td{{font-family:var(--ff-en);font-weight:700;white-space:nowrap;text-align:right;width:22%}}
.price thead th:not(:first-child){{text-align:right}}
.price tbody th small{{display:block;font-size:12px;color:var(--tx2);font-weight:600;margin-top:2px}}
.price tbody tr:last-child th,.price tbody tr:last-child td{{border-bottom:0}}
.tag{{display:inline-block;margin-left:10px;background:var(--red);color:#fff;font-size:11px;padding:2px 9px;border-radius:3px;vertical-align:2px;letter-spacing:.06em}}
.sales{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}
.sales li{{background:rgba(17,35,58,.9);border:1px solid var(--line);border-radius:10px;padding:18px 22px;display:flex;flex-direction:column;gap:4px}}
.sales li:last-child{{border-color:var(--g1);background:linear-gradient(135deg,rgba(212,167,58,.16),rgba(17,35,58,.9))}}
.sale__label{{color:var(--g2);font-size:14px;letter-spacing:.06em}}
.sale__label a{{border-bottom:1px solid var(--g1)}}
.sale__date{{font-size:17px}}
.sale__note{{font-size:12px;color:var(--tx2)}}
.pgs{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.pg{{display:flex;flex-direction:column;background:rgba(17,35,58,.9);border:1px solid var(--line);border-radius:10px;padding:24px;transition:.2s}}
.pg:hover{{border-color:var(--g2);transform:translateY(-2px)}}
.pg__name{{font-size:18px;font-weight:700}}
.pg__note{{font-size:13px;color:var(--tx2);margin:6px 0 18px;flex:1}}
.pg__go{{display:flex;align-items:center;justify-content:center;min-height:46px;border-radius:6px;background:linear-gradient(180deg,var(--g2),var(--g1));color:#1a1206;font-weight:700;font-size:14px;letter-spacing:.06em}}
.notes{{background:rgba(17,35,58,.9);border:1px solid var(--line);border-radius:10px;padding:24px 28px}}
.notes + .notes{{margin-top:16px}}
.notes h4{{font-size:14px;letter-spacing:.12em;color:var(--g2);margin-bottom:10px}}
.notes li{{position:relative;padding-left:16px;font-size:13px;color:var(--tx2);line-height:1.8;margin-bottom:4px}}
.notes li::before{{content:"※";position:absolute;left:0;color:var(--g1)}}

/* access */
.acc{{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:start}}
.acc__venue{{font-size:30px;line-height:1.3}}
.acc__addr{{color:var(--tx2);margin:14px 0 10px;font-size:15px}}
.acc__route li{{font-size:15px;line-height:1.9;padding-left:18px;position:relative}}
.acc__route li::before{{content:"";position:absolute;left:0;top:.75em;width:7px;height:7px;border-radius:50%;background:var(--red)}}
.acc__map{{margin-top:22px}}
.acc__frame{{aspect-ratio:4/3;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--bg2)}}
.acc__frame iframe{{width:100%;height:100%;border:0}}

/* video */
.videos{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:24px}}
.video{{background:var(--bg2);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
.video__frame{{position:relative;display:block;width:100%;aspect-ratio:16/9;padding:0;border:0;cursor:pointer;overflow:hidden;background:#000}}
.video__frame img{{width:100%;height:100%;object-fit:cover;transition:.3s}}
.video__play{{position:absolute;left:50%;top:50%;width:76px;height:76px;margin:-38px 0 0 -38px;border-radius:50%;background:rgba(212,167,58,.92)}}
.video__play::after{{content:'';position:absolute;left:30px;top:22px;border-style:solid;border-width:16px 0 16px 26px;border-color:transparent transparent transparent #1a1206}}
.video__iframe{{width:100%;aspect-ratio:16/9;border:0;display:block}}
.video__title{{padding:14px 18px;font-size:14px}}

/* footer */
.footer{{border-top:1px solid var(--line);padding:56px 0 40px;text-align:center;background:#081320}}
.footer__lockup{{display:flex;flex-direction:column;align-items:center;gap:14px;margin-bottom:28px}}
.footer__lockup img{{height:60px;width:auto}}
.footer__name{{font-family:var(--ff-en);font-weight:800;letter-spacing:.08em;font-size:18px}}
.footer__links{{display:flex;flex-wrap:wrap;justify-content:center;gap:10px 28px;font-size:13px;color:var(--tx2);margin-bottom:24px}}
.footer__links a{{white-space:nowrap}}
.footer__links a:hover{{color:var(--g2)}}
.footer__sns{{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-bottom:28px}}
.footer__sns a{{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:999px;padding:8px 20px;font-weight:700;font-size:13px;letter-spacing:.06em}}
.footer__sns a:hover{{border-color:var(--g2);color:var(--g2)}}
.footer__copy{{font-family:var(--ff-en);font-size:11px;color:var(--tx2);letter-spacing:.1em}}

/* ---- SP ---- */
@media (max-width:900px){{
  .wrap{{width:min(100% - 32px,var(--max))}}
  .sec{{padding:60px 0}}
  .sec__head{{margin-bottom:30px}}
  .header{{height:56px}}
  .header__logo img{{height:30px}}
  .header__logo span{{font-size:12px}}
  .header__nav{{display:none}}
  .header__cta{{min-height:36px;padding:6px 14px;font-size:12px}}
  .spnav{{display:flex;gap:22px;overflow-x:auto;white-space:nowrap;padding:0 16px 10px;font-weight:700;font-size:13px;letter-spacing:.06em;scrollbar-width:none}}
  .spnav::-webkit-scrollbar{{display:none}}
  .spnav a{{color:var(--tx2)}}
  .hero__img--pc{{display:none}}
  .hero__img--sp{{display:block;aspect-ratio:9/10}}
  .mv{{min-height:0;aspect-ratio:9/10}}
  .mv__kicker{{font-size:10px;letter-spacing:.35em}}
  .mv__date{{gap:10px;padding:8px 14px;margin-top:22px}}
  .hero__bar .wrap{{gap:6px 18px;padding:14px 0}}
  .hero__date{{font-size:24px}}
  .hero__venue{{font-size:16px}}
  .hero__time{{width:100%;text-align:center}}
  .catchsec{{padding:52px 0 0}}
  .catch__ja{{letter-spacing:.08em}}
  .infogrid{{grid-template-columns:1fr;gap:16px}}
  .card{{padding:22px 20px}}
  .datecard__d{{font-size:42px}}
  .datecard__v{{font-size:19px}}
  .datecard__btns .btn{{flex:1}}
  .cre dl{{grid-template-columns:1fr;gap:2px}}
  .cre dd{{margin-bottom:10px}}
  .bc{{flex-direction:column;align-items:flex-start;padding:24px 20px}}
  .bc .btn{{width:100%}}
  .news__item a{{flex-wrap:wrap;gap:6px 14px}}
  .news__title{{flex:1 0 100%;font-size:14px}}
  .price{{font-size:14px}}
  .price th,.price td{{padding:12px 12px}}
  .price td{{width:auto;font-size:13px}}
  .tag{{margin-left:6px}}
  .sales{{grid-template-columns:1fr;gap:10px}}
  .pgs{{grid-template-columns:1fr;gap:12px}}
  .pg{{padding:18px 20px}}
  .pg__note{{margin-bottom:12px}}
  .notes{{padding:20px 18px}}
  .acc{{grid-template-columns:1fr;gap:20px}}
  .acc__venue{{font-size:24px}}
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
  <meta property="og:site_name" content="{esc(E['title'])}｜プロレスリング・ノア">
  <meta property="og:url" content="{esc(E['lp_url'])}">
  <meta property="og:image" content="{esc(E['lp_url'])}img/ogp.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@noah_ghc">
  <meta name="theme-color" content="{T['bg']}">
  <link rel="icon" href="img/noah_badge.png">
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
    <a href="#top" class="header__logo"><img src="img/noah_badge.png" alt="PRO WRESTLING NOAH" width="123" height="118"><span class="gold">THE NEW YEAR EVE 2026</span></a>
    <nav class="header__nav">{nav_links()}</nav>
    <a class="btn btn--pri header__cta" href="#ticket">チケット購入</a>
  </header>
  <nav class="spnav">{nav_links()}</nav>
</div>

<main id="top">{hero()}

  <section class="catchsec">
    <div class="wrap catch"><p class="catch__ja">{catch_html()}</p><span class="catch__line"></span></div>
  </section>

  <section id="info" class="sec">
    <div class="wrap">
      {sec_head('大会情報', 'INFORMATION')}
      <div class="infogrid">
        <div class="card datecard">
          <p class="card__title">日時・会場<small>DATE &amp; VENUE</small></p>
          <p class="datecard__d">{esc(E['date_label'])}<small>{esc(E['dow'])}</small></p>
          <p class="datecard__v">{esc(E['venue'])}</p>
          <p class="datecard__a">{esc(E['address'])}</p>
          <div class="datecard__t"><div><span>開場</span><b>{esc(E['open'])}</b></div><div><span>開始</span><b>{esc(E['start'])}</b></div></div>
          <div class="datecard__btns"><a class="btn btn--pri" href="#ticket">チケット情報</a>{official_btn}</div>
        </div>
        <div class="card cre">
          <p class="card__title">主催・協賛<small>CREDITS</small></p>
          <dl>
            <dt>主催</dt><dd class="main">{esc(E['organizer'])}</dd>
            {credits_ts}<dt>協賛</dt><dd>{esc(E['sponsors'])}</dd>
            <dt>お問合せ</dt><dd><a href="{esc(E['contact_url'])}" target="_blank" rel="noopener">プロレスリング・ノア お問合せフォーム ↗</a><br>{esc(E['contact_note'])}</dd>
          </dl>
        </div>
      </div>
    </div>
  </section>
{broadcast_section()}{news_section()}
  <section id="ticket" class="sec sec--alt">
    <div class="wrap">
      {sec_head('チケット情報', 'TICKET')}
      <p class="tk__status"><span>{esc(TK['status'])}</span></p>

      <div class="tk__block">
        <h3 class="tk__h">チケットを購入する</h3>
        <div class="pgs">{playguides()}
        </div>
      </div>

      <div class="tk__block">
        <h3 class="tk__h">席種・料金</h3>
        <table class="price">
          <thead><tr><th>席種</th><th>前売</th><th>当日</th></tr></thead>
          <tbody>{seat_rows()}
          </tbody>
        </table>
      </div>

      <div class="tk__block">
        <h3 class="tk__h">発売スケジュール</h3>
        <ul class="sales">{sales_rows()}
        </ul>
      </div>

      <div class="notes"><h4>高校生シート・小中学生無料について</h4><ul>{li(TK['youth_notes'])}</ul></div>
      <div class="notes"><h4>ご観戦にあたってのご注意</h4><ul>{li(TK['notes'])}</ul></div>
    </div>
  </section>
{video_section()}
  <section id="access" class="sec">
    <div class="wrap">
      {sec_head('アクセス', 'ACCESS')}
      <div class="acc">
        <div>
          <p class="acc__venue">{esc(E['venue'])}</p>
          <p class="acc__addr">{esc(E['address'])}</p>
          <ul class="acc__route">{li(E['access'])}</ul>
          <p class="acc__map"><a class="btn btn--ghost" href="{map_url}" target="_blank" rel="noopener">Googleマップで見る ↗</a></p>
        </div>
        <div class="acc__frame"><iframe loading="lazy" title="{esc(map_q)} 地図" src="https://www.google.com/maps?q={urllib.parse.quote(map_q)}&output=embed" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      </div>
    </div>
  </section>
</main>

<footer class="footer">
  <div class="wrap">
    <div class="footer__lockup">
      <img src="img/noah_badge.png" alt="PRO WRESTLING NOAH" width="123" height="118" loading="lazy">
      <p class="footer__name gold">{esc(E['title'])}</p>
    </div>
    <ul class="footer__links">{footer_links()}</ul>
    <div class="footer__sns">{sns_links()}</div>
    <p class="footer__copy">&copy; CyberFight Inc. All Rights Reserved.</p>
  </div>
</footer>
</body>
</html>
'''
open(args.out, 'w', encoding='utf-8').write(HTML)
print('wrote', args.out, len(HTML.encode()), 'bytes', '(noindex)' if args.noindex else '')

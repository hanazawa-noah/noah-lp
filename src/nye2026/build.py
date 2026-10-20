#!/usr/bin/env python3
"""NOAH "THE NEW YEAR" EVE 2026 LP builder: data.json (+ unannounced.json) -> out/index.html
usage: python3 build.py [--noindex] [--out PATH]
画像は prep_img.py が uploads/ から out/img/ に作る
"""
import json, os, html, urllib.parse, argparse, random, math

ap = argparse.ArgumentParser()
ap.add_argument('--noindex', action='store_true')
ap.add_argument('--out', default='out/index.html')
args = ap.parse_args()

D = json.load(open('data.json', encoding='utf-8'))
U = json.load(open('unannounced.json', encoding='utf-8')) if os.path.exists('unannounced.json') else {}
E, T, TK, KV, LG = D['event'], D['theme'], D['tickets'], D['kv'], D['logo']
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

# ---------- MVに合わせた質感(ざらつき・にじみ・花火)。SVGを data URI で埋め込む ----------
def svg_uri(svg): return 'data:image/svg+xml,' + urllib.parse.quote(svg)

GRAIN = svg_uri('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>')

def burst(r, cx, cy, rad, col, n=56):
    """MVの花火のような、点線の火花が垂れる形"""
    g = []
    for i in range(n):
        a = 2 * math.pi * i / n + r.uniform(-.05, .05)
        L = rad * r.uniform(.55, 1.0)
        x1, y1 = cx + 6 * math.cos(a), cy + 6 * math.sin(a)
        x2, y2 = cx + L * math.cos(a), cy + L * math.sin(a) + L * .12
        mx, my = cx + L * .6 * math.cos(a), cy + L * .6 * math.sin(a)
        g.append(f'<path d="M{x1:.0f} {y1:.0f}Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}" stroke="{col}" stroke-width="{r.uniform(1,1.8):.1f}" stroke-dasharray="{r.randint(2,5)} {r.randint(3,7)}" fill="none" opacity="{r.uniform(.35,.8):.2f}"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{rad*.08:.0f}" fill="{col}" opacity=".5"/>')
    return ''.join(g)

def fireworks(seed, W, H, spec):
    r = random.Random(seed)
    body = ''.join(burst(r, *s) for s in spec)
    return svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">{body}</svg>')

FW_CATCH = fireworks(1231, 1600, 600, [(140, 120, 210, T['gold']), (1450, 150, 230, T['red']), (1300, 520, 120, T['gold_d'])])
FW_FOOT = fireworks(101, 1600, 500, [(160, 520, 300, T['gold_d']), (1480, 80, 220, T['red'])])

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
    return f'<div class="sec__head"><h2 class="sec__ja">{ja}</h2><span class="sec__rule"></span><p class="sec__en">{en}</p></div>'

def broadcast_section():
    if not BC: return ''
    return f'''
  <section id="broadcast" class="sec">
    <div class="wrap">
      {sec_head('放送情報', 'LIVE STREAMING')}
      <div class="bc box">
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
  <section id="news" class="sec">
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
        <a class="pg box" href="{esc(p['url'])}" target="_blank" rel="noopener"><span class="pg__name">{esc(p['name'])}</span><span class="pg__note">{esc(p['note'])}</span><span class="pg__go">チケットを購入する ↗</span></a>''' for p in TK['playguides'])

def li(xs): return ''.join(f'<li>{esc(x)}</li>' for x in xs)

def video_section():
    V = D.get('videos') or []
    if not V: return ''
    cards, yt = '', False
    for v in V:
        if v.get('type') == 'mp4':
            cards += f'''
      <div class="video box"><video class="video__mp4" src="{esc(v['src'])}" poster="{esc(v['poster'])}" controls playsinline preload="none" width="1280" height="720"></video>{'<p class="video__title">'+esc(v['title'])+'</p>' if v.get('title') else ''}</div>'''
        else:
            yt = True
            vid = esc(v['id'])
            cards += f'''
      <div class="video box"><button class="video__frame" type="button" data-id="{vid}" aria-label="動画を再生"><img src="img/video_{vid}.jpg" alt="{esc(v.get('title','') or '動画')}" loading="lazy" width="1280" height="720"><span class="video__play"></span></button>{'<p class="video__title">'+esc(v['title'])+'</p>' if v.get('title') else ''}</div>'''
    js = '''
  <script>document.querySelectorAll('.video__frame[data-id]').forEach(function(b){b.addEventListener('click',function(){var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0';f.title='YouTube video';f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';f.allowFullscreen=true;b.replaceWith(f);f.className='video__iframe';});});</script>''' if yt else ''
    return f'''
  <section id="movie" class="sec sec--alt">
    <div class="wrap">{sec_head('動画', 'MOVIE')}<div class="videos{' videos--one' if len(V) == 1 else ''}">{cards}</div></div>
  </section>{js}'''

def footer_links():
    return ''.join(f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])}</a></li>' for l in D['footer_links'])

def sns_links():
    return ''.join(f'<a href="{esc(x["url"])}" target="_blank" rel="noopener">{esc(x["label"])} ↗</a>' for x in D.get('sns', []) if x.get('url'))

mincho_chars = ''.join(sorted(set(E.get('lead', '') + E['catch'] + ''.join(E.get('catch_ruby', {}).values()))))
MINCHO = 'https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@900&display=swap&text=' + urllib.parse.quote(mincho_chars)
noindex = '<meta name="robots" content="noindex,nofollow">\n  ' if args.noindex else ''
desc = f"{E['catch']} ─ {E.get('lead','')}{E['date_ja']} {E['venue']}。プロレスリング・ノア「{E['title']}」特設サイト。"
official_btn = f'<a class="btn btn--ghost" href="{esc(E["official_url"])}" target="_blank" rel="noopener">公式大会ページ ↗</a>' if E.get('official_url') else ''
credits_ts = f'<dt>特別協賛</dt><dd class="main">{esc(TS["name"])}</dd>' if TS else ''
VP = E.get('venue_photo')
venue_photo = f'<img class="acc__photo" src="{VP["sm"]}" srcset="{VP["sm"]} 960w, {VP["src"]} 1520w" sizes="(max-width:900px) 100vw, 540px" alt="{esc(map_q)} 外観" loading="lazy" width="1520" height="1080">' if VP else ''
alt = f"{esc(title)} {esc(E['date_ja'])} {esc(E['venue'])}"

# ---------- CSS ----------
CSS = f'''
:root{{--bg:{T['bg']};--bg2:{T['bg2']};--gold:{T['gold']};--gold-d:{T['gold_d']};--red:{T['red']};--tx:#F3EEE2;--tx2:#AEB9BE;--line:rgba(246,194,68,.30);--max:1100px;
--ff-en:'Montserrat','Helvetica Neue',Helvetica,Arial,sans-serif;--ff-min:'Noto Serif JP','Hiragino Mincho ProN','Yu Mincho','YuMincho',serif;--ff-ja:'Hiragino Kaku Gothic ProN','Hiragino Sans',Meiryo,'Noto Sans JP',sans-serif;}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{position:relative;background:var(--bg);color:var(--tx);font-family:var(--ff-ja);font-weight:600;line-height:1.7;letter-spacing:.02em;overflow-x:hidden}}
/* MVと同じ「ざらついた紙」の質感を全体にかける */
body::before{{content:"";position:fixed;inset:0;z-index:200;pointer-events:none;background:url("{GRAIN}");opacity:.07;mix-blend-mode:screen}}
img,video{{max-width:100%;height:auto;display:block}}
a{{color:inherit;text-decoration:none}}
ul{{list-style:none}}
.en{{font-family:var(--ff-en)}}
.wrap{{width:min(100% - 40px,var(--max));margin:0 auto}}
.sec{{position:relative;padding:96px 0}}
.sec--alt{{background:radial-gradient(ellipse 60% 50% at 15% 20%,rgba(0,0,0,.28),transparent 70%),radial-gradient(ellipse 50% 60% at 85% 80%,rgba(0,0,0,.25),transparent 70%),#0d2029}}
.sec__head{{text-align:center;margin-bottom:48px}}
.sec__ja{{font-weight:800;font-size:clamp(26px,3.6vw,38px);letter-spacing:.16em;line-height:1.2;color:var(--gold)}}
.sec__rule{{display:block;width:96px;height:2px;background:var(--gold);margin:18px auto 12px}}
.sec__en{{font-family:var(--ff-en);font-weight:800;font-size:13px;color:var(--gold);letter-spacing:.32em}}
.box{{background:rgba(16,37,47,.82);border:1px solid var(--line);border-radius:4px}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:12px 28px;border-radius:3px;font-weight:800;font-size:15px;letter-spacing:.08em;transition:.2s;white-space:nowrap}}
.btn--pri{{background:var(--gold);color:#0b1b24}}
.btn--pri:hover{{background:#ffd365}}
.btn--ghost{{border:2px solid var(--gold);color:var(--gold)}}
.btn--ghost:hover{{background:rgba(246,194,68,.12)}}

/* header */
.topwrap{{position:sticky;top:0;z-index:100;background:rgba(9,22,29,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.header{{display:flex;align-items:center;justify-content:space-between;gap:16px;height:68px}}
.header__logo img{{height:44px;width:auto}}
.header__nav{{display:flex;gap:28px;font-weight:700;font-size:14px;letter-spacing:.1em}}
.header__nav a{{position:relative;padding:4px 0}}
.header__nav a::after{{content:"";position:absolute;left:0;bottom:-2px;width:0;height:2px;background:var(--gold);transition:.25s}}
.header__nav a:hover{{color:var(--gold)}}
.header__nav a:hover::after{{width:100%}}
.header__cta{{min-height:40px;padding:8px 22px;font-size:13px}}
.spnav{{display:none}}

/* hero */
.hero{{background:#06131a}}
.hero__img{{width:100%;max-width:1920px;margin:0 auto;aspect-ratio:16/9;object-fit:cover}}
.hero__bar{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:#0a1a22}}
.hero__bar .wrap{{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px 40px;padding:18px 0}}
.hero__date{{font-family:var(--ff-en);font-weight:800;font-size:30px;letter-spacing:.02em;line-height:1;color:var(--gold)}}
.hero__date small,.datecard__d small{{font-size:.5em;margin-left:8px;padding-bottom:3px;border-bottom:2px solid var(--gold);vertical-align:.5em}}
.hero__venue{{font-size:18px;font-weight:800}}
.hero__time{{font-size:14px;color:var(--tx2)}}
.hero__time b{{color:var(--tx);margin-left:4px;font-family:var(--ff-en)}}

/* catch */
.catchsec{{position:relative;padding:96px 0 84px;text-align:center;overflow:hidden;background:url("{FW_CATCH}") center/cover no-repeat}}
.catch__lead{{display:inline-block;font-family:var(--ff-min);font-weight:900;font-size:clamp(14px,1.6vw,17px);letter-spacing:.3em;color:var(--tx);padding:6px 0 6px .3em;border-top:1px solid var(--gold);border-bottom:1px solid var(--gold)}}
.catch__ja{{font-family:var(--ff-min);font-weight:900;font-size:clamp(32px,6.2vw,68px);letter-spacing:.16em;line-height:1.5;margin-top:26px;color:var(--gold);text-shadow:0 0 28px rgba(246,194,68,.25)}}
.catch__ja ruby{{ruby-position:over}}
.catch__ja rt{{font-size:.32em;letter-spacing:.3em;color:var(--gold)}}

/* info */
.infogrid{{display:grid;grid-template-columns:1.1fr .9fr;gap:28px}}
.card{{padding:32px}}
.card__title{{font-weight:800;letter-spacing:.2em;font-size:14px;color:var(--gold);margin-bottom:18px;padding-bottom:12px;border-bottom:1px solid var(--line)}}
.card__title small{{font-family:var(--ff-en);font-size:10px;margin-left:10px;letter-spacing:.25em}}
.datecard__d{{font-family:var(--ff-en);font-weight:800;font-size:54px;line-height:1;color:var(--gold)}}
.datecard__v{{font-size:22px;font-weight:800;margin:16px 0 4px}}
.datecard__a{{color:var(--tx2);font-size:14px}}
.datecard__t{{display:flex;gap:32px;margin:18px 0 24px;padding-top:18px;border-top:1px solid var(--line)}}
.datecard__t div span{{display:block;font-size:12px;letter-spacing:.2em;color:var(--tx2)}}
.datecard__t div b{{font-family:var(--ff-en);font-weight:800;font-size:28px}}
.datecard__btns{{display:flex;gap:12px;flex-wrap:wrap}}
.cre dl{{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;font-size:14px}}
.cre dt{{color:var(--gold);white-space:nowrap;font-weight:800;letter-spacing:.1em;font-size:13px;padding-top:2px}}
.cre dd{{color:var(--tx2);line-height:1.8}}
.cre dd.main{{color:var(--tx);font-size:16px}}
.cre dd a{{color:var(--tx);border-bottom:1px solid var(--gold)}}

/* broadcast */
.bc{{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:30px 34px}}
.bc__title{{font-size:24px}}
.bc__note{{color:var(--tx2);font-size:14px;margin-top:6px}}

/* news */
.news{{border-top:1px solid var(--line)}}
.news__item a{{display:flex;align-items:center;gap:22px;padding:22px 6px;border-bottom:1px solid var(--line)}}
.news__item time{{font-family:var(--ff-en);color:var(--gold);font-weight:800;white-space:nowrap}}
.news__title{{flex:1;font-size:15px}}

/* tickets */
.tk__status{{text-align:center;margin-bottom:40px}}
.tk__status span{{display:inline-block;background:var(--red);color:#fff;font-weight:800;padding:7px 28px;letter-spacing:.2em;font-size:14px}}
.tk__h{{font-size:19px;font-weight:800;letter-spacing:.12em;margin:0 0 16px;display:flex;align-items:center;gap:14px}}
.tk__h::after{{content:"";flex:1;height:1px;background:var(--line)}}
.tk__h::before{{content:"";width:10px;height:10px;background:var(--gold);transform:rotate(45deg)}}
.tk__block{{margin-bottom:52px}}
.pgs{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.pg{{display:flex;flex-direction:column;padding:24px;transition:.2s}}
.pg:hover{{border-color:var(--gold);transform:translateY(-2px)}}
.pg__name{{font-size:19px;font-weight:800}}
.pg__note{{font-size:13px;color:var(--tx2);margin:6px 0 18px;flex:1}}
.pg__go{{display:flex;align-items:center;justify-content:center;min-height:48px;border-radius:3px;background:var(--gold);color:#0b1b24;font-weight:800;font-size:14px;letter-spacing:.08em}}
.price{{width:100%;border-collapse:collapse;font-size:15px}}
.price th,.price td{{padding:15px 20px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}}
.price thead th{{color:var(--gold);font-size:13px;letter-spacing:.2em;border-bottom:2px solid var(--gold)}}
.price td{{font-family:var(--ff-en);font-weight:700;white-space:nowrap;text-align:right;width:22%}}
.price thead th:not(:first-child){{text-align:right}}
.price tbody th{{font-weight:800}}
.price tbody th small{{display:block;font-size:12px;color:var(--tx2);font-weight:600;margin-top:2px}}
.price tbody tr:last-child th,.price tbody tr:last-child td{{border-bottom:0}}
.tag{{display:inline-block;margin-left:10px;background:var(--red);color:#fff;font-size:11px;padding:2px 9px;vertical-align:2px;letter-spacing:.06em}}
.sales{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}
.sales li{{padding:18px 22px;display:flex;flex-direction:column;gap:4px;border-left:3px solid var(--line);background:rgba(16,37,47,.6)}}
.sales li:last-child{{border-left-color:var(--gold);background:rgba(246,194,68,.10)}}
.sale__label{{color:var(--gold);font-size:14px;font-weight:800;letter-spacing:.06em}}
.sale__label a{{border-bottom:1px solid var(--gold)}}
.sale__date{{font-size:17px;font-weight:800}}
.sale__note{{font-size:12px;color:var(--tx2)}}
.notes{{padding:24px 28px}}
.notes + .notes{{margin-top:16px}}
.notes h4{{font-size:14px;font-weight:800;letter-spacing:.12em;color:var(--gold);margin-bottom:10px}}
.notes li{{position:relative;padding-left:16px;font-size:13px;color:var(--tx2);line-height:1.8;margin-bottom:4px}}
.notes li::before{{content:"※";position:absolute;left:0;color:var(--gold)}}

/* video */
.videos{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:24px}}
.videos--one{{max-width:900px;margin:0 auto;grid-template-columns:1fr}}
.video{{overflow:hidden;padding:0}}
.video__mp4{{width:100%;aspect-ratio:16/9;background:#000}}
.video__frame{{position:relative;display:block;width:100%;aspect-ratio:16/9;padding:0;border:0;cursor:pointer;overflow:hidden;background:#000}}
.video__frame img{{width:100%;height:100%;object-fit:cover}}
.video__play{{position:absolute;left:50%;top:50%;width:76px;height:76px;margin:-38px 0 0 -38px;border-radius:50%;background:var(--gold)}}
.video__play::after{{content:'';position:absolute;left:30px;top:22px;border-style:solid;border-width:16px 0 16px 26px;border-color:transparent transparent transparent #0b1b24}}
.video__iframe{{width:100%;aspect-ratio:16/9;border:0;display:block}}
.video__title{{padding:14px 18px;font-size:14px}}

/* access */
.acc{{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start}}
.acc__photo{{width:100%;aspect-ratio:1520/1080;object-fit:cover;border:1px solid var(--line);border-radius:4px;margin-bottom:24px}}
.acc__venue{{font-size:30px;font-weight:800;line-height:1.3}}
.acc__addr{{color:var(--tx2);margin:12px 0 10px;font-size:15px}}
.acc__route li{{font-size:15px;line-height:1.9;padding-left:18px;position:relative}}
.acc__route li::before{{content:"";position:absolute;left:0;top:.72em;width:7px;height:7px;background:var(--gold);transform:rotate(45deg)}}
.acc__map{{margin-top:22px}}
.acc__frame{{aspect-ratio:3/4;border:1px solid var(--line);border-radius:4px;overflow:hidden;background:var(--bg2)}}
.acc__frame iframe{{width:100%;height:100%;border:0}}

/* footer */
.footer{{position:relative;border-top:1px solid var(--line);padding:72px 0 44px;text-align:center;background:url("{FW_FOOT}") center/cover no-repeat,#071319}}
.footer__logo{{width:min(520px,86%);margin:0 auto 22px}}
.footer__badge{{height:56px;width:auto;margin:0 auto 30px}}
.footer__links{{display:flex;flex-wrap:wrap;justify-content:center;gap:10px 28px;font-size:13px;color:var(--tx2);margin-bottom:24px}}
.footer__links a{{white-space:nowrap}}
.footer__links a:hover{{color:var(--gold)}}
.footer__sns{{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-bottom:30px}}
.footer__sns a{{display:inline-flex;align-items:center;border:1px solid var(--gold);color:var(--gold);border-radius:3px;padding:9px 22px;font-weight:800;font-size:13px;letter-spacing:.06em}}
.footer__sns a:hover{{background:var(--gold);color:#0b1b24}}
.footer__copy{{font-family:var(--ff-en);font-size:11px;color:var(--tx2);letter-spacing:.1em}}

/* ---- SP ---- */
@media (max-width:900px){{
  .wrap{{width:min(100% - 32px,var(--max))}}
  .sec{{padding:64px 0}}
  .sec__head{{margin-bottom:32px}}
  .header{{height:56px}}
  .header__logo img{{height:34px}}
  .header__nav{{display:none}}
  .header__cta{{min-height:36px;padding:6px 14px;font-size:12px}}
  .spnav{{display:flex;gap:22px;overflow-x:auto;white-space:nowrap;padding:0 16px 10px;font-weight:700;font-size:13px;letter-spacing:.06em;scrollbar-width:none}}
  .spnav::-webkit-scrollbar{{display:none}}
  .spnav a{{color:var(--tx2)}}
  .hero__bar .wrap{{gap:8px 18px;padding:16px 0}}
  .hero__date{{font-size:26px}}
  .hero__venue{{font-size:16px}}
  .hero__time{{width:100%;text-align:center}}
  .catchsec{{padding:60px 0 56px;background-size:auto 100%}}
  .catch__lead{{letter-spacing:.18em}}
  .catch__ja{{letter-spacing:.08em;margin-top:18px}}
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
  .tk__block{{margin-bottom:40px}}
  .pgs{{grid-template-columns:1fr;gap:12px}}
  .pg{{padding:18px 20px}}
  .pg__note{{margin-bottom:12px}}
  .price{{font-size:14px}}
  .price th,.price td{{padding:12px 8px}}
  .price td{{width:auto;font-size:13px}}
  .tag{{margin-left:6px}}
  .sales{{grid-template-columns:1fr;gap:10px}}
  .notes{{padding:20px 18px}}
  .acc{{grid-template-columns:1fr;gap:20px}}
  .acc__frame{{aspect-ratio:4/3}}
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
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
  <link href="{MINCHO}" rel="stylesheet">
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
    <a href="#top" class="header__logo"><img src="{LG['pc']}" alt="{esc(E['title'])}" width="{LG['w']}" height="{LG['h']}"></a>
    <nav class="header__nav">{nav_links()}</nav>
    <a class="btn btn--pri header__cta" href="#ticket">チケット購入</a>
  </header>
  <nav class="spnav">{nav_links()}</nav>
</div>

<main id="top">
  <section class="hero">
    <h1><img class="hero__img" src="{KV['pc']}" srcset="{KV['sp']} 960w, {KV['pc_1280']} 1280w, {KV['pc']} 1920w" sizes="100vw" alt="{alt}" width="1920" height="1080" fetchpriority="high"></h1>
    <div class="hero__bar"><div class="wrap">
      <div class="hero__date">{esc(E['date_label'])}<small>{esc(E['dow'])}</small></div>
      <div class="hero__venue">{esc(E['venue'])}</div>
      <div class="hero__time">開場<b>{esc(E['open'])}</b> ／ 開始<b>{esc(E['start'])}</b></div>
    </div></div>
  </section>

  <section class="catchsec">
    <div class="wrap">{('<p class="catch__lead">'+esc(E['lead'])+'</p>') if E.get('lead') else ''}<p class="catch__ja">{catch_html()}</p></div>
  </section>

  <section id="info" class="sec sec--alt">
    <div class="wrap">
      {sec_head('大会情報', 'INFORMATION')}
      <div class="infogrid">
        <div class="card box datecard">
          <p class="card__title">日時・会場<small>DATE &amp; VENUE</small></p>
          <p class="datecard__d">{esc(E['date_label'])}<small>{esc(E['dow'])}</small></p>
          <p class="datecard__v">{esc(E['venue'])}</p>
          <p class="datecard__a">{esc(E['address'])}</p>
          <div class="datecard__t"><div><span>開場</span><b>{esc(E['open'])}</b></div><div><span>開始</span><b>{esc(E['start'])}</b></div></div>
          <div class="datecard__btns"><a class="btn btn--pri" href="#ticket">チケット情報</a>{official_btn}</div>
        </div>
        <div class="card box cre">
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
  <section id="ticket" class="sec">
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

      <div class="notes box"><h4>高校生シート・小中学生無料について</h4><ul>{li(TK['youth_notes'])}</ul></div>
      <div class="notes box"><h4>ご観戦にあたってのご注意</h4><ul>{li(TK['notes'])}</ul></div>
    </div>
  </section>
{video_section()}
  <section id="access" class="sec">
    <div class="wrap">
      {sec_head('アクセス', 'ACCESS')}
      <div class="acc">
        <div>
          {venue_photo}
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
    <img class="footer__logo" src="{LG['lg']}" alt="{esc(E['title'])}" width="{LG['lg_w']}" height="{LG['lg_h']}" loading="lazy">
    <img class="footer__badge" src="img/noah_badge.png" alt="PRO WRESTLING NOAH" width="123" height="118" loading="lazy">
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

#!/usr/bin/env python3
"""マルハン presents NOAH Jr. GRAND PRIX 2 LP builder: data.json -> out/index.html
usage: python3 build.py [--noindex] [--out PATH]
画像は prep_img.py が uploads/ から out/img/ に作る
"""
import json, html, urllib.parse, argparse

ap = argparse.ArgumentParser()
ap.add_argument('--noindex', action='store_true')
ap.add_argument('--out', default='out/index.html')
args = ap.parse_args()

D = json.load(open('data.json', encoding='utf-8'))
E, T, KV, LG, BR, TK, MH = D['event'], D['theme'], D['kv'], D['logo'], D['bracket'], D['tickets'], D['maruhan']
P = {p['id']: p for p in D['players']}
esc = html.escape
GTM = 'GTM-KQF9WVX'
title = E['title']
RAINBOW = f"linear-gradient(90deg,{T['g6']},{T['g5']},{T['g4']},{T['g3']},{T['g2']},{T['g1']})"
# KVと同じ「左下が赤〜右上が青」の斜めグラデーション
KVGRAD = (f"radial-gradient(ellipse 70% 60% at 0% 100%,{T['g6']} 0%,transparent 70%),"
          f"radial-gradient(ellipse 60% 60% at 100% 0%,{T['g1']} 0%,transparent 70%),"
          f"linear-gradient(35deg,{T['g5']} 0%,{T['g4']} 30%,{T['g3']} 55%,{T['g2']} 78%,{T['g1']} 100%)")

def svg_uri(svg): return 'data:image/svg+xml,' + urllib.parse.quote(svg)
GRAIN = svg_uri('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>')

def map_url(e): return 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(e['venue_map'])
NAV = [('players', '出場選手'), ('bracket', 'トーナメント表'), ('round1', '1回戦カード'), ('schedule', '日程'), ('maruhan', 'マルハン企画'), ('goods', 'コラボグッズ'), ('ticket', 'チケット')]
def nav_links(): return ''.join(f'<a href="#{i}">{t}</a>' for i, t in NAV)

def sec_head(ja, en):
    return f'<div class="sec__head"><p class="sec__en">{en}</p><h2 class="sec__ja">{ja}</h2><span class="sec__rule"></span></div>'

def players():
    out = ''
    for p in D['players']:
        nick = f'<span class="pl__nick">{esc(p["nick"])}</span>' if p.get('nick') else ''
        team = f'<span class="pl__team">{esc(p["team"])}</span>' if p.get('team') else ''
        out += f'''
        <li class="pl"><img src="img/p_{p['id']}.webp" alt="{esc(p['name'])}" width="210" height="265" loading="lazy"><div class="pl__box">{nick}<span class="pl__name">{esc(p['name']).replace('・', '・<wbr>').replace('ブラック', 'ブラック<wbr>')}</span>{team}</div></li>'''
    return out

def round1():
    out = ''
    for e in D['events']:
        cards = [m for m in e['matches'] if m.get('img')]
        if not cards: continue
        items = ''.join(f'''
          <figure class="vs"><img src="img/{m['img']}_960.jpg" srcset="img/{m['img']}_960.jpg 960w, img/{m['img']}.jpg 1920w" sizes="(max-width:900px) 100vw, 540px" alt="{esc(P[m['a']]['name'])} vs {esc(P[m['b']]['name'])}" width="1920" height="1080" loading="lazy"><figcaption><b>{m['no']}</b>{esc(P[m['a']]['name'])}<i>vs</i>{esc(P[m['b']]['name'])}</figcaption></figure>''' for m in cards)
        out += f'''
        <div class="r1">
          <p class="r1__day"><span class="en">{esc(e['date'])}</span><small>{esc(e['dow'])}</small>{esc(e['venue'])}</p>
          <div class="r1__grid">{items}
          </div>
        </div>'''
    return out

def match_line(m):
    if m.get('a'):
        return f'<li><b>{m["no"]}</b><span>{esc(P[m["a"]]["name"])} <i>vs</i> {esc(P[m["b"]]["name"])}</span></li>'
    return f'<li><b>{esc(m["no"])}</b><span>{esc(m["a_text"])}<i>vs</i>{esc(m["b_text"])}</span></li>'

def schedule():
    out = ''
    for e in D['events']:
        fin = ' sc--final' if e.get('final') else ''
        out += f'''
        <article class="sc box{fin}">
          <p class="sc__round">{esc(e['round'])}</p>
          <p class="sc__date en">{esc(e['date'])}<small>{esc(e['dow'])}</small></p>
          <p class="sc__venue">{esc(e['venue'])}</p>
          <p class="sc__time">開場 <b class="en">{esc(e['open'])}</b>　開始 <b class="en">{esc(e['start'])}</b></p>{'<a class="sc__mh" href="#maruhan">マルハンコラボブース・撮影会</a>' if e.get('maruhan') else ''}
          <details class="sc__cards"><summary>対戦カード</summary><ul>{''.join(match_line(m) for m in e['matches'])}</ul></details>
          <p class="sc__tour">〜{esc(e['tour'])}〜</p>
          <a class="sc__map" href="{map_url(e)}" target="_blank" rel="noopener">会場の地図 ↗</a>
        </article>'''
    return out

def banner(n, alt):
    return f'<img class="mh__banner" src="img/{n}_960.jpg" srcset="img/{n}_960.jpg 960w, img/{n}.jpg 1920w" sizes="(max-width:900px) 100vw, 860px" alt="{esc(alt)}" width="1920" height="1080" loading="lazy">'

def notes_ul(xs): return '<ul class="mh__notes">' + ''.join(f'<li>{esc(x)}</li>' for x in xs) + '</ul>'

def maruhan():
    evs = ''.join(f'''
        <article class="mhe box"><p class="mhe__no en">{esc(v['no'])}</p><h3 class="mhe__t">{esc(v['title'])}</h3><p class="mhe__x">{esc(v['text'])}</p>
          <dl class="mhe__spec">{''.join(f'<dt>{esc(k)}</dt><dd>{esc(d)}</dd>' for k, d in v['spec'])}</dl>{notes_ul(v['notes'])}</article>''' for v in MH['events'])
    ven = ''.join(f'<li><b class="en">{esc(e["date"])}</b><small class="en">{esc(e["dow"])}</small><span>{esc(e["venue"])}</span><em>開場 {esc(e["open"])}／開始 {esc(e["start"])}</em></li>' for e in D['events'] if e.get('maruhan'))
    return f'''
  <section id="maruhan" class="sec">
    <div class="wrap">
      {sec_head('マルハン×NOAH 特別企画', 'MARUHAN × NOAH')}
      <div class="mh__intro">{banner(MH['banner'], 'マルハン×NOAH NOAH Jr. GRAND PRIX 2 冠協賛記念')}{''.join(f'<p>{esc(x)}</p>' for x in MH['lead'])}</div>
      <div class="mhes">{evs}
      </div>
      <div class="mhv box"><h3 class="mhv__t">{esc(MH['venues_title'])}</h3><ul>{ven}</ul></div>
      <p class="mh__credit">{esc(MH['credit'])}</p>
    </div>
  </section>'''

def goods():
    G, C = MH['goods'], MH['campaign']
    ser = ''
    for sr in G['series']:
        items = ''.join(f'''
          <li class="gd"><img src="img/{i['img']}.webp" alt="{esc(sr['name'])} {esc(i['name'])}" width="484" height="272" loading="lazy"><p class="gd__n">{esc(i['name'])}</p><p class="gd__p en">{esc(i['price'])}</p>{('<p class="gd__note">' + esc(i['note']) + '</p>') if i.get('note') else ''}</li>''' for i in sr['items'])
        ser += f'''
      <div class="gs"><h3 class="gs__t">{esc(sr['name'])}<small>シリーズ</small></h3><p class="gs__d">{esc(sr['desc'])}</p><ul class="gds">{items}
      </ul></div>'''
    steps = ''.join(f'<li><b class="en">{k + 1}</b>{esc(x)}</li>' for k, x in enumerate(C['steps']))
    return f'''
  <section id="goods" class="sec">
    <div class="wrap">
      {sec_head('マルハン×NOAH コラボグッズ', 'COLLABORATION GOODS')}
      <div class="mh__intro">{banner(G['banner'], 'マルハン×NOAH コラボアイテム発売決定')}<p>{esc(G['lead'])}</p><p class="mh__sale">{esc(G['sale'])}</p></div>{ser}
      <div class="box mh__nbox">{notes_ul(G['notes'])}</div>
      <div class="cp box">
        <p class="cp__lab en">CAMPAIGN</p>
        <h3 class="cp__t">{esc(C['title'])}</h3>
        <p class="cp__prize">{esc(C['prize'])}</p>
        <dl class="mhe__spec"><dt>応募期間</dt><dd>{esc(C['period'])}</dd></dl>
        <ol class="cp__steps">{steps}</ol>
        <p class="cp__sn">{esc(C['steps_note'])}</p>
        <p class="cp__btn"><a class="btn btn--pri" href="{esc(C['x_url'])}" target="_blank" rel="noopener">NOAH公式X（@noah_ghc）を見る ↗</a></p>
        <details class="cp__more"><summary>当選発表・注意事項</summary>{notes_ul(C['result'] + C['notes'])}</details>
      </div>
      <p class="mh__credit">{esc(MH['credit'])}</p>
    </div>
  </section>'''

def playguides():
    return ''.join(f'<a class="pg" href="{esc(p["url"])}" target="_blank" rel="noopener"><span>{esc(p["name"])}</span><b>チケットを購入する ↗</b></a>' for p in TK['playguides'])

def li(xs): return ''.join(f'<li>{esc(x)}</li>' for x in xs)
def footer_links(): return ''.join(f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])}</a></li>' for l in D['footer_links'])

first, last = D['events'][0], D['events'][-1]
noindex = '<meta name="robots" content="noindex,nofollow">\n  ' if args.noindex else ''
desc = f"{E['catch']} ─ {E['lead']}。{first['date_ja']}後楽園ホールで開幕、{last['date_ja']}後楽園ホールで決勝。出場選手・トーナメント表・全日程。プロレスリング・ノア特設サイト。"
alt = f"{esc(title)} {esc(E['period_label'])}"

# ---------- CSS ----------
CSS = f'''
:root{{--bg:{T['bg']};--bg2:{T['bg2']};--tx:#fff;--tx2:#B9C0D6;--line:rgba(255,255,255,.18);--max:1160px;--rb:{RAINBOW};
--ff-en:'Montserrat','Helvetica Neue',Helvetica,Arial,sans-serif;--ff-ja:'Hiragino Kaku Gothic ProN','Hiragino Sans',Meiryo,'Noto Sans JP',sans-serif;}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{position:relative;z-index:0;background:var(--bg);color:var(--tx);font-family:var(--ff-ja);font-weight:600;line-height:1.7;letter-spacing:.02em;overflow-x:hidden}}
/* 背景はKVと同じ斜めグラデーションを画面に固定し、ざらつきを重ねる */
body::after{{content:"";position:fixed;inset:0;z-index:-1;background:{KVGRAD}}}
body::before{{content:"";position:fixed;inset:0;z-index:200;pointer-events:none;background:url("{GRAIN}");opacity:.16;mix-blend-mode:overlay}}
img{{max-width:100%;height:auto;display:block}}
a{{color:inherit;text-decoration:none}}
ul{{list-style:none}}
.en{{font-family:var(--ff-en)}}
.wrap{{width:min(100% - 40px,var(--max));margin:0 auto}}
.sec{{position:relative;padding:96px 0;text-shadow:0 1px 12px rgba(0,0,0,.28)}}
.sec__head{{text-align:center;margin-bottom:48px}}
.sec__en{{font-family:var(--ff-en);font-weight:800;font-size:clamp(30px,4.4vw,52px);line-height:1.05;letter-spacing:.02em}}
.sec__ja{{font-weight:700;font-size:15px;letter-spacing:.24em;margin-top:10px}}
.sec__rule{{display:block;width:120px;height:4px;background:#fff;margin:18px auto 0}}
.box{{background:rgba(12,18,38,.72);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);border:1px solid var(--line);border-radius:4px}}
.btn{{text-shadow:none;display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:12px 28px;border-radius:3px;font-weight:800;font-size:15px;letter-spacing:.08em;transition:.2s;white-space:nowrap}}
.btn--pri{{background:#fff;color:var(--bg)}}
.btn--pri:hover{{opacity:.85}}
.btn--ghost{{border:2px solid #fff}}
.btn--ghost:hover{{background:rgba(255,255,255,.12)}}

/* header */
.topwrap{{position:sticky;top:0;z-index:100;background:rgba(12,18,38,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}}
.topwrap::after{{content:"";display:block;height:3px;background:var(--rb)}}
.header{{display:flex;align-items:center;justify-content:space-between;gap:16px;height:68px}}
.header__logo{{display:flex;align-items:center;gap:12px}}
.header__logo img{{height:30px;width:auto}}
.header__logo small{{font-size:11px;letter-spacing:.06em;color:var(--tx2);white-space:nowrap}}
.header__nav{{display:flex;gap:26px;font-weight:700;font-size:14px;letter-spacing:.08em}}
.header__nav a{{position:relative;padding:4px 0}}
.header__nav a::after{{content:"";position:absolute;left:0;bottom:-2px;width:0;height:2px;background:var(--rb);transition:.25s}}
.header__nav a:hover::after{{width:100%}}
.header__cta{{min-height:40px;padding:8px 22px;font-size:13px}}
.spnav{{display:none}}

/* hero */
.hero{{background:#0a0f20}}
.hero__img{{width:100%;max-width:1920px;margin:0 auto}}
.hero__bar{{position:relative;background:{KVGRAD}}}
.hero__bar::after{{content:"";position:absolute;inset:0;background:url("{GRAIN}");opacity:.18;mix-blend-mode:overlay;pointer-events:none}}
.hero__bar .wrap{{position:relative;z-index:1;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px 48px;padding:22px 0;text-shadow:0 2px 12px rgba(0,0,0,.2)}}
.hb{{display:flex;align-items:baseline;gap:14px}}
.hb__lab{{font-family:var(--ff-en);font-style:italic;font-weight:800;font-size:12px;letter-spacing:.06em;border-top:2px solid #fff;padding-top:2px}}
.hb__d{{font-family:var(--ff-en);font-weight:800;font-size:40px;line-height:1}}
.hb__d small,.sc__date small{{white-space:nowrap;font-weight:700;font-size:.5em;margin-left:8px;border-bottom:2px solid #fff;vertical-align:.4em}}
.hb__v{{font-weight:800;font-size:15px}}
.hb__arrow{{font-family:var(--ff-en);font-size:28px;opacity:.8}}

/* catch */
.catch{{text-align:center;padding:84px 0 76px;text-shadow:0 2px 16px rgba(0,0,0,.3)}}
.catch__sp{{font-size:14px;letter-spacing:.2em}}
.catch__title{{font-family:var(--ff-en);font-weight:800;font-size:clamp(28px,4.6vw,56px);line-height:1.15;margin-top:10px}}
.catch__en{{display:inline-block;font-family:var(--ff-en);font-weight:800;font-size:clamp(13px,1.5vw,17px);letter-spacing:.24em;margin-top:26px;padding:8px 0 8px .24em;border-top:3px solid #fff;border-bottom:3px solid #fff}}
.catch__lead{{font-size:clamp(16px,1.9vw,20px);font-weight:700;margin-top:22px;letter-spacing:.1em}}

/* players */
.pls{{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:14px 12px}}
.pl img{{width:100%;aspect-ratio:210/265;object-fit:cover}}
.pl__box{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:1px;padding:10px 4px 11px;background:rgba(12,18,38,.62);border:1px solid rgba(255,255,255,.75);border-top:0;min-height:96px;justify-content:center}}
.pl__nick{{font-size:10px;letter-spacing:.04em;opacity:.85;line-height:1.35}}
.pl__name{{word-break:keep-all;overflow-wrap:anywhere;font-size:15px;font-weight:800;line-height:1.35;letter-spacing:.04em}}
.pl__team{{overflow-wrap:anywhere;font-size:9.5px;opacity:.75;line-height:1.35;margin-top:2px}}

/* bracket */
.br{{display:block;border:1px solid var(--line)}}
.br__note{{text-align:center;font-size:13px;margin-top:14px}}
.br__note a{{border-bottom:1px solid #fff;color:#fff}}

/* round1 */
.r1 + .r1{{margin-top:44px}}
.r1__day{{display:flex;align-items:baseline;gap:14px;font-weight:800;font-size:17px;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid var(--line)}}
.r1__day .en{{font-size:30px;line-height:1}}
.r1__day small{{font-family:var(--ff-en);font-size:13px;margin-left:-8px}}
.r1__grid{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.vs img{{width:100%;aspect-ratio:16/9;object-fit:cover}}
.vs figcaption{{display:flex;align-items:center;gap:10px;padding:12px 2px;font-size:15px;font-weight:800}}
.vs figcaption b{{font-size:18px}}
.vs figcaption i,.sc__cards i{{font-family:var(--ff-en);font-style:normal;font-size:.8em;opacity:.7;margin:0 4px}}

/* schedule */
.scs{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.sc{{position:relative;display:flex;flex-direction:column;padding:22px 20px 18px;overflow:hidden}}
.sc::before{{content:"";position:absolute;left:0;top:0;right:0;height:4px;background:var(--rb)}}
.sc--final{{background:rgba(255,255,255,.94);color:var(--bg);border-color:#fff;text-shadow:none}}
.sc--final::before{{background:var(--rb)}}
.sc--final .sc__cards{{border-color:rgba(12,18,38,.2)}}
.sc__round{{align-self:flex-start;font-size:12px;font-weight:800;letter-spacing:.14em;border:1px solid #fff;padding:1px 10px}}
.sc--final .sc__round{{background:var(--bg);color:#fff;border-color:var(--bg)}}
.sc__date{{font-weight:800;font-size:40px;line-height:1;margin-top:14px}}
.sc__venue{{font-size:15px;font-weight:800;margin-top:10px;line-height:1.5}}
.sc__time{{font-size:12px;color:var(--tx2);margin-top:6px}}
.sc--final .sc__time,.sc--final .sc__tour{{color:#46506e}}
.sc--final .sc__time b{{color:var(--bg)}}
.sc--final .sc__date small{{border-color:var(--bg)}}
.sc__time b{{color:#fff;font-size:14px}}
.sc__cards{{margin-top:14px;border-top:1px solid var(--line);font-size:13px}}
.sc__cards summary{{cursor:pointer;list-style:none;padding:10px 0 4px;font-weight:800;letter-spacing:.1em;display:flex;justify-content:space-between}}
.sc__cards summary::-webkit-details-marker{{display:none}}
.sc__cards summary::after{{content:"＋"}}
.sc__cards[open] summary::after{{content:"－"}}
.sc__cards li{{display:flex;gap:8px;padding:6px 0;line-height:1.55}}
.sc__cards li b{{flex:none}}
.sc__tour{{font-size:11px;color:var(--tx2);margin-top:auto;padding-top:12px}}
.sc__map{{font-size:12px;margin-top:6px;align-self:flex-start;border-bottom:1px solid currentColor}}

/* maruhan */
.mh__intro{{max-width:860px;margin:0 auto 40px;text-align:center}}
.mh__banner{{width:100%;aspect-ratio:16/9;object-fit:cover;border:1px solid rgba(255,255,255,.6);margin-bottom:24px}}
.mh__intro p{{font-size:15px;line-height:1.9;margin-top:8px;text-align:left}}
.mh__intro p:first-of-type{{font-size:18px;font-weight:800;text-align:center}}
.mh__intro p.mh__sale{{display:inline-block;text-align:center;margin-top:16px;background:#fff;color:var(--bg);text-shadow:none;font-size:15px;font-weight:800;padding:6px 18px}}
.mhes{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
.mhe{{position:relative;padding:28px 24px 22px}}
.mhe::before{{content:"";position:absolute;left:0;top:0;right:0;height:4px;background:{T['mh']}}}
.mhe__no{{font-weight:800;font-size:34px;line-height:1}}
.mhe__t{{font-size:19px;font-weight:800;line-height:1.45;margin:10px 0 12px}}
.mhe__x{{font-size:14px;line-height:1.85}}
.mhe__spec{{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:13px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line)}}
.mhe__spec dt{{font-weight:800;white-space:nowrap;padding:1px 8px;border:1px solid rgba(255,255,255,.6);font-size:11px;align-self:start;text-align:center}}
.mhe__spec dd{{line-height:1.6}}
.mh__notes{{margin-top:12px}}
.mh__notes li{{position:relative;padding-left:16px;font-size:12px;color:var(--tx2);line-height:1.75}}
.mh__notes li::before{{content:"※";position:absolute;left:0}}
.mhv{{margin-top:22px;padding:24px 28px}}
.mhv__t{{font-size:16px;font-weight:800;letter-spacing:.06em;margin-bottom:10px}}
.mhv li{{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;padding:10px 0;border-top:1px solid var(--line)}}
.mhv li b{{font-size:22px;line-height:1}}
.mhv li small{{font-size:11px;margin-left:-6px}}
.mhv li span{{font-weight:800}}
.mhv li em{{font-style:normal;font-size:13px;color:var(--tx2)}}
.mh__credit{{text-align:center;font-size:13px;margin-top:28px}}
.gs{{margin-top:44px}}
.gs__t{{font-size:24px;font-weight:800;display:flex;align-items:center;gap:14px}}
.gs__t small{{font-size:13px;margin-left:-8px}}
.gs__t::after{{content:"";flex:1;height:2px;background:#fff;opacity:.7}}
.gs__d{{font-size:14px;margin:8px 0 18px}}
.gds{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
.gd{{background:rgba(12,18,38,.72);border:1px solid var(--line);border-radius:4px;overflow:hidden;padding-bottom:14px}}
.gd img{{width:100%;aspect-ratio:484/272;object-fit:cover;background:#fff}}
.gd__n{{font-size:14px;font-weight:800;line-height:1.5;padding:12px 16px 2px}}
.gd__p{{font-size:17px;font-weight:800;padding:0 16px}}
.gd__note{{font-size:12px;color:var(--tx2);padding:2px 16px 0}}
.mh__nbox{{margin-top:24px;padding:14px 24px 18px}}
.cp{{position:relative;margin-top:44px;padding:36px 40px;text-align:center}}
.cp::before{{content:"";position:absolute;left:0;top:0;right:0;height:4px;background:var(--rb)}}
.cp__lab{{display:inline-block;font-weight:800;font-size:12px;letter-spacing:.2em;border:1px solid #fff;padding:2px 14px}}
.cp__t{{font-size:clamp(20px,2.6vw,28px);font-weight:800;margin-top:14px;line-height:1.45}}
.cp__prize{{font-size:16px;margin-top:10px}}
.cp .mhe__spec{{display:inline-grid;text-align:left;border-top:0;margin-top:12px}}
.cp__steps{{list-style:none;display:flex;justify-content:center;gap:16px;margin-top:20px;text-align:left}}
.cp__steps li{{display:flex;align-items:center;gap:12px;flex:1;max-width:360px;padding:14px 18px;border:1px solid rgba(255,255,255,.6);font-size:14px;line-height:1.55}}
.cp__steps b{{flex:none;display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:#fff;color:var(--bg);text-shadow:none;font-size:15px}}
.cp__sn{{font-size:13px;margin-top:14px}}
.cp__btn{{margin-top:20px}}
.cp__more{{max-width:820px;margin:24px auto 0;text-align:left;border-top:1px solid var(--line)}}
.cp__more summary{{cursor:pointer;list-style:none;padding:14px 0 4px;font-weight:800;font-size:14px;display:flex;justify-content:space-between}}
.cp__more summary::-webkit-details-marker{{display:none}}
.cp__more summary::after{{content:"＋"}}
.cp__more[open] summary::after{{content:"－"}}
.sc__mh{{align-self:flex-start;margin-top:10px;font-size:11px;font-weight:800;letter-spacing:.04em;background:{T['mh']};color:#fff;padding:3px 9px;text-shadow:none}}

/* ticket */
.pgs{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.pg{{display:flex;flex-direction:column;gap:14px;padding:24px;background:rgba(12,18,38,.72);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);border:1px solid var(--line);border-radius:4px;transition:.2s}}
.pg:hover{{border-color:#fff;transform:translateY(-2px)}}
.pg span{{font-size:19px;font-weight:800}}
.pg b{{text-shadow:none;display:flex;align-items:center;justify-content:center;min-height:48px;border-radius:3px;background:#fff;color:var(--bg);font-size:14px;letter-spacing:.08em}}
.tk__more{{text-align:center;margin-top:32px}}
.notes{{padding:22px 26px;margin-top:28px}}
.notes li{{position:relative;padding-left:16px;font-size:13px;color:var(--tx2);line-height:1.8}}
.notes li::before{{content:"※";position:absolute;left:0}}

/* footer */
.footer{{position:relative;padding:72px 0 44px;text-align:center;background:rgba(7,11,24,.9)}}
.footer::before{{content:"";position:absolute;left:0;right:0;top:0;height:4px;background:var(--rb)}}
.footer__sp{{font-size:12px;letter-spacing:.2em;color:var(--tx2);margin-bottom:10px}}
.footer__logo{{width:min(311px,70%);margin:0 auto 26px}}
.footer__badge{{height:56px;width:auto;margin:0 auto 30px}}
.footer__links{{display:flex;flex-wrap:wrap;justify-content:center;gap:10px 28px;font-size:13px;color:var(--tx2);margin-bottom:26px}}
.footer__links a{{white-space:nowrap}}
.footer__links a:hover{{color:#fff}}
.footer__copy{{font-family:var(--ff-en);font-size:11px;color:var(--tx2);letter-spacing:.1em}}

/* ---- SP ---- */
@media (max-width:900px){{
  .wrap{{width:min(100% - 32px,var(--max))}}
  .sec{{padding:64px 0}}
  .sec__head{{margin-bottom:32px}}
  .header{{height:56px}}
  .header__logo img{{height:24px}}
  .header__logo small{{display:none}}
  .header__nav{{display:none}}
  .header__cta{{min-height:36px;padding:6px 14px;font-size:12px}}
  .spnav{{display:flex;gap:22px;overflow-x:auto;white-space:nowrap;padding:0 16px 10px;font-weight:700;font-size:13px;letter-spacing:.06em;scrollbar-width:none}}
  .spnav::-webkit-scrollbar{{display:none}}
  .spnav a{{color:var(--tx2)}}
  .hero__bar .wrap{{flex-direction:column;gap:12px;padding:18px 0}}
  .hb{{flex-wrap:wrap;justify-content:center;gap:4px 12px}}
  .hb__d{{font-size:34px}}
  .hb__v{{width:100%;text-align:center;font-size:13px}}
  .hb__arrow{{transform:rotate(90deg);font-size:20px;line-height:1}}
  .catch{{padding:56px 0 52px}}
  .catch__en{{letter-spacing:.12em;padding-left:.12em}}
  .pls{{grid-template-columns:repeat(4,minmax(0,1fr));gap:10px 6px}}
  .pl__box{{padding:6px 2px 7px;min-height:78px}}
  .pl__nick{{font-size:8px}}
  .pl__name{{font-size:11px;letter-spacing:0}}
  .pl__team{{font-size:7.5px}}
  .r1__grid{{grid-template-columns:1fr;gap:14px}}
  .r1__day{{flex-wrap:wrap;gap:4px 12px;font-size:14px}}
  .r1__day .en{{font-size:26px}}
  .vs figcaption{{font-size:14px;padding:8px 2px}}
  .scs{{grid-template-columns:1fr 1fr;gap:10px}}
  .sc{{padding:18px 12px 14px}}
  .sc__round{{font-size:11px;padding:1px 8px}}
  .sc__date{{font-size:30px;margin-top:10px}}
  .sc__venue{{font-size:13px}}
  .sc__time{{font-size:11px}}
  .sc__time b{{font-size:12px}}
  .sc__cards{{font-size:12px}}
  .sc__cards li{{flex-direction:column;gap:0}}
  .mhes{{grid-template-columns:1fr;gap:14px}}
  .mhe{{padding:22px 18px 18px}}
  .mhe__t{{font-size:17px}}
  .mhv{{padding:18px}}
  .mh__intro p:first-of-type{{font-size:16px;text-align:left}}
  .gs__t{{font-size:20px}}
  .gds{{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}
  .gd__n{{font-size:12px;padding:8px 10px 0}}
  .gd__p{{font-size:14px;padding:0 10px}}
  .gd__note{{font-size:10.5px;padding:2px 10px 0}}
  .mh__nbox{{padding:10px 16px 14px}}
  .cp{{padding:28px 18px}}
  .cp__steps{{flex-direction:column;align-items:stretch}}
  .cp__steps li{{max-width:none}}
  .cp__btn .btn{{width:100%;white-space:normal}}
  .sc__mh{{font-size:10px;padding:2px 6px}}
  .pgs{{grid-template-columns:1fr;gap:12px}}
  .pg{{padding:18px 20px}}
  .notes{{padding:18px}}
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
  <meta property="og:site_name" content="{esc(E['short'])}｜プロレスリング・ノア">
  <meta property="og:url" content="{esc(E['lp_url'])}">
  <meta property="og:image" content="{esc(E['lp_url'])}img/ogp.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@noah_ghc">
  <meta name="theme-color" content="{T['bg']}">
  <link rel="icon" href="img/noah_badge.png">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,700;0,800;1,800&display=swap" rel="stylesheet">
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
    <a href="#top" class="header__logo"><img src="{LG['src']}" alt="{esc(title)}" width="{LG['w']}" height="{LG['h']}"><small>{esc(E['sponsor'])} presents</small></a>
    <nav class="header__nav">{nav_links()}</nav>
    <a class="btn btn--pri header__cta" href="#ticket">チケット購入</a>
  </header>
  <nav class="spnav">{nav_links()}</nav>
</div>

<main id="top">
  <section class="hero">
    <h1><picture>
      <source media="(max-width:900px)" srcset="{KV['sp_750']} 750w, {KV['sp']} 1125w" sizes="100vw" width="1125" height="1500">
      <img class="hero__img" src="{KV['pc']}" srcset="{KV['pc_960']} 960w, {KV['pc_1280']} 1280w, {KV['pc']} 1920w" sizes="100vw" alt="{alt}" width="1920" height="1080" fetchpriority="high">
    </picture></h1>
    <div class="hero__bar"><div class="wrap">
      <div class="hb"><span class="hb__lab">OPENING</span><span class="hb__d">{esc(first['date'])}<small>{esc(first['dow'])}</small></span><span class="hb__v">{esc(first['venue'])}</span></div>
      <span class="hb__arrow">→</span>
      <div class="hb"><span class="hb__lab">FINAL</span><span class="hb__d">{esc(last['date'])}<small>{esc(last['dow'])}</small></span><span class="hb__v">{esc(last['venue'])}</span></div>
    </div></div>
  </section>

  <section class="catch">
    <div class="wrap">
      <p class="catch__sp">{esc(E['sponsor'])} presents</p>
      <p class="catch__title">{esc(E['short']).replace('GRAND PRIX 2', '<span style="white-space:nowrap">GRAND PRIX 2</span>')}</p>
      <p class="catch__en">{esc(E['catch'])}</p>
      <p class="catch__lead">{esc(E['lead'])}</p>
    </div>
  </section>

  <section id="players" class="sec">
    <div class="wrap">
      {sec_head('出場選手', 'ENTRY')}
      <ul class="pls">{players()}
      </ul>
    </div>
  </section>

  <section id="bracket" class="sec">
    <div class="wrap">
      {sec_head('トーナメント表', 'BRACKET')}
      <a class="br" href="{BR['src']}" target="_blank" rel="noopener"><img src="{BR['sm']}" srcset="{BR['sm']} 960w, {BR['src']} 1920w" sizes="(max-width:1160px) 100vw, 1160px" alt="{esc(title)} トーナメント表" width="1920" height="1080" loading="lazy"></a>
      <p class="br__note">画像をタップすると大きく表示されます</p>
    </div>
  </section>

  <section id="round1" class="sec" style="padding-top:0">
    <div class="wrap">
      {sec_head('1回戦 対戦カード', '1ST ROUND')}{round1()}
    </div>
  </section>

  <section id="schedule" class="sec">
    <div class="wrap">
      {sec_head('公式戦日程', 'SCHEDULE')}
      <div class="scs">{schedule()}
      </div>
    </div>
  </section>
{maruhan()}{goods()}

  <section id="ticket" class="sec">
    <div class="wrap">
      {sec_head('チケット', 'TICKET')}
      <div class="pgs">{playguides()}</div>
      <div class="notes box"><ul>{li(TK['notes'])}</ul></div>
      <p class="tk__more"><a class="btn btn--ghost" href="{esc(E['official_url'])}" target="_blank" rel="noopener">NOAH公式サイト 大会日程 ↗</a></p>
    </div>
  </section>
</main>

<footer class="footer">
  <div class="wrap">
    <p class="footer__sp">{esc(E['sponsor'])} presents</p>
    <img class="footer__logo" src="{LG['src']}" alt="{esc(title)}" width="{LG['w']}" height="{LG['h']}" loading="lazy">
    <img class="footer__badge" src="img/noah_badge.png" alt="PRO WRESTLING NOAH" width="123" height="118" loading="lazy">
    <ul class="footer__links">{footer_links()}</ul>
    <p class="footer__copy">&copy; CyberFight Inc. All Rights Reserved.</p>
  </div>
</footer>
</body>
</html>
'''
open(args.out, 'w', encoding='utf-8').write(HTML)
print('wrote', args.out, len(HTML.encode()), 'bytes', '(noindex)' if args.noindex else '')

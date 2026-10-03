---
name: noah-event-lp
description: "NOAHの大会特設LP(ランディングページ)の新規制作・修正・更新運用の依頼時に使う。「LP」「特設ページ」「ランディングページ」や大会名(N-1、WRESTLE ODYSSEY等)で発動。"
---

# NOAH大会特設LP 制作・運用スキル

プロレスリング・ノアの大会特設LPを、確立済みのデザインシステムと運用フローで制作・修正する。実績: N-1 VICTORY 2026 (noah.co.jp/lp/n12026/)、WRESTLE ODYSSEY Ⅱ(2026/10/25 両国)。
**現行テンプレート = WRESTLE ODYSSEY Ⅱ版**(2026-10-03確定)。新規LPはこのテンプレートの data.json / build.py を複製して作る。

## テンプレートの所在(環境リセット後もここから取得)

- GitHubリポジトリ `hanazawa-noah/noah-lp` の `_template/` に `data.json` `build.py` `pack.sh` `deploy.sh` `設置手順.txt` を保管。
  取得: `git clone https://x-access-token:$GH_TOKEN@github.com/hanazawa-noah/noah-lp.git` → `_template/` をコピー。
- トークンはプロジェクトメモリ(/projects/.../areas/github-pages-deploy.md)に保存済み。ユーザーに再度聞かない。
- ユーザーが `wo2_ソース_data_build.zip` を添付した場合はそちらを優先。

## 大原則

- 依頼者はWebのプロではない。手順は最小化し、納品物は「上書きするだけ」の完成ファイルにする。専門用語を避け、アップロード手順・キャッシュ更新(Ctrl+F5)まで毎回添える。
- 人間の作業は「素材提供」と「本番サーバーへのHTML一式アップロード」のみ。限定公開・検証・ZIP化はAIで完結させる。
- 関係者フィードバックは鵜呑みにせず、Webマーケのプロとして実施可否の判断コメントを付けてから反映する(例: ヒーローのカルーセル化は定石として非推奨)。
- noah.co.jp はボット対策でこちらから読めない。公式情報はユーザーに本文を貼ってもらう。curl等での回避はしない。
- 未定情報(当日スケジュール・グッズ等)は「後日発表」「後日追加」と書かず、**セクションごと出さない**。決まり次第追加。
- ヒアリング項目: 日程 / ビジュアル / 対戦カード / スケジュール / グッズ / マップ / 配信(ABEMA or WRESTLE UNIVERSE) / ニュース / 動画。

## 構成・デザインシステム(WO2テンプレート準拠)

- 単一 index.html(CSS/JSインライン)+ img/。data.json → build.py で静的生成(HTML直書き禁止)。
- セクション順: ヒーロー(静止KV、スライダー禁止)→ **キャッチコピー(ヒーロー直下、英文大+和文リード)** → 対戦カード → 大会情報(日程カード+主催/協賛クレジット)→ 放送情報 → ニュース → チケット → 動画(動画がある時のみ)→ アクセス → フッター。
  ※リーグ戦(N-1等)は対戦カードの代わりに出場選手グリッド+星取表。
- **ナビ・見出しは日本語主体**(対戦カード/大会情報/放送情報/ニュース/チケット/動画/アクセス)。英語(MATCH CARD等)は見出し下の小さな添え字。
- ヘッダー: `<div class="topwrap">`(sticky)内に header(ロゴ+PCナビ+チケットCTA)と SP横スクロールナビ。fixed+マージン合わせ禁止。
- フッター: 大会ロゴ+NOAHバッジ → サイトリンク(公式/大会情報/ニュース/選手一覧/YouTube公式) → **SNSボタン(X @noah_ghc, YouTube https://www.youtube.com/channel/UC4T0v46s8yxJuTOW1_mD1xA/)** → コピーライト。
- 動画: YouTubeサムネ(i.ytimg.com/vi/ID/maxresdefault.jpg を img/video_ID.jpg に保存)をクリックで youtube-nocookie 埋め込みに差し替える方式。data.json の `videos` にIDを足すだけで出る。
- 放送情報の時刻: 「試合開始 15:00 ／ 配信開始時間はABEMAの番組ページをご確認ください」の形(配信開始は直前に変わるため断定しない)。
- フォント: 欧文 'Helvetica Neue',Helvetica,Arial / 和文 'Hiragino Kaku Gothic ProN','Hiragino Sans',Meiryo,'Noto Sans JP'。白系・太字基調。アクセント色は罫線・ボタン・装飾のみ。
- テーマ配色はKVから抽出(N-1 2026=#0F0C25×金#C9A24B、WO2=宇宙#070B18×アイスブルー#5BC0F8)。
- SP用CSSは @media(max-width:900px) で末尾に。

## 画像(解像度を落とさない)

- KVはPSDがあればPSDから直接書き出し(JPEG再圧縮を避ける)。**PC用1920w q92 + 1280w q88 を srcset で出し分け**、CSSで max-width:1920px。1600w以下に落とさない。
- SP用ヒーローは別合成: PSDの背景レイヤー+白版ロゴで 1080×1200(Retina 2倍)。
- 対戦カード画像 1920w q88 + 960w q84。ロゴはPSD「ロゴ3D」グループを透過WebP(ネイティブ解像度+640w)。
- OGP 1200×630(KV中央を横幅基準でクロップ。縦 = 幅×630/1200)。
- 選手写真560×700 WebP q76。遅延読み込み必須(ヒーローは fetchpriority=high)。
- 元素材が1920×1080の場合、4Kでは限界があることをユーザーに一言添える。

## 固定ルール(全LP共通)

- 表記: 単独の「ノア」は「NOAH」。大会ロゴは公式ロックアップのみ・改変禁止。
- 計測: GTM-KQF9WVX をhead+body直後noscriptに設置。
- 配信: WRESTLE UNIVERSE = https://www.wrestle-universe.com/ja/noah / ABEMA = https://abema.tv/video/genre/fightingsports。
- プレイガイド: e+ https://eplus.jp/noah/ / チケットぴあ https://t.pia.jp/pia/artist/artists.do?artistsCd=11027339 / ローソン https://l-tike.com/sports/mevent/?mid=111745。ヘッダーCTAはイープラス。席種・価格は公式大会ページへリンク。
- 選手プロフィールURL noah.co.jp/profile/数値ID/。既知ID: 清宮1/杉浦7/拳王10/北宮11/Inamura36/藤田74/ウルフ86/征矢120/飯野155/遠藤206/KENTA228/OZAWA272/煌牙396/タイタス414/ヘイスト632/チェン657。
- OGP: twitter:site @noah_ghc、og:site_name「大会名|プロレスリング・ノア」、公開URLは /lp/◯◯/ を仮置きしユーザーに確認。

## 納品・運用フロー

- 納品3形態(pack.sh で一括生成): ①軽量プレビュー(data URI埋め込み。**ヒーローとロゴはフル解像度**、他は縮小。2MB程度可) ②限定公開用ZIP(noindex、ZIP直下) ③本番設置用ZIP(フォルダごと、設置手順.txt同梱)。ソースZIP(data.json/build.py/pack.sh/deploy.sh)も毎回出す。
- **関係者向け限定公開 = GitHub Pages**(`deploy.sh` で `https://hanazawa-noah.github.io/noah-lp/<大会slug>/` に反映。noindex版)。NOAH社内はClaudeアカウントを持たないため、アーティファクト公開URLでは見られない。Netlify Dropの手作業はしない。Claudeアーティファクトは補助的に同じURLへ再publishしてよい。
- 公開後の修正: 本番サーバー上のindex.htmlが正。ユーザーにダウンロード→添付してもらい最小修正。ただしdata.jsonから再生成できる場合はそちらを優先し全体整合を保つ。
- 検証: 機械チェック(リンク/画像参照/noindex/GTM)+Playwrightスクショ(PC1440・SP390、Retina等倍でヒーロー画質も確認)。ローカルではGoogleマップiframe・YouTubeはネットワーク制限で黒くなる(本番では表示される)。
- 更新運用が増えたらClaude Codeへの移行を提案する(素材フォルダ→コマンド1発で再ビルド&デプロイ)。

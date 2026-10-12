# NOAH 大会特設LP リポジトリ

プロレスリング・ノアの大会特設LPを作る場所。依頼者はWebのプロではないので、専門用語を避け、依頼者にやってもらう作業は最小限にすること。

## 構成
- `src/<大会slug>/`(例: `src/wo2/`): その大会のソース。`data.json`(内容)+ `build.py`(生成)+ `out/img/`(画像)+ `pack.sh`(納品物生成)
- `<大会slug>/`(例: `wo2/`): GitHub Pages で公開される確認用サイト(noindex版)。**手で編集しない**。`deploy.sh` が生成する
- `SKILL.md`: 制作ルール(デザイン・表記・画像・納品フロー)。**作業前に必ず読む**
- `_template/` `_skill/` `index.html`: 旧運用の名残。消してよい

## 更新のやり方(定型)
1. 素材(画像・ニュース本文・動画URL)をチャットで受け取る(または `src/<slug>/uploads/` に置いてもらう)
2. `src/<slug>/data.json` を更新(HTML直書き禁止)。画像は 1920w q88 + 960w q84 の2段階で `out/img/` へ。YouTubeは `i.ytimg.com/vi/<ID>/maxresdefault.jpg` を `out/img/video_<ID>.jpg` に保存
3. `cd src/<slug> && bash pack.sh` → `dist/` に納品3形態(プレビューHTML・限定公開用ZIP・本番設置用ZIP)
4. `bash deploy.sh <slug>` で確認用サイトに反映(commit & push まで行う)。URL: https://hanazawa-noah.github.io/noah-lp/<slug>/
5. 本番は依頼者が `dist/<slug>_本番設置用.zip` を noah.co.jp の `/lp/…/` に手でアップする(wo2 は `/lp/wo2026/`)。ZIPの場所を伝える
6. 完了報告は箇条書きで短く(1項目100文字程度)。push に失敗したら GitHub Desktop で「Push origin」を押すよう案内

## 禁止・注意
- 未定情報(スケジュール・グッズ等)は「後日発表」と書かず、セクションごと出さない
- noah.co.jp はこちらから読めない。ニュース本文は依頼者に貼ってもらう
- 公開リポジトリなので、未発表の対戦カード画像を先行して置かない(置く場合は依頼者に確認)
- 新しい大会は `cp -r src/wo2 src/<slug>` から始め、SKILL.md のルールに従う。`index.html`(確認用トップ)にリンクを足す
- Python が無い/PIL・playwright が無いときは `pip install pillow playwright && playwright install chromium` を自分で実行する

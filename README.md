# MAVS DAILY v2

Dallas Mavericksの非公式個人ファンサイト。

## 追加済み
- 最新ニュース
- 西地区順位
- 直近試合
- 最新ロースター
- 選手別スタッツ欄
- 2026-27 salary cap / cap hit
- サラリー棒グラフ
- 将来ドラフト指名権
- `data/take.json` で編集できる「今日のMavs」
- GitHub Actionsによる毎日自動更新

## 公開
GitHub repositoryへこのフォルダの中身をpushし、Settings → Pages → Deploy from a branch → main / root。

## 今日のMavsを編集
`data/take.json` の `text` と `date` を書き換えてcommitするだけです。

## 注意
Stats / draft assets / salaryは外部サイトの仕様変更で自動取得できない場合があります。
失敗時は既存JSONを保持するfail-safe設計です。


## v3 additions
- Sports-media style top page
- Clickable roster cards
- Individual player profile pages
- Player salary / contract / stat overview

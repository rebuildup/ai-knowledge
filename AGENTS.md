# AI Knowledge — editorial contract

このリポジトリの制作物は読者向けの記事。編集時には次の順で判断する。

1. [執筆方針](docs/執筆方針.md)、[図版方針](docs/図版方針.md)、[根拠と更新](docs/根拠と更新.md)を最優先で読む。
2. **執筆前**に [.agents/skills/writing-discipline/SKILL.md](.agents/skills/writing-discipline/SKILL.md) を読んで、読者の問い・答え・根拠を選ぶ。会話の経緯や作業報告を記事へ持ち込まない。
3. 日本語の本文は [.agents/skills/natural-japanese/SKILL.md](.agents/skills/natural-japanese/SKILL.md) を使って執筆・構造レビューし、[.agents/skills/yomiyasu/SKILL.md](.agents/skills/yomiyasu/SKILL.md) を**推敲と意味保持の確認**に使う。同種の修正を両スキルから競合させない。
4. **最後に**タイトル・第一文・各見出しを単体で読み、何が言いたい記事か分からなければ書き直す。
5. 図版は本文を箱に置き換えたものを採用しない。一次資料の画面・公式図・比較結果・手順の失敗箇所など、実際に情報が増える場合だけ使う。外部画像のライセンスと機密を確認。
6. 元記事の意味・前提・断定の強さを変えず、事実は公式出典・実測・経験・推論に分ける。根拠なしの数字・スクリーンショットを作らない。
7. `articles/<slug>/article.md`の変更時は`python3 scripts/editorial_check.py`を実行する。機械検査が成功しても日本語や内容の品質が保証されたとは言わない。

記事の主張が弱ければ見た目を整えて公開するのではなく、取材・検証を追加するか`draft`のまま残す。

第三者スキルの出典とライセンスは [スキル運用](docs/執筆スキル.md) を参照。

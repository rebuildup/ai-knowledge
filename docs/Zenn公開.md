# Zennでの公開

AIナレッジの正本はこのリポジトリの `main` ブランチの `articles/<slug>/article.md`。Zenn専用の `zenn` ブランチはGitHub Actionsが自動生成する。原稿を二重管理しない。

## 初回の準備

1. このPRをレビュー・mainへマージする。Sync Zenn publishing branch ワークフローが実行され、`zenn` ブランチが作成される。GitHub ActionsのWrite権限またはブランチ保護で失敗した場合は、ワークフローのログを確認する。
2. [ZennのGitHub連携](https://zenn.dev/zenn/articles/connect-to-github)からGitHubの `rebuildup/ai-knowledge` を連携する（ZennでのGitHub App認可操作が必要）。
3. **連携するブランチを `zenn` に設定する。mainを連携しない。**
4. Zennのデプロイ履歴で正常に同期されていること、5本とも下書きになっていることを確認する。連携だけでは公開されない。

Zennアカウントと同じGitHub Organizationに別のリポジトリを連携している場合は、既存の連携・アプリ権限との衝突に注意する。連携はこのリポジトリのコードだけでは完結しない。

## 執筆と公開

- 原稿：`articles/<slug>/article.md`。本文と根拠・記事固有メタデータはここに保持する。
- Zennの識別子・`emoji`・`type`・`topics`：`zenn.json`。新規記事は必ず登録する。Zennのslugは12〜50文字で一度公開すると変更不可。
- `status: draft` → Zennの `published: false`。検証していない5本は初期状態で全て下書き。
- 検証が完了したら `verified_at` と `published_at` を `YYYY-MM-DD` にし、`status: published` に変更してPRを作成する。GitHub側のマージ後、Zennへ `published: true` と公開日を反映する。公開日は予約投稿にも使用されるため日付を確認する。
- 記事の修正は必ずmain上の元原稿に行う。生成先 `zenn` ブランチの直接編集は次の同期で上書きされる。
- Zennのアカウント上で既に同名slugの記事が存在しないか、最初の公開前に確認する。

## ローカルで変換・検査

```bash
python -m pip install -r requirements-zenn.txt
python scripts/export_zenn.py
python scripts/export_zenn.py --check
python -m unittest discover -s scripts -p 'test_export_zenn.py' -v
```

生成先は既定で `.zenn-export/`。このディレクトリはGit管理せず、専用の `zenn` ブランチだけに生成結果をコミットする。別の出力先には `--output /path/to/directory` を指定できる。

記事中の相対画像は `/images/<zenn-slug>/...` に変換し、SVGはPNGに変換する。Zennの画像制限（PNG/JPEG/GIF/WebP・3MiB以内）を超える場合、同期しない。元原稿の画像は変更しない。

## 注意

`published: false` は公開一覧に掲載しないという意味であり、Zennに送られた下書きが絶対に第三者からアクセスできないという秘匿性の保証ではない。機密情報や未公開にすべき内容は連携ブランチに出力しないこと。PR作成時のZenn側下書き同期挙動についても[公式仕様](https://zenn.dev/zenn/articles/connect-to-github)を確認する。

ZennのGitHub同期は削除したMarkdownを自動で公開サイトから削除しない。記事の削除・非公開化はZenn管理画面側でも確認する。

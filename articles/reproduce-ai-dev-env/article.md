---
title: AI開発環境はpc-setupから構築し、dotfilesで設定を管理する
slug: reproduce-ai-dev-env
type: 手順
entries: [構築, 活用]
time_policy: 継続更新
status: draft
published_at: null
verified_at: null
sources:
  - https://github.com/rebuildup/pc-setup/blob/783359624ad80dee80ae92d49de4f5ee12709241/README.md
  - https://github.com/rebuildup/dotfiles/blob/929ec8c03e31eeb07340aa1f2b9c396a7f653a92/README.md
---

# AI開発環境はpc-setupから構築し、dotfilesで設定を管理する

公開されている[pc-setup](https://github.com/rebuildup/pc-setup)と[dotfiles](https://github.com/rebuildup/dotfiles)の構成では、Ubuntu/WSL・macOSの初期設定をpc-setupから始め、ユーザー設定をdotfilesに引き継ぐ。インストールと日常の設定を別々に管理できる。

## 端末へのインストールはpc-setupが担当する

[pc-setupのREADME（確認した版）](https://github.com/rebuildup/pc-setup/blob/783359624ad80dee80ae92d49de4f5ee12709241/README.md)に、Ubuntu/WSLとmacOS向けの共通の入口がある。

```bash
curl -fsSL https://raw.githubusercontent.com/rebuildup/pc-setup/main/bootstrap.sh | bash
```

このコマンドは公開手順の引用であり、この記事のために新しい端末で実行したわけではない。ネットワークから取得したスクリプトをそのまま実行する形式なので、**実行前に取得内容・更新履歴・既存環境への影響を確認する**。

Windows側で直接セットアップする場合は、PowerShell用の別スクリプトが用意されている。OS別の詳細は公式ではなく**この構成の実装元**である[pc-setup](https://github.com/rebuildup/pc-setup)を参照する。

## ユーザー設定の検査はdotfilesが担当する

pc-setupが引き継ぐ[dotfilesのREADME（確認した版）](https://github.com/rebuildup/dotfiles/blob/929ec8c03e31eeb07340aa1f2b9c396a7f653a92/README.md)には、導入後の確認コマンドがある。

```bash
cd ~/.dotfiles
./script/check
./script/secrets-doctor
git submodule status --recursive
```

`script/check`は設定の整合性、`secrets-doctor`は秘密情報管理との接続を確認する。**設定が正しく配置されたことと、認証できることは別**だ。秘密情報はリポジトリに書き込まず、Infisicalのログインや権限で扱う。

## エージェントは使うプロバイダを明示して起動できる

[agentランチャーの説明](https://github.com/rebuildup/dotfiles/blob/929ec8c03e31eeb07340aa1f2b9c396a7f653a92/docs/agent-launcher.md)では、利用する経路を一覧し、設定を検査してから起動できる。

```bash
agent list
agent check
agent claude
```

`agent claude`はプロバイダの指定がないため、ネイティブの起動経路を使う。環境ごとに選びたいモデルや認証方法が違う場合は、[説明されているルート指定](https://github.com/rebuildup/dotfiles/blob/929ec8c03e31eeb07340aa1f2b9c396a7f653a92/docs/agent-launcher.md)を確認する。

## 新規端末での再現テストは未実施

この手順は公開ソースから確認できる範囲を整理したものだ。新しい端末で最後まで実行し、実画面・エラー例・インストール後の動作を確認した記録はまだない。**再現完了の手順として公開する前に**、OSの版、認証、必要な権限を明示した実機テストが必要になる。

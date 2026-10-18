---
title: "既存のCLIで足りるなら、MCPを追加する必要はない"
emoji: "🔌"
type: tech
topics: [ai, mcp, cli]
published: false
---
定型的な操作をコマンドで実行できるなら、まずCLIを利用する。AIアプリが外部ツールを共通の形式で発見・呼び出す必要がある場合に、MCPの導入を検討すればよい。**CLIとMCPは上下関係ではなく、操作を呼び出す方法が異なる。**

## CLIは人間やスクリプトから操作を再現しやすい

[GitHub CLIの公式リファレンス](https://docs.github.com/en/github-cli)にある`gh`コマンドは、端末やスクリプトからGitHubの操作を実行する手段だ。

```bash
gh pr list
gh issue list
```

既存のコマンドが十分なら、それをシェルスクリプトやCIから使うだけでよい。AIがそのコマンドを実行できる環境なら、ツール専用サーバーを別途管理せずに済む場合もある。

## MCPは一つのHostから複数のServerにつなげる

[Model Context Protocolの公式アーキテクチャ（2026-07-28版）](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/learn/architecture.mdx)では、AIアプリが**Host**となり、接続先のServerごとに**Clientを一つずつ**作る。Serverはツール・リソース・プロンプトを提供する。

![AIアプリのHost内にClientが2つあり、それぞれローカルServerとリモートServerへ個別に接続するMCP構成](/images/mcp-or-cli-guide/mcp-architecture.png)

*図は上記の公式アーキテクチャを基に再構成。1つのHost内のClientとServerが接続単位ごとに対応することを示している。*

CLIと異なり、MCPには接続の初期化、機能の通知、メッセージ形式、トランスポートなどの取り決めがある。例えばローカルでは標準入出力、リモートではHTTPを使える。

## AIアプリでツールを共有するときはMCPが候補になる

| 必要なこと | 選び方 |
| --- | --- |
| 手元でコマンドを一度動かす | CLI |
| シェル・CIから同じ操作を繰り返す | CLI |
| 複数のAIアプリでツールの仕様を共有する | MCPを検討 |
| ツール・リソースをアプリから発見する | MCPを検討 |
| 追加サーバーの運用や認可を避けたい | CLIで済むか先に確認 |

MCPだから自動的に安全になるわけではない。Serverに与える権限、扱えるデータ、実行前の承認は別に設計する必要がある。

**判断の順序は「使えるCLIがあるか」「AIアプリにどんな統合が必要か」「MCPの追加コストに見合うか」**で十分だ。

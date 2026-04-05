# copilot-agent-template

汎用 VS Code GitHub Copilot エージェントカスタマイズキット。任意のプロジェクトリポジトリを指定すると、`@Setup` エージェントがコードベースを読み取り、そのプロジェクト向けにカスタマイズされたパッケージを生成します: ルートの `AGENTS.md`、ワークスペースの `.github/` ファイル、および `.vscode/settings.json`。

> 🌐 [English](./README.md)

## 生成されるファイル

```
<your-project>/
├── AGENTS.md                        # プロジェクトの制約とファイルマップ
├── .vscode/
│   └── settings.json                # エージェントハンドオフとスキルの場所の設定
└── .github/
  ├── copilot-instructions.md      # 常時有効なワークスペース指示
  ├── agents/
  │   ├── <project>.agent.md       # 自律的な「なんでもやる」エージェント
  │   ├── explore.agent.md         # 読み取り専用の探索
  │   ├── plan.agent.md            # タスク計画、承認用プランを出力
  │   ├── implementer.agent.md     # 承認済みプランをハンドオフで実行
  │   ├── reviewer.agent.md        # セキュリティ・品質監査
  │   └── verification.agent.md   # lint / ビルド / テストの実行
  ├── instructions/
  │   ├── src-coding.instructions.md
  │   └── testing.instructions.md
  ├── prompts/
  │   ├── plan-change.prompt.md
  │   ├── implement-change.prompt.md
  │   └── verify-workspace.prompt.md
  ├── hooks/
  │   └── pre-tool-use.json        # 任意の確認フックの例
  ├── scripts/
  │   ├── guard-dangerous-command.sh
  │   └── run-project-checks.sh    # sh が利用可能な場合の POSIX ヘルパー
  └── skills/
    └── <domain>/
      ├── SKILL.md
      └── [任意のバンドルアセット]
```

## ワークフロー

### 1. このリポジトリをプロジェクトの隣にクローン

```sh
# プロジェクトを含む親ディレクトリで:
git clone https://github.com/your-org/copilot-agent-template
```

サブモジュールとして追加する場合:

```sh
cd your-project
git submodule add https://github.com/your-org/copilot-agent-template .agent-setup
```

### 2. VS Code で両フォルダーをマルチルートワークスペースとして開く

```jsonc
// .code-workspace
{
  "folders": [
    { "path": "/path/to/your-project" },
    { "path": "/path/to/copilot-agent-template" }
  ]
}
```

または **ファイル → フォルダーをワークスペースに追加** で両フォルダーを開きます。

### 3. `@Setup` エージェントを実行

VS Code Copilot Chat で次のように入力します:

```
@Setup /path/to/your-project
```

エージェントは以下を実行します:
1. プロジェクトの `README.md`、パッケージマネージャーのマニフェスト、アーキテクチャドキュメント、代表的なソースファイルとテストファイルを読み取る
2. 技術スタック、規約、ビルドおよびテストコマンド、ランタイム設定、ドメイン制約を特定する
3. ルートの `AGENTS.md`、`.github/`、`.vscode/settings.json`、プロンプト、およびプロジェクトのランタイム規約に合ったフック・ヘルパースクリプト・スキルアセットを生成する
4. 作成または更新されるファイルを表示し、書き込み前に確認を求める

付属の PreToolUse フックは利便性のための例であり、強固なセキュリティ境界ではありません。より強力な保護が必要な場合は、フックをリポジトリ外のユーザー管理スクリプトに向けるか、OS レベルの権限でヘルパースクリプトを保護してください。

シェルベースのヘルパーは POSIX の `sh` ランタイムを想定しています。ターゲットプロジェクトがすでに `sh` に依存している場合にのみ生成し、そうでない場合はスキップしてプラットフォーム固有のフォローアップをユーザーに委ねます。

### 4. テンプレートをワークスペースから削除（任意）

セットアップが完了したら、このリポジトリをワークスペースから削除できます。生成されたカスタマイズファイルはプロジェクト内の `AGENTS.md`、`.github/`、`.vscode/settings.json` に格納されています。

### 5. 生成されたエージェントを使用

プロジェクトで以下を使用します:

```
@<ShortAgentName> # 完全自律エージェント（例: @APP）
@Plan             # 実装計画の設計
@Reviewer         # コード変更の監査
@Verification     # テスト + lint の実行
@Explore          # 読み取り専用のコードベース探索
```

`Implementer` は主にユーザーのメインエントリーポイントとしてではなく、`@Plan` からのハンドオフターゲットとして使用されます。

## セットアップの再実行

プロジェクト構造が大幅に変わった場合は、`@Setup` を再実行してカスタマイズファイルを更新します。エージェントは既存のカスタマイズファイルを検出し、作成または更新すべきファイルをまとめて表示します。

## テンプレートリファレンス

`{{PLACEHOLDER}}` マーカーを含む生のテンプレートは [`templates/`](./templates/) を参照してください。セットアップエージェントがプロジェクト分析から自動的に埋め込みます。

## スキーマリファレンス

抽出対象の全リストは [`schema/project-profile.md`](./schema/project-profile.md) を参照してください。生成された `AGENTS.md` を編集することで、エージェントが把握する情報を調整できます。

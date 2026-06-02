# copilot-agent-template

汎用 VS Code GitHub Copilot エージェントカスタマイズキット。任意のプロジェクトリポジトリを指定すると、`@Setup` エージェントがコードベースを読み取り、そのプロジェクト向けにカスタマイズされたパッケージを生成します: ルートの `AGENTS.md`、ワークスペースの `.github/` ファイル、`.vscode/settings.json`、そしてオプションの GitHub Actions トリガー。

**従量課金環境向け設計**: トリアージベースのモデルルーティング・フェーズ間状態圧縮・サーキットブレーカーによるリトライ制御で、コード品質を落とさずに推論コストを最小化します。

> 🌐 [English](./README.md)

## 自律コーディングループ

このテンプレートは [claw-code](https://github.com/ultraworkers/claw-code) が採用する3層自律パターンを再現します:

| レイヤー | claw-code | Copilot 対応 |
|---|---|---|
| **実行ループ** | OmX / oh-my-codex | `<project>.agent.md` — triage → explore → plan → implement → verify → review |
| **イベントトリガー** | clawhip | `copilot-autoassign.yml` — ラベル → トリアージ → Copilot が PR 作成 |
| **マルチエージェント調整** | OmO / oh-my-openagent | レーン状態 JSON ハンドオフ・Reflexion 修復・サーキットブレーカー |

**ヒューマンインターフェース**: GitHub Issue を作成して `copilot` ラベルを付けるだけ（ブラウザ・スマホ・CLI から）。エージェントがあとは自動処理します。

## 生成されるファイル

```
<your-project>/
├── AGENTS.md                          # プロジェクトの制約とファイルマップ
├── .vscode/
│   └── settings.json                  # エージェントハンドオフとスキルの場所の設定
└── .github/
    ├── copilot-instructions.md        # 常時有効なワークスペース指示
    ├── schema/
    │   ├── lane-state.schema.json     # フェーズ間状態オブジェクト（Trajectory Reduction）
    │   ├── reflexion.schema.json      # 構造化失敗診断レポート（ターゲット修正用）
    │   └── task-triage.schema.json    # Issue 分類結果（Level 1/2/3）
    ├── workflows/
    │   └── copilot-autoassign.yml     # キーワードトリアージ → モデルルーティング → PR 自動作成
    ├── agents/
    │   ├── <project>.agent.md         # 自律パイプラインエージェント（オーケストレーター）
    │   ├── explore.agent.md           # 読み取り専用探索  [model: lightweight]
    │   ├── plan.agent.md              # タスク計画        [model: advanced]
    │   ├── implementer.agent.md       # プラン実行        [model: advanced]
    │   ├── reviewer.agent.md          # セキュリティ・品質 [model: standard]
    │   └── verification.agent.md      # lint/ビルド/テスト [model: lightweight]
    ├── prompts/
    │   ├── plan-change.prompt.md
    │   ├── implement-change.prompt.md  # Point-to-Point 差分のみ
    │   └── verify-workspace.prompt.md
    ├── hooks/
    │   ├── pre-tool-use.json
    │   └── post-tool-use.json
    ├── scripts/
    │   ├── guard-dangerous-command.sh
    │   ├── run-project-checks.sh
    │   ├── create_skill.py            # メタツール: エージェントが実行時にスキルを作成
    │   ├── refactor_skills.py         # 夜間バッチ: 重複スキルをマージ
    │   └── security/
    │       ├── codeql-scan.sh         # SAST ラッパー（CodeQL → gh CLI → ESLint フォールバック）
    │       └── sast-api.py            # Python 製統合 SAST アダプター
    └── skills/
        └── <domain>/
            ├── SKILL.md
            └── [任意のバンドルアセット]
```

## コスト最適化アーキテクチャ

従量課金 API でトークンコストを最小化しながらコード品質を担保する7つの施策:

### 1. Semantic Routing — LLM 呼び出し前の Issue トリアージ

`copilot-autoassign.yml` が**キーワードマッチング（LLMコストゼロ）**で Issue を3段階に分類します:

| Level | 説明 | 例 | アクション |
|---|---|---|---|
| **1** | 軽微: タイポ・リネーム・フォーマット | "README のタイポ修正", "関数 X をリネーム" | ファイル名が明記されていれば explore をスキップ; 全フェーズ軽量モデル |
| **2** | 標準: 新コンポーネント・バグ修正 | "ログインボタン追加", "認証エラー修正" | フルパイプライン; explore/verify は軽量モデル |
| **3** | アーキテクチャ: マイグレーション・大規模リファクタ | "GraphQL 移行", "認証システム再設計" | **人間承認ゲート**が必要; 高度モデル使用 |

### 2. フェーズ別モデルルーティング — 適材適所のモデル選択

各エージェントファイルに `model:` frontmatter を設定。オーケストレーターがトリアージレベルに応じてモデルティアを選択します:

| フェーズ | Level 1 | Level 2 | Level 3 |
|---|---|---|---|
| explore | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_STANDARD}}` |
| plan | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_ADVANCED}}` | `{{MODEL_ADVANCED}}` |
| implement | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_ADVANCED}}` | `{{MODEL_ADVANCED}}` |
| verify | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_STANDARD}}` |
| review | `{{MODEL_LIGHTWEIGHT}}` | `{{MODEL_STANDARD}}` | `{{MODEL_STANDARD}}` |

`@Setup` 時に `{{MODEL_LIGHTWEIGHT}}`・`{{MODEL_STANDARD}}`・`{{MODEL_ADVANCED}}` を一度だけ設定すれば、全エージェントに自動反映されます。Claude Code ユーザーはオーケストレーターが `Agent` ツール呼び出し時に `model:` パラメーターを動的に指定します。

### 3. Trajectory Reduction — フェーズ間の状態圧縮

オーケストレーターはフェーズ間で生の会話履歴を転送しません。代わりに、各フェーズ遷移で必要最小限の情報だけを `LaneState` JSON に圧縮して渡します（スキーマ: `.github/schema/lane-state.schema.json`）:

```json
{
  "phase": "explore",
  "task": "ログインボタンを追加する",
  "triage_level": 2,
  "relevant_files": ["src/auth/login.ts"],
  "plan_steps": [],
  "changed_files": [],
  "retry_count": 0,
  "error_fingerprints": []
}
```

これにより、5+ エージェント呼び出しにわたって会話履歴が転送される際の入力トークン爆発を防ぎます。

### 4. Point-to-Point 編集 — 差分だけを出力

Implementer エージェントはファイル全体を Write ツールで上書きすることが禁止されています。すべての変更は Search/Replace 差分編集のみ — 変更行だけが生成されるため、大きなファイルでは出力トークンが10〜100倍削減されます。

### 5. Reflexion + サーキットブレーカー — 構造化自己修正でループを防止

検証が失敗した際、Verification エージェントは自由形式のエラーテキストではなく `ReflexionReport` JSON を生成します（スキーマ: `.github/schema/reflexion.schema.json`）:

```json
{
  "error_type": "test",
  "error_fingerprint": "test:TS2345_login_return_type",
  "root_cause": "login() の戻り値型が string から Promise<string> に変わった",
  "affected_files": [{ "path": "src/auth.test.ts", "line": 42, "issue": "await が不足" }],
  "fix_plan": [{
    "file": "src/auth.test.ts",
    "search": "expect(login())",
    "replace": "expect(await login())",
    "rationale": "login が async になったため await が必要"
  }],
  "safe_to_retry": true
}
```

Implementer は `fix_plan` の各エントリを Point-to-Point 差分編集で適用します — 推測不要。

**サーキットブレーカー**: 同一の `error_fingerprint` が `lane_state.error_fingerprints[]` に2回出現すると、パイプラインは即座に停止して人間にエスカレーションします。トークンをループで浪費しません。

### 6. Shift-Left SAST — 実装フェーズへのセキュリティ検査の前出し

Implementer が各ステップ完了前に `{{SAST_COMMAND}}` を実行します。事後のレビューループ（修正コストが高い）ではなく、実装中（修正コストが低い）にセキュリティ問題を検出します。

利用可能なラッパー（可用性に応じて自動選択）:
- `codeql` CLI
- `semgrep`（auto config）
- ESLint security プラグイン（JS/TS フォールバック）
- GitHub Advanced Security API（gh CLI フォールバック）

### 7. Voyager パターンのスキルライブラリ — 再推論ではなく再利用

`create_skill.py` が成功した実装を `SKILL.md` に蒸留します。`refactor_skills.py` が夜間に重複スキルをマージします。新タスクはまずスキルライブラリを検索 — 一致があれば保存済み手順を適用するだけで、ゼロからの LLM 推論が不要になります。

## 自律パイプライン

```
[ワークフロー] triage（キーワードマッチング、LLMコストゼロ）
                   ↓
[エージェント] ▶ [LANE:explore]   → ✓ [LANE:explore:complete]    {軽量モデル}
               ▶ [LANE:plan]      → ✓ [LANE:plan:complete]       {高度モデル}
               ▶ [LANE:implement] → ✓ [LANE:implement:complete]   {高度モデル + SAST}
               ▶ [LANE:verify]    → ✓ [LANE:verify:complete]     {軽量モデル + Reflexion}
               ▶ [LANE:review]    → ✓ [LANE:review:complete]     {標準モデル}
```

各フェーズ間: レーン状態 JSON をシリアライズ（会話履歴は転送しない）。

`✗ [LANE:{name}:blocked]` イベントはフェーズが失敗してパイプラインが停止したことを意味します。ブロックされたエージェントは理由を報告し、可能な場合は上流エージェントに自己修正を委譲します。サーキットブレーカーが発動した場合（同一 `error_fingerprint` が2回出現）、パイプラインは即座に停止して人間に報告します。

複数セッションにまたがる大型タスクでは、自律エージェントがコンテキスト終了前に現在の `lane_state` JSON を含む `SESSION CHECKPOINT` ブロックを出力します。新セッションでチェックポイントを読み込めば、完了済みフェーズをスキップして再開できます。

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
{
  "folders": [
    { "path": "/path/to/your-project" },
    { "path": "/path/to/copilot-agent-template" }
  ]
}
```

### 3. `@Setup` エージェントを実行

VS Code Copilot Chat で入力:

```
@Setup /path/to/your-project
```

エージェントは以下を実行します:
1. `README.md`・パッケージマネージャーマニフェスト・アーキテクチャドキュメント・ソースファイルを読み取る
2. 技術スタック・規約・ビルド/テストコマンドを特定する
3. `{{MODEL_LIGHTWEIGHT}}`・`{{MODEL_STANDARD}}`・`{{MODEL_ADVANCED}}` を環境に最適なモデルに設定する
4. インストール済みのセキュリティツールに基づいて `{{SAST_COMMAND}}` を設定する（`codeql`・`semgrep`・`eslint-plugin-security`）
5. `AGENTS.md`・`.github/`・`.vscode/settings.json`・プロンプト・フック・セキュリティスクリプト・スキルを生成する
6. 作成または更新されるファイルを表示し、書き込み前に確認を求める

### 4. 生成されたエージェントを使用

**VS Code Copilot Chat から:**

```
@<ShortAgentName> implement X    # 完全自律実行
@Plan             実装計画の設計
@Reviewer         コード変更の監査
@Verification     テスト + lint の実行
@Explore          読み取り専用のコードベース探索
```

プロンプトショートカット (`.github/prompts/`):
- **Plan Change** — 機能・バグ修正の構造化計画
- **Implement Change** — フルパイプライン実行（Point-to-Point 差分 + SAST 必須）
- **Verify Workspace** — ターゲットを絞った lint/build/test（失敗時は Reflexion JSON 出力）

**任意のデバイスから（GitHub Issue → 自律 PR）:**

1. GitHub Issue を作成してタスクを説明する
2. `copilot` ラベル（またはセットアップ時に設定したラベル）を追加する
3. ワークフローが自動的に Issue を分類（Level 1/2/3）して Copilot にアサイン
4. Level 3 タスクは人間承認ラベルが付くまでパイプラインを停止
5. エージェントがフルパイプラインを実行して PR を作成（ローカル環境不要）

## セットアップの再実行

プロジェクト構造が大幅に変わった場合は、`@Setup` を再実行してカスタマイズファイルを更新します。

## テンプレートリファレンス

`{{PLACEHOLDER}}` マーカーを含む生のテンプレートは [`templates/`](./templates/) を参照してください。

主要テンプレート:
- `templates/agents/autonomous.template.agent.md` — Trajectory Reduction・サーキットブレーカー付き6フェーズパイプライン
- `templates/agents/explore.template.agent.md` — 読み取り専用探索（`model: {{MODEL_LIGHTWEIGHT}}`）
- `templates/agents/plan.template.agent.md` — 計画（`model: {{MODEL_ADVANCED}}`）
- `templates/agents/implementer.template.agent.md` — Point-to-Point 実装（`model: {{MODEL_ADVANCED}}`）
- `templates/agents/verification.template.agent.md` — Reflexion 出力付き検証（`model: {{MODEL_LIGHTWEIGHT}}`）
- `templates/agents/reviewer.template.agent.md` — OWASP セキュリティレビュー（`model: {{MODEL_STANDARD}}`）
- `templates/workflows/copilot-autoassign.template.yml` — 3ジョブ Semantic Routing ワークフロー
- `templates/schema/lane-state.schema.json` — フェーズ間状態コントラクト
- `templates/schema/reflexion.schema.json` — 構造化失敗診断コントラクト
- `templates/schema/task-triage.schema.json` — Issue 分類コントラクト
- `templates/scripts/security/codeql-scan.template.sh` — SAST シェルラッパー
- `templates/scripts/security/sast-api.template.py` — Python SAST アダプター

## エージェントメタツール: 自律スキル作成と夜間リファクタリング

`templates/scripts/` の2つのPythonスクリプトにより、エージェントが**実行時に自らのスキルライブラリを成長**させられます — [Voyager](https://voyager.minedojo.org/) 自己改善エージェントアーキテクチャに着想。

### `create_skill.py` — 解決済みタスクを再利用可能なスキルに蒸留

```sh
python .agent/tools/create_skill.py \
    --name "sort_3dgs_splats" \
    --description "3DGS Splat データをビュー空間の深度でソート" \
    --code_file "temp_sort.ts" \
    --domain "3dcg" --subdomain "3dgs" \
    --facets "lang:typescript,target:browser" \
    --skills_dir ".agent/skills"
```

### `refactor_skills.py` — 夜間バッチによる重複スキルの統合

```sh
# ドライラン（書き込みなし）
python .agent/tools/refactor_skills.py --skills_dir .agent/skills

# 重複スキルをマージ
python .agent/tools/refactor_skills.py --skills_dir .agent/skills --merge
```

### OJT ループ

| フェーズ | 内容 |
|---|---|
| **1 試行** | スキル DB を検索し、既存知識でタスクを試みる |
| **2 探索・検索** | 失敗時にドキュメントを読み、コードを更新する |
| **3 検証** | テストを実行; 全アサーションが通過するまでフェーズ2を繰り返す |
| **4 蒸留・保存** | `create_skill.py` を呼び出して成功実装を保存 |

## スキーマリファレンス

`{{PLACEHOLDER}}` 抽出対象の全リストは [`schema/project-profile.md`](./schema/project-profile.md) を参照してください。`{{MODEL_LIGHTWEIGHT}}`・`{{MODEL_ADVANCED}}`・`{{SAST_COMMAND}}`・`{{PRIMARY_LANGUAGE_CODEQL}}` などの新しいプレースホルダーも含まれます。

## ドメインスキル足場

`templates/skills/` は生成されたエージェントが参照するドメイン固有の知識パックの足場を提供します: コーディング・3DCG・CAD・ML・ゲームエンジン。レイアウトは **`<domain>/<subdomain>/SKILL.md`** 形式。


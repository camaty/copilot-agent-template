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

## ドメインスキル足場

`templates/skills/` は、生成されたエージェントが参照するドメイン固有の知識パックの足場を提供します — コーディング（ネットワーク、組込み）、3D CG（Blender、Houdini）、CAD（パラメトリック）、機械学習（学習、推論）、ゲームエンジン（Unity、Unreal）。レイアウトは **`<domain>/<subdomain>/SKILL.md`** 形式で、言語・ターゲット・ベンダーなどの直交軸はフォルダーを深くするのではなくフロントマターの `facets:` で表現します。

- [`templates/skills/README.md`](./templates/skills/README.md) — レイヤーモデルとディレクトリレイアウト
- [`templates/skills/EXTENDING.md`](./templates/skills/EXTENDING.md) — モデルを壊さずに新しいドメイン／サブドメインを追加する方法
- [`templates/skills/_layout/`](./templates/skills/_layout/) — 再利用可能な `DOMAIN_INDEX.template.md` と `SUBDOMAIN_SKILL.template.md`

### 優先ドメイン: Generative Spatial Computing

上記のベースドメイン（コーディング・3DCG・CAD・ML・ゲームエンジン）は、本テンプレートがスキル整備の優先ベクトルとして据える、より広い領域 — **3DGS・基盤モデル・ネットワーク・セキュリティが交差する「自律的でセキュアな空間コンピューティング」** — を構成します。`templates/skills/` 配下に新しいスキルを追加する際は、まず以下のクラスタのいずれかに位置付けてください。

1. **次世代Webグラフィックスと空間レンダリング基盤**
   - WebGPU および TSL/WGSL によるレンダリング最適化（マルチパスシェーダー、ブラウザ上での直接 GPU 計算）。
   - 3DGS ビューアの高度化と超解像（FSR）— 大容量 Splat データを Web 上でリアルタイムにストリーミング・編集・コンポジット。
   - 物理ベースのボリュメトリック・シミュレーション（Taylor–Sedov 爆発モデル、流体演算）を GLSL/WGSL シェーダー内で完結させる実装。

2. **決定論的AI制御（ハーネス・エンジニアリング）とプロシージャル CAD**
   - スマート CG API とエージェント連携：厳格な API スキーマと決定論的チェッカーで LLM のハルシネーションを排除し、確実な 3D シーン構築を担保するアーキテクチャ。
   - トポロジー制約型のアセンブリ自動化（"IKEA トポロジー"、Point-to-Point 合致など）による歯車・家具などの機能的 CAD モデル自動生成。
   - 上位の構造設計モデルと、階層化リファレンスを参照する下位ローカルモデル群（Qwen 等）を並列稼働させる Map-Reduce 型のマルチエージェント・コード生成エコシステム。

3. **デジタルヒューマンとモーション基盤モデル**
   - 単一 RGB 動画から骨格キネマティクスを抽出し VRM 等に適用可能な BVH を生成する自己回帰型モーション生成基盤モデル。
   - 2D-to-3D のクロスシミュレーションとフィッティング：平面デザインからアバター適用可能な 3D 衣服を生成し、自然なドレープを物理演算で再現するパイプライン。

4. **空間アセットのためのセキュアな開発・通信インフラ**
   - 大容量 3D バイナリの高速転送プロトコル（Aspera 等の UDP ベース高帯域幅転送）による 3DGS シーン・学習データセットのシームレス同期基盤。
   - GitHub Advanced Security 等を利用した、エージェントが自動生成したスクリプト／3D パイプラインの静的セキュリティ解析（SCA）— インジェクションや非同期処理の競合などを検出。

5. **Embodied AI（身体性AI）と合成データ生成**
   - Unity / Unreal Engine を用いたシミュレーション環境構築：慣性航法モデルや自律移動アルゴリズムの訓練向けに、物理的に正確な合成データをゲームエンジン上で大量生成。
   - 空間認識のための VLM（視覚言語モデル）統合：3D スキャン現実空間（点群・3DGS）を AI に解釈させ、オブジェクトのセマンティックなレイアウトを自律的に編集・再構成。

新しいスキルを追加するときは、最も適合する既存ベースドメイン配下（例：`3dcg/3dgs/`、`coding/webgpu/`、`gameengine/unity-synthetic-data/`）に置き、SKILL.md のフロントマター `facets:` で上記 5 クラスタのどれに資するかを明示してください。

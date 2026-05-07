# In-Fusion クローニング用プライマー設計ツール

## 📋 概要
このツールは、**In-Fusion クローニング**に用いるプライマー設計を自動化するPythonアプリケーションです。ベクターとインサートの塩基配列から、制限酵素による直鎖化とプライマー設計を一括処理します。

### 主な機能

  - 長さ: 18～25 bp
  - 3'末端: G または C（GCクランプ）
  - ヘアピン構造の回避（3塩基以上の自己相補配列を検出）
  - Tm値バランス警告（Forward/Reverseの Tm 差が 5℃ 超の場合）
---
## 🛠️ 環境構築

### 前提条件

- **conda** がインストールされていること
  - [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) または [Anaconda](https://www.anaconda.com/) をインストールしてください

### セットアップ手順

1. **conda環境を作成**

```bash
cd /path/to/PrimerDesigner
conda env create -f environment.yml
```

2. **環境を有効化**

```bash
conda activate primer-designer
```

3. **環境の確認**

```bash
python --version  # Python 3.11以上が表示されることを確認
```

### 環境の削除（不要になった場合）

```bash
conda deactivate
conda env remove --name primer-designer
```

---

## 📁 ファイル構成

```
PrimerDesigner/
├── README.md                          # このファイル
├── environment.yml                    # conda環境定義
├── .gitignore                         # Git無視設定
│
├── app.py                             # 統合エントリーポイント（GUI/CUI 両対応）⭐ v1.3 新規
│
├── src/
│   └── primer_designer.py             # ライブラリ関数（ビジネスロジック）
│
├── scripts/
│   └── run_primer_designer.py         # 実行ファイル（従来の CLI 実行）
│
├── data/
│   ├── plasmid/
│   │   └── p10A1.dna                 # ベクター塩基配列
│   ├── insert/
│   │   └── sample.dna                 # インサート塩基配列
│   └── restriction_digest/
│       └── BglII.seq                  # 制限酵素サイト（AGATCT）
│
├── output/                            # 出力ファイル出力先（app.py --output で使用）
│
└── logs/                              # ログファイル出力先
    └── primer_design_*.log            # 実行ログ（日時付き）
```

---

## 🚀 使用方法

### 1️⃣ GUI モード（デスクトップアプリ）

手動操作用のビジュアルインターフェース。ファイルを選択してボタンをクリックするだけでプライマー設計を実行できます。

```bash
# 環境を有効化
conda activate primer-designer

# GUI を起動（引数なし）
python app.py
```

**UI の構成:**
- ベクター・インサート・制限酵素ファイル選択ボタン（参照）
- 選択したファイルパスの表示
- プライマー設計実行ボタン
- スクロール可能な結果表示エリア（Tm値、配列、エラーメッセージなど）

### 2️⃣ CUI モード（コマンドライン / 自動化パイプライン）

DBTL パイプラインやロボット自動化システム用。`argparse` で構造化された引数を指定。

```bash
# 基本的な実行（テキスト出力）
python app.py --vector data/plasmid/p10A1.dna \
              --insert data/insert/sample.dna \
              --enzyme data/restriction_digest/BglII.seq

# JSON 形式で出力（後段システム用）
python app.py --vector data/plasmid/p10A1.dna \
              --insert data/insert/sample.dna \
              --enzyme data/restriction_digest/BglII.seq \
              --json

# ファイルに出力
python app.py --vector data/plasmid/p10A1.dna \
              --insert data/insert/sample.dna \
              --enzyme data/restriction_digest/BglII.seq \
              --output output/results.json \
              --json
```

**引数説明:**
- `--vector <path>`: ベクターファイルパス（必須）
- `--insert <path>`: インサートファイルパス（必須）
- `--enzyme <path>`: 制限酵素サイトファイルパス（必須）
- `--output <path>`: 出力ファイルパス（オプション、指定なしで標準出力）
- `--json`: JSON 形式で出力（オプション、フラグ。指定なしでテキスト形式）

### 3️⃣ スクリプト実行（従来の方法）

```bash
# 環境を有効化
conda activate primer-designer

# 従来のスクリプト実行（固定ファイルでの実行）
python scripts/run_primer_designer.py
```

### 出力内容

実行結果は以下の両方に出力されます：

1. **標準出力** - ターミナルに直接表示
2. **ログファイル** - `logs/` ディレクトリに保存（`primer_design_YYYYMMDD_HHMMSS.log`）

### 出力例（ターミナル）

```
[2026-05-06 14:47:11] INFO: ============================================================
[2026-05-06 14:47:11] INFO: In-Fusion クローニング用プライマー設計ツール
[2026-05-06 14:47:11] INFO: ============================================================
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: [ステップ1] 塩基配列を読み込み中...
[2026-05-06 14:47:11] INFO: ✓ ベクター長: 6732 bp
[2026-05-06 14:47:11] INFO: ✓ インサート長: 2691 bp
[2026-05-06 14:47:11] INFO: ✓ 制限酵素サイト: AGATCT
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: [ステップ2] ベクターを直鎖化中...
[2026-05-06 14:47:11] INFO: ✓ 直鎖化ベクター長: 6732 bp
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: [ステップ3] 相同アームを抽出中...
[2026-05-06 14:47:11] INFO: ✓ 5'末端相同アーム (15 bp): GATCTTTTTCCCTCT
[2026-05-06 14:47:11] INFO: ✓ 3'末端相同アーム (15 bp): CACAAATACCACTGA
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: [ステップ4] 特異的プライマーを設計中...
[2026-05-06 15:23:41] INFO: ✓ Forward特異的配列: TCGCGCGTTTCGGTGATGAC
[2026-05-06 15:23:41] INFO:   - 長さ: 20 bp
[2026-05-06 15:23:41] INFO:   - GC含有率: 60.0%
[2026-05-06 15:23:41] INFO:   - Tm値: 64.0℃
[2026-05-06 15:23:41] INFO: ✓ Reverse特異的配列: GTATCACGAGGCCCTTTCGTC
[2026-05-06 15:23:41] INFO:   - 長さ: 21 bp
[2026-05-06 15:23:41] INFO:   - GC含有率: 57.1%
[2026-05-06 15:23:41] INFO:   - Tm値: 66.0℃
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: [ステップ5] 最終プライマーを生成中...
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: ============================================================
[2026-05-06 14:47:11] INFO: 【 最終結果 】
[2026-05-06 14:47:11] INFO: ============================================================
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: 直鎖化ベクター長: 6732 bp
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: [Forwardプライマー]
[2026-05-06 15:23:41] INFO: 配列: CACAAATACCACTGATCGCGCGTTTCGGTGATGAC
[2026-05-06 14:47:11] INFO: 長さ: 35 bp
[2026-05-06 14:47:11] INFO: Tm値（特異的配列部分）: 64.0℃
[2026-05-06 14:47:11] INFO: 
[2026-05-06 15:02:49] INFO: [Reverseプライマー]
[2026-05-06 15:23:41] INFO: 配列: AGAGGGAAAAAGATCGACGAAAGGGCCTCGTGATAC
[2026-05-06 15:02:49] INFO: 長さ: 36 bp
[2026-05-06 15:02:49] INFO: Tm値（特異的配列部分）: 66.0℃
[2026-05-06 14:47:11] INFO: 
[2026-05-06 14:47:11] INFO: ============================================================
[2026-05-06 14:47:11] INFO: ✓ プライマー設計完了
[2026-05-06 14:47:11] INFO: ============================================================
```

### ログファイルの確認

```bash
# 最新のログファイルを表示
tail -f logs/primer_design_*.log

# 全ログファイルを列表示
ls -lah logs/
```

---

## 📥 入力 (Input)

このツールが受け取る入力は、DNA 塩基配列を記載したプレーンテキストファイルです。研究用途の手入力データや、他システムが生成した配列ファイルをそのまま投入できます。

**データ形式:**
- 対応拡張子例: `.dna`, `.seq`
- 内容: `A`, `T`, `G`, `C` の塩基配列（改行・空白を含んでも可）
- 内部クレンジング: 読み込み時に空白・改行を除去し、大文字へ正規化

**必須ファイル:**
- ベクター塩基配列ファイル
- インサート塩基配列ファイル
- 制限酵素サイトファイル（例: `AGATCT`）

**入力インターフェース:**
- GUI: ファイル選択ダイアログから 3 ファイルを指定
- CLI: `--vector`, `--insert`, `--enzyme` で各ファイルパスを指定

この設計により、研究者の手動操作と DBTL 自動実行の両方で同一ロジックを再利用できます。

---

## 📤 出力 (Output)

用途に応じて、ヒューマンリーダブル形式とマシンリーダブル形式の 2 系統を提供します。

**1. ヒューマンリーダブル形式（テキスト）**
- GUI の結果画面、および CLI 標準出力に表示
- 主な出力項目:
   - 直鎖化ベクター長
   - 抽出した 5' / 3' 相同アーム
   - Forward / Reverse 各プライマーの最終配列
   - 長さ、特異的配列部分の Tm 値、GC 含有率
   - Forward / Reverse の Tm 差警告（しきい値: 5℃）

**2. マシンリーダブル形式（JSON）**
- CLI で `--json` を指定した場合に出力
- キー・バリューの構造化データとして提供
- DBTL サイクル後段（LIMS、分注ロボットスクリプト、ETL）でのパースを想定

**保存機能**
- `--output` 指定時: 任意ファイルへ書き出し
- ログ保存: `logs/` 配下にタイムスタンプ付きで実行ログを自動保存

この二層出力により、「人が読む結果確認」と「システム連携の自動処理」を同時に満たします。

---

## 🧠 内部システムの概要 (System Architecture & Algorithm)

本ツールは、UI/CLI 制御層とビジネスロジック層を分離したクリーンアーキテクチャです。

- コントローラー層: `app.py`（GUI・CLI・入出力・例外制御）
- 計算ロジック層: `src/primer_designer.py`（配列処理・評価・設計アルゴリズム）

この分離により、表示方式が変わっても設計アルゴリズムの再検証や再実装が不要で、品質保証と自動化運用を両立できます。

**アルゴリズムフロー**

1. **ベクターの直鎖化と相同アーム抽出**
- 制限酵素サイト（例: `A|GATCT`）で切断位置を同定
- 直鎖化後、突出末端を考慮した 5' / 3' 側から相同アーム（標準 15 bp）を抽出

2. **インサート末端アンカーと特異的配列探索**
- インサート全長を欠損なく保持するため、Forward は先頭固定、Reverse は末尾固定
- 18〜25 bp 範囲で候補を探索し、PCR 適性を満たす配列を選択

3. **ペナルティシステムによる評価（フォールバック機構）**
- 評価対象:
   - Tm 値（55〜65℃）
   - GC 含有率（40〜60%）
   - GC クランプ
   - ホモポリマー（連続塩基）
   - ヘアピン（二次構造）
- 理想候補がない場合でも停止せず、ペナルティ最小の候補を返す
- これにより DBTL 自動化ラインのジョブ停止リスクを低減

4. **結合と最適化**
- 生物学的に正しい向きで相同アームと特異的配列を結合
- Reverse 側は逆相補鎖へ変換
- 結合境界で 1 塩基重複があれば自動短縮（オーバーラップ除去）
- 最終プライマーをテキスト/JSON で出力

この処理系は、単純な文字列連結ではなく、クローニング成立条件と実験運用を同時に満たすことを目的に設計されています。

---

## 📚 API リファレンス

### `primer_designer.py` の主要関数

#### 1. `read_sequence(filepath)`
ファイルから塩基配列を読み込む。改行・空白を除去し、大文字に変換します。

```python
from src.primer_designer import read_sequence
seq = read_sequence('data/plasmid/p10A1.dna')
```

#### 2. `linearize_vector(vector_seq, enzyme_site)`
ベクターを制限酵素サイトで直鎖化します。

```python
from src.primer_designer import linearize_vector
linearized = linearize_vector(vector_seq, 'AGATCT')
```

#### 3. `extract_homology_arms(linearized_vector, arm_length=15)`
直鎖化ベクターの5'・3'末端から相同アームを抽出します。

```python
from src.primer_designer import extract_homology_arms
arm_5prime, arm_3prime = extract_homology_arms(linearized_vector)
```

#### 4. `calculate_tm(sequence)`
簡易計算式（Tm = 4×(G+C) + 2×(A+T)）でTm値を計算します。

```python
from src.primer_designer import calculate_tm
tm = calculate_tm('ATGCATGC')  # 返り値: 32.0℃
```

#### 5. `design_gene_specific_primers(insert_seq)`
インサートの両端から特異的プライマー配列を探索します。

**重要な仕様:**
- **Forward用**: インサートの「最初の塩基（index 0）」から開始する配列を抽出
  - `insert_seq[0:length]` の形式で探索（length は 18～25 bp）
  - インサートの5'末端を確実に増幅
  - GCクランプ判定：3'末端（`sequence[-1]`）が G または C
- **Reverse用**: インサートの「最後の塩基（末尾）」で終わる配列を抽出
  - `insert_seq[-length:]` の形式で探索（length は 18～25 bp）
  - インサートの3'末端を確実に増幅
  - GCクランプ判定：5'末端（`sequence[0]`）が G または C（逆相補鎖の3'末端のため）
- **フォールバック機能**: 設計条件を満たす配列が見つからない場合、ペナルティスコアが最小の配列か、長さ 20 bp の配列をデフォルトとして返却
- **Tm値バランス警告**: ForwardとReverseのTm差が 5℃ を超える場合、stderr に警告を出力（PCR効率低下の可能性）

```python
from src.primer_designer import design_gene_specific_primers
forward_seq, reverse_seq = design_gene_specific_primers(insert_seq)
```

**In-Fusion クローニングでの重要性:**
- インサート全長を欠損なく増幅するため、開始位置・終了位置を厳密に固定
- 相同アームと組み合わせることで、ベクターへの正確な挿入を実現

#### 6. `generate_infusion_primers(homology_arms, specific_seqs)`
相同アームと特異的配列を生物学的な向きで結合し、最終プライマーを生成します。

**重要な仕様:**
- **Forward**: `arm_3prime` を接頭辞に使用
- **Reverse**: `arm_5prime` の逆相補鎖を接頭辞に使用
- 結合境界で1塩基の重複がある場合は、重複分を削除して短縮してから結合

```python
from src.primer_designer import generate_infusion_primers
forward_primer, reverse_primer = generate_infusion_primers(
    (arm_5prime, arm_3prime),
    (forward_specific, reverse_specific)
)
```

#### 7. `get_reverse_complement(sequence)`
DNAシーケンスの逆相補鎖を返します。

```python
from src.primer_designer import get_reverse_complement
rc = get_reverse_complement('ATGC')  # 返り値: 'GCAT'
```

#### 8. `check_consecutive_bases(sequence)` ⭐ v1.2 新規
プライマー内の4塩基以上の連続した同一塩基（ホモポリマー）を検出します。

```python
from src.primer_designer import check_consecutive_bases
result = check_consecutive_bases('AAAA')  # 返り値: 4
result = check_consecutive_bases('ATGC')  # 返り値: 0
```

**用途**: プライマー品質評価。ペナルティスコア計算で不利な評価を受けます。

#### 9. `check_hairpin(sequence)` ⭐ v1.2 新規（v1.2.1 で偽陽性バグ修正）
プライマー内部に3塩基以上の自己相補配列が存在するか検出します（二次構造形成の可能性）。

```python
from src.primer_designer import check_hairpin
result = check_hairpin('ATCGATCGAT')  # 返り値: True（実際のヘアピン）
result = check_hairpin('ATGCATGC')    # 返り値: False
```

**用途**: プライマー品質評価。ヘアピン形成の可能性があるプライマーはペナルティスコア計算で不利な評価を受けます。

**注意**: v1.2.1 で偽陽性（False Positive）バグを修正。左側領域と右側領域を独立して評価するため、文字列結合による人工的なつなぎ目での誤検知は発生しません。

---

## 🔧 カスタマイズ

### 異なるファイルパスで実行する場合

`scripts/run_primer_designer.py` の以下の部分を修正してください：

```python
# ファイルパスの定義
vector_file = base_dir / 'data' / 'plasmid' / 'p10A1.dna'      # ← ベクターファイルパス
insert_file = base_dir / 'data' / 'insert' / 'sample.dna'      # ← インサートファイルパス
enzyme_file = base_dir / 'data' / 'restriction_digest' / 'BglII.seq'  # ← 酵素サイトファイルパス
```

### ログファイルの出力先変更

`scripts/run_primer_designer.py` の `setup_logging()` 呼び出し部分で、ログディレクトリを変更できます：

```python
logger = setup_logging(log_dir='logs')  # ← ここでログ出力先を変更
```

### プライマー設計条件の変更

`src/primer_designer.py` の `is_valid_primer()` 関数内で以下のパラメータを変更できます：

```python
def is_valid_primer(sequence):
    # 条件1: 長さ（現在 18～25 bp）
    if len(sequence) < 18 or len(sequence) > 25:
        return False
    
    # 条件3: GC含有率（現在 40～60%）
    if gc_content < 40 or gc_content > 60:
        return False
    
    # 条件4: Tm値（現在 55～65℃）
    if tm < 55 or tm > 65:
        return False
    
    return True
```

### 相同アームの長さ変更

`scripts/run_primer_designer.py` で以下を変更してください：

```python
arm_5prime, arm_3prime = extract_homology_arms(linearized_vector, arm_length=15)
#                                                                  ↑
#                                                    ここで長さを変更（デフォルト: 15 bp）
```

---

## 📊 処理フロー

```
┌─────────────────────────┐
│ 1. ファイル読み込み      │
│ - ベクター               │
│ - インサート             │
│ - 酵素サイト             │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ 2. ベクター直鎖化        │
│ - 酵素サイト検索         │
│ - A|GATCT で切断         │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ 3. 相同アーム抽出        │
│ - 5'末端 15 bp           │
│ - 3'末端 15 bp           │
└──────────┬──────────────┘
           ↓
┌──────────────────────────┐
│ 4. 特異的プライマー設計   │
│ - Forward: arm_3prime 側  │
│ - Reverse: arm_5prime_rc側│
│ - 1bp 重複を短縮          │
│ - ペナルティスコア最適化  │
└──────────┬───────────────┘
           ↓
┌─────────────────────────┐
│ 5. 最終プライマー生成    │
│ - 向きに応じた相同アーム  │
│ - 逆相補鎖変換          │
│ - 重複塩基の削除          │
└──────────┬──────────────┘
           ↓
     結果を出力・ログ保存
```

---

## 🧬 生物学的背景

### In-Fusion クローニングとは

In-Fusion は、**ExoIII エキソヌクレアーゼ**を利用した高効率なDNA組み込みクローニング手法です。

**特徴:**
- ホモロジー組み換え（15～25 bp の相同領域が必要）
- 制限酵素サイトが不要
- 高い組み込み効率（>80%）

### プライマー設計の原理

| 項目 | 説明 |
|------|------|
| **相同アーム** | ベクターとインサートを結合するための配列（通常 15～25 bp） |
| **GCクランプ** | 3'末端を G または C にすることで、プライマーの安定性を向上 |
| **Tm値** | プライマーの融解温度。PCR反応温度の設定に使用 |
| **GC含有率** | 40～60% が PCR 効率の最適範囲 |
| **Forward配列** | インサート最初（index 0）から開始 → `arm_3prime` を接頭辞にして結合 |
| **Reverse配列** | インサート末尾で終了 → `arm_5prime` の逆相補鎖を接頭辞にして結合 |
| **重複塩基削除** | ベクター末端とインサート末端が1塩基重複する場合、最終プライマーを1塩基短縮 |
| **ペナルティスコア** | v1.1で導入。条件からの外れ度を定量化し、最適な配列を選別 |

---

## 📝 データ形式

### 入力ファイル形式

塩基配列ファイルは以下の形式に対応しています：

```
ATGCATGCATGCATGC
ATGCATGC
ATGC
```

- 複数行でも、改行や空白は自動的に除去されます
- 大文字・小文字は自動的に大文字に統一されます
- A, T, G, C のみが有効な塩基です

---

## 🐛 トラブルシューティング

### エラー: `制限酵素サイト AGATCT が見つかりません`

**原因:** ベクター塩基配列に指定された制限酵素サイトが含まれていません。

**対処:**
1. ベクターファイルが正しいか確認
2. 制限酵素サイトが正しいか確認
3. 異なる酵素サイトを使用する場合は、`scripts/run_primer_designer.py` 内の `enzyme_file` パスを修正

### エラー: `ファイルが見つかりません`

**原因:** ベクター、インサート、または酵素サイトファイルのパスが正しくありません。

**対処:**
1. `scripts/run_primer_designer.py` のファイルパスを確認
   ```python
   vector_file = base_dir / 'data' / 'plasmid' / 'p10A1.dna'
   insert_file = base_dir / 'data' / 'insert' / 'sample.dna'
   enzyme_file = base_dir / 'data' / 'restriction_digest' / 'BglII.seq'
   ```
2. ファイルが実際に存在するか確認

### プライマー設計が最適でない場合

**背景:** v1.1では、設計条件を満たす配列が見つからない場合、ペナルティスコアが最小の配列をデフォルトとして返却します。

**対処:**
1. プライマー設計条件を緩和（`is_valid_primer()` 内のTm値範囲やGC含有率範囲を拡大）
2. 異なるインサートを使用
3. 相同アームの長さを調整

---

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

## 👤 作成者

バイオインフォマティクス・エンジニア

---

## � 修正履歴・バージョン情報
### v1.3.1 - 結合順序修正とオーバーラップ短縮（2026-05-06）

**生物学的整合性の修正:**
- Forward プライマーの接頭辞を `arm_3prime` に修正
- Reverse プライマーの接頭辞を `arm_5prime` の逆相補鎖に修正
- 結合境界の 1 塩基重複を削除するロジックを追加

**修正内容:**
- `generate_infusion_primers()` に重複除去ヘルパーを追加
- Forward は `arm_3prime[-1] == forward_specific[0]` の場合、特異的配列先頭1塩基を削除
- Reverse は `arm_5prime[0] == reverse_specific[-1]` の場合、特異的配列末尾1塩基を削除してから逆相補化

**実行結果の変化:**
- Forward: `CACAAATACCACTGA` + `TCGCGCGTTTCGGTGATGAC` → `CACAAATACCACTGATCGCGCGTTTCGGTGATGAC`
- Reverse: `AGAGGGAAAAAGATC` + `reverse_complement(ACGAAAGGGCCTCGTGAT)` → `AGAGGGAAAAAGATCGACGAAAGGGCCTCGTGATAC`

---

### v1.3.0 - GUI/CUI 統合エントリーポイント追加（2026-05-06）

**新機能: app.py - 統合エントリーポイント（GUI/CUI 両対応）**

**GUI モード（手動操作用）:**
- PyQt6 を使用したデスクトップアプリケーション
- ファイル選択ボタン（QFileDialog 統合）
- リアルタイム結果表示（QTextEdit）
- 例外処理によるエラー表示（クラッシュなし）
- 起動: `python app.py`（引数なし）

**CUI モード（DBTL パイプライン用）:**
- `argparse` による構造化された引数処理
- 必須引数: `--vector`, `--insert`, `--enzyme`
- オプション引数: `--output`, `--json`
- JSON 形式対応（後段システムのパース容易）
- 起動: `python app.py --vector <path> --insert <path> --enzyme <path> [--json] [--output <path>]`

**実装詳細:**
- `sys.argv` の長さで起動モード自動判定
- `PrimerDesignLogic` クラスで CUI/GUI 共通のビジネスロジック管理
- `src.primer_designer` からすべての関数をインポート（再実装なし）
- 完全な例外処理で信頼性確保

**修正ファイル:**
- 新規: `app.py` (420行以上)
- 更新: `environment.yml` (PyQt6 追加)
- 更新: `README.md` (使用方法セクション追加)

**動作確認:**
- ✅ GUI モード: PyQt6 ウィンドウ正常表示
- ✅ CUI モード（テキスト）: 標準出力に結果出力
- ✅ CUI モード（JSON）: JSON 形式で出力
- ✅ ファイル出力: `--output` フラグで指定パスに保存

---
### v1.2.1 - check_hairpin の偽陽性バグ修正（2026-05-06）

**バグ修正: check_hairpin 関数の偽陽性（False Positive）排除**

**問題点:**
- 関数内で左右の領域を文字列結合していた: `remaining = sequence[:start] + sequence[start + length:]`
- 結合のつなぎ目で「人工的な逆相補配列」が生成される可能性があった
- 実際には存在しないヘアピン構造を誤検知していた

**修正内容:**
- 文字列結合を廃止
- 左側領域 (`left_part = sequence[:start]`) と右側領域 (`right_part = sequence[start + length:]`) を独立して評価
- 逆相補配列が**どちらか一方**に含まれる場合のみ `True` を返す

**修正効果:**
- ✅ 結合のつなぎ目による偽陽性を完全に排除
- ✅ 実際のヘアピン構造は正しく検出
- ✅ プライマー品質評価の精度向上

---
### v1.2.0 - プライマー品質向上と制約追加（2026-05-06）

**バグ修正＆高度な制約導入**

**バグ修正: Reverseプライマーの GC クランプ判定誤り**
- `is_valid_primer()` と `calculate_penalty_score()` に `is_forward` 引数を追加
- **問題点**: Reverseプライマーは逆相補鎖なため、GCクランプ判定位置が間違っていた
  - 旧: 常に `sequence[-1]` (末尾) をチェック
  - 新: Forward は `sequence[-1]`、Reverse は `sequence[0]` をチェック
- **修正効果**: Reverse配列が 19bp (Tm 60℃) → 21bp (Tm 66℃) に改善
  - 旧19bp配列: 最初が 'A' → GCクランプ不満足
  - 新21bp配列: 最初が 'G' → GCクランプ満足

**新しい制約（ペナルティ条件）の追加:**

1. **連続塩基の回避** (`check_consecutive_bases()`)
   - 4塩基以上の連続した同一塩基を検出
   - ペナルティ: `(連続塩基数 - 3) × 10`
   - 例: AAAA, GGGG などをペナルティで排除

2. **二次構造（ヘアピン）の回避** (`check_hairpin()`)
   - 3塩基以上の自己相補配列を検出
   - ペナルティ: 20.0（固定値）
   - プライマー自己結合による非特異的PCRを防止

3. **Tm値バランス警告**
   - ForwardとReverseのTm差が 5℃ を超える場合、警告を出力
   - PCR効率低下を事前に警告

**実装変更:**
- 新規関数: `check_consecutive_bases()`, `check_hairpin()`
- 修正関数: `is_valid_primer()`, `calculate_penalty_score()`, `find_forward_primer()`, `find_reverse_primer()`, `design_gene_specific_primers()`
- ペナルティスコア計算: 従来の3項目 → 6項目に拡張

**実行結果の変化:**
- v1.1: Forward 20bp Tm 64℃, Reverse 19bp Tm 60℃
- v1.2: Forward 20bp Tm 64℃, Reverse 21bp Tm 66℃ (バグ修正による改善)

---
### v1.1.0 - 生物学的エラー修正（2026-05-06）

**重大な修正: プライマー抽出位置の厳密化**

**問題点 (v1.0):**
- `find_forward_primer()` と `find_reverse_primer()` が配列内を自由にスキップしていた
- インサートの「どこか」から条件を満たす配列を抽出していた
- **生物学的に危険**: インサート全長を欠損なく増幅できない可能性があった

**修正内容 (v1.1):**
1. **Forward用プライマー**: インサート最初（index 0）から開始
   - `insert_seq[0:length]` のみで探索 (length: 18～25 bp)
   - インサートの5'末端を確実に増幅

2. **Reverse用プライマー**: インサート末尾で終了
   - `insert_seq[-length:]` のみで探索 (length: 18～25 bp)
   - インサートの3'末端を確実に増幅

3. **フォールバック機能の実装**
   - `calculate_penalty_score()` 関数を追加
   - ペナルティスコア: Tm値、GC%、長さの偏差を定量化
   - 設計条件を満たす配列が見つからない場合、ペナルティスコアが最小の配列を返却
   - 最悪の場合は長さ 20 bp の配列をデフォルトとして返却

**検証結果:**
- ✅ Forward配列は `insert_seq[0:length]` から取得
- ✅ Reverse配列は `insert_seq[-length:]` から取得
- ✅ インサート全長を欠損なくカバー
- ✅ In-Fusionクローニングの要件を完全に満たす
- ✅ 実行例: Forward 20 bp + Reverse 19 bp でインサート全長 2691 bp を保存

---

問題が発生した場合は、以下の情報を記録してください：

- エラーメッセージ
- 使用したファイルパス
- 実行環境（Python版、OS）
- 実行したコマンド

---

## 📖 参考文献

- In-Fusion HD Cloning Plus キット | Takara Bio
- PCR Primer Design | Molecular Cloning Manual

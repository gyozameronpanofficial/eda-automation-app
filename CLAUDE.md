# EDA自動化アプリ - Claude開発ドキュメント

## 📋 プロジェクト概要

### 🎯 目的
データサイエンスチーム向けの探索的データ分析（EDA）自動化ツール。CSVやExcelファイルをアップロードするだけで、包括的なデータ分析を自動実行し、インタラクティブな結果を提供する。

### 🏗️ アーキテクチャ
- **フレームワーク**: Streamlit (Webアプリ)
- **言語**: Python 3.8+
- **環境**: Python venv (仮想環境)
- **対応OS**: Windows 11, macOS 10.15+, Ubuntu 20.04+

### 🎨 設計思想
- **探索的分析**: データを見ながら段階的に分析
- **ユーザーフレンドリー**: 技術的知識がなくても使用可能
- **モジュラー設計**: 機能ごとの独立したコンポーネント
- **拡張性**: 新機能の追加が容易
- **セキュア**: ローカル動作でデータ外部送信なし

## 🚀 機能一覧

### ✅ 実装済み機能

#### 📊 基本統計分析
- **データ概要**: 行数、列数、メモリ使用量
- **データ型分析**: 数値列、カテゴリ列、日時列の自動分類
- **欠損値分析**: 欠損数、欠損率、欠損パターンの詳細分析
- **重複値分析**: 重複行の検出と統計

#### 📈 分布分析
- **数値列分析**: 
  - ヒストグラム、箱ひげ図、Q-Qプロット、密度プロット
  - 基本統計量（平均、中央値、標準偏差、歪度、尖度）
  - 外れ値検出（IQR法、Z-score法、修正Z-score法）
- **カテゴリ列分析**:
  - 棒グラフ、円グラフ、頻度統計
  - ユニーク値数、最頻値分析
- **インタラクティブプロット**: Plotlyによる動的可視化

#### 🔗 相関分析
- **相関係数**: Pearson、Spearman、Kendall
- **相関ヒートマップ**: 完全なn×n相関行列表示
- **強い相関の自動検出**: 閾値ベースの相関関係抽出
- **散布図マトリックス**: 回帰線付き散布図
- **統計的有意性**: p値による有意性検定

#### ⏰ 時系列分析
- **日付列自動検出**: カラム名とデータ内容による判定
- **日付列選択**: ユーザーによるプルダウン選択
- **基本分析**: トレンド方向、傾き、決定係数
- **移動平均**: 7日、14日、30日、60日、90日
- **予測機能**: 線形・多項式回帰による将来予測（実際値と予測値の色分け）
- **周期性分析**: 月別、曜日別、年別統計

#### 🔧 前処理機能
- **探索的前処理**: ユーザーが順序を自由に選択
- **欠損値処理**: 削除、平均値・中央値・最頻値補完、前方・後方補完、カスタム値
- **外れ値除去**: IQR法、Z-score法、修正Z-score法
- **データ型変換**: int64, float64, object, datetime64, category, bool
- **重複行除去**: 最初/最後の行保持選択
- **プレビュー機能**: 処理前後の比較表示
- **処理履歴**: 全操作の詳細ログと復元機能

### 📁 ファイル対応
- **CSV**: カンマ、タブ、セミコロン区切り
- **Excel**: .xlsx, .xls形式
- **文字エンコーディング**: 自動判定（UTF-8, Shift-JIS, CP932等）
- **最大ファイルサイズ**: 3GB（設定変更可能）

## 🏗️ アーキテクチャ詳細

### 📂 ディレクトリ構成
```
eda-automation-app/
├── README.md                    # ユーザー向けドキュメント
├── CLAUDE.md                   # Claude開発ドキュメント
├── requirements.txt            # Python依存関係
├── setup.bat / setup.sh        # セットアップスクリプト
├── run.bat / run.sh            # 起動スクリプト
├── .gitignore                  # Git除外設定
├── config/
│   └── settings.yaml          # アプリ設定（自動生成）
├── venv/                       # Python仮想環境（自動生成）
└── app/
    ├── main.py                 # メインページ
    ├── components/             # ビジネスロジック
    │   ├── __init__.py
    │   ├── file_handler.py     # ファイル処理
    │   ├── basic_stats.py      # 基本統計
    │   ├── visualization.py    # 分布分析・可視化
    │   ├── correlation.py      # 相関分析
    │   ├── timeseries.py       # 時系列分析
    │   └── preprocessor.py     # 前処理
    ├── pages/                  # Streamlit UI
    │   ├── 01_basic_stats.py   # 基本統計ページ
    │   ├── 02_distribution.py  # 分布分析ページ
    │   ├── 03_correlation.py   # 相関分析ページ
    │   ├── 04_timeseries.py    # 時系列分析ページ
    │   └── 05_preprocessing.py # 前処理ページ
    └── utils/                  # ユーティリティ
        ├── __init__.py
        ├── config_loader.py    # 設定管理
        └── session_state.py    # セッション管理
```

### 🔄 データフロー
```
1. ファイルアップロード (main.py)
    ↓
2. ファイル読み込み・データ型判定 (file_handler.py)
    ↓
3. セッション状態保存 (session_state.py)
    ↓
4. 各分析コンポーネント実行
   - basic_stats.py
   - visualization.py
   - correlation.py
   - timeseries.py
   - preprocessor.py
    ↓
5. 結果表示・インタラクション (pages/*.py)
```

### 🧩 コンポーネント設計

#### FileHandler
- **責務**: ファイル読み込み、エンコーディング判定、データ型自動変換
- **特徴**: 多様なファイル形式に対応、堅牢なエラーハンドリング

#### BasicStats
- **責務**: 基本統計量計算、欠損値・重複値分析
- **特徴**: 数値・カテゴリ両対応、包括的な統計情報

#### Visualization
- **責務**: 分布分析、可視化、外れ値検出
- **特徴**: 静的・インタラクティブ両対応、多彩なプロット

#### Correlation
- **責務**: 相関分析、ヒートマップ、散布図マトリックス
- **特徴**: 複数の相関係数、統計的有意性検定

#### TimeSeries
- **責務**: 時系列分析、トレンド検出、予測
- **特徴**: 自動頻度推定、機械学習予測、周期性分析

#### Preprocessor
- **責務**: データ前処理、履歴管理
- **特徴**: 探索的ワークフロー、プレビュー機能、復元機能

### 🛠️ 技術スタック

#### 主要ライブラリ
- **Streamlit** (1.28.0+): Webアプリフレームワーク
- **pandas** (2.0.0+): データ操作・分析
- **numpy** (1.24.0+): 数値計算
- **matplotlib** (3.7.0+): 静的可視化
- **seaborn** (0.12.0+): 統計的可視化
- **plotly** (5.15.0+): インタラクティブ可視化
- **scipy** (1.10.0+): 科学計算
- **scikit-learn** (1.3.0+): 機械学習（予測機能）

#### 日本語対応
- **japanize-matplotlib** (1.1.3+): 日本語フォント自動設定
- **フォント自動検出**: システム環境に応じた最適フォント選択

#### ファイル処理
- **openpyxl** (3.1.0+): Excel読み書き
- **xlrd** (2.0.1+): 旧Excel形式対応
- **chardet** (5.1.0+): 文字エンコーディング自動検出

#### 設定管理
- **PyYAML** (6.0+): YAML設定ファイル処理

## ⚙️ 設定システム

### 📄 settings.yaml構成
```yaml
general:
  max_file_size_mb: 3000        # 最大ファイルサイズ
  max_memory_usage_gb: 16       # 最大メモリ使用量
  timeout_seconds: 120          # 処理タイムアウト

analysis:
  basic_stats: true             # 各分析機能のON/OFF
  distribution: true
  correlation: true
  timeseries: true
  preprocessing: true

visualization:
  figure_size:
    width: 10
    height: 6
  dpi: 100
  style: "whitegrid"
  color_palette: "husl"
  max_categories: 20

correlation:
  method: "pearson"
  threshold: 0.5
  show_heatmap: true
  show_scatter_matrix: true

preprocessing:
  missing_value_methods: [...]
  outlier_methods: [...]
```

### 🔧 カスタマイズ方法
1. `config/settings.yaml`を編集
2. アプリを再起動
3. 新しい設定が反映

## 🔒 セキュリティ設計

### 🛡️ データ保護
- **ローカル処理**: データは外部送信されない
- **メモリ上処理**: 一時ファイル作成なし
- **セッション終了時削除**: ブラウザ終了でデータ消去
- **仮想環境分離**: 本体Python環境への影響なし

### 🚫 除外設定 (.gitignore)
```
venv/                           # 仮想環境
config/settings.yaml            # 個人設定
*.csv, *.xlsx                   # アップロードファイル
__pycache__/                    # Pythonキャッシュ
.streamlit/                     # Streamlit設定
```

## 🧪 開発・拡張ガイド

### 🔧 開発環境セットアップ
```bash
# リポジトリクローン
git clone [リポジトリURL]
cd eda-automation-app

# 仮想環境構築
./setup.sh  # macOS/Linux
setup.bat   # Windows

# 開発モード起動
./run.sh    # macOS/Linux
run.bat     # Windows
```

### 📝 新機能追加手順

#### 1. 新しい分析コンポーネント追加
```python
# app/components/new_analysis.py
class NewAnalysis:
    def __init__(self, config):
        self.config = config
    
    def analyze(self, df):
        # 分析ロジック
        pass
```

#### 2. 新しいページ追加
```python
# app/pages/06_new_analysis.py
from components.new_analysis import NewAnalysis

# Streamlitページ実装
```

#### 3. 設定追加
```yaml
# config/settings.yaml
analysis:
  new_analysis: true
```

#### 4. 初期化ファイル更新
```python
# app/components/__init__.py
from .new_analysis import NewAnalysis
__all__ = [..., 'NewAnalysis']
```

### 🎨 UI設計ガイドライン

#### レイアウトパターン
- **3カラム**: 設定 | メイン表示 | サイドバー
- **タブ**: 関連機能のグループ化
- **エクスパンダー**: 詳細情報の折りたたみ
- **メトリクス**: 重要指標の強調表示

#### インタラクション設計
- **プレビュー**: 実行前の結果確認
- **プログレスバー**: 長時間処理の進捗表示
- **エラーメッセージ**: 分かりやすい問題説明
- **ヘルプテキスト**: 機能説明の提供

### 🔍 テスト戦略

#### 手動テスト項目
- [ ] 各ファイル形式での読み込み (CSV, Excel)
- [ ] 文字エンコーディング対応 (UTF-8, Shift-JIS)
- [ ] 大容量ファイル処理 (1GB+)
- [ ] 欠損値・外れ値を含むデータ
- [ ] 日本語列名・データ
- [ ] 各分析機能の動作確認
- [ ] 前処理機能の組み合わせテスト
- [ ] エラー処理の確認

#### パフォーマンステスト
- メモリ使用量監視
- 処理時間測定
- 大容量データでの動作確認

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. 文字化け問題
**現象**: グラフタイトルが「□□□」で表示
**原因**: 日本語フォント未設定
**解決**: japanize-matplotlibの自動フォント選択

#### 2. メモリエラー
**現象**: 大容量ファイルでメモリ不足
**解決**: settings.yamlでmax_memory_usage_gb調整

#### 3. 日付列認識エラー
**現象**: 日付列が認識されない
**解決**: カラム名での判定とエラー閾値の調整

#### 4. インポートエラー
**現象**: モジュールが見つからない
**解決**: アプリ再起動、パス設定確認

### 🔧 デバッグ方法
```python
# デバッグモード有効化
import streamlit as st
st.set_option('logger.level', 'debug')

# セッション状態確認
st.write(st.session_state)

# エラー詳細表示
import traceback
st.error(traceback.format_exc())
```

## 🚀 今後の拡張予定

### Phase 1: 基盤強化
- [ ] **PDFレポート生成**: 全分析結果の統合レポート
- [ ] **設定UI**: ブラウザ上での設定変更機能
- [ ] **バッチ処理**: 複数ファイルの一括処理

### Phase 2: 高度な分析
- [ ] **統計的検定**: t検定、カイ二乗検定、ANOVA
- [ ] **機械学習統合**: クラスタリング、特徴量重要度
- [ ] **多変量解析**: PCA、因子分析

### Phase 3: 連携・運用
- [ ] **データベース接続**: SQL Server、PostgreSQL
- [ ] **API連携**: 外部データソース
- [ ] **スケジュール実行**: 定期分析の自動化

### Phase 4: エンタープライズ
- [ ] **ユーザー管理**: 認証・権限制御
- [ ] **監査ログ**: 操作履歴の詳細記録
- [ ] **パフォーマンス監視**: 使用統計の収集

## 📊 プロジェクト統計

### 開発規模
- **総ファイル数**: ~20ファイル
- **総コード行数**: ~3,000行
- **コンポーネント数**: 6個
- **ページ数**: 5ページ
- **対応分析種類**: 4種類

### 機能カバレッジ
- **ファイル読み込み**: 100% (CSV, Excel)
- **基本分析**: 100% (統計、分布、相関)
- **高度分析**: 70% (時系列、前処理)
- **可視化**: 90% (静的、インタラクティブ)
- **UI/UX**: 95% (レスポンシブ、直感的)

## 👥 開発チーム

### 開発者
- **アーキテクト**: Claude (Anthropic)
- **プロダクトオーナー**: データサイエンスチーム

### 貢献方法
1. **Issue作成**: バグ報告・機能要望
2. **コード改善**: プルリクエスト
3. **ドキュメント更新**: 使用方法の改善
4. **テスト**: 新機能の動作確認

## 📄 ライセンス・利用規約

### 使用範囲
- **社内利用のみ**: 外部配布禁止
- **データ保護**: 機密データの適切な取り扱い
- **責任範囲**: 使用結果に対する自己責任

### 更新・保守
- **定期レビュー**: 月1回の機能改善
- **セキュリティ更新**: 随時対応
- **機能拡張**: 要望ベースでの開発

---

**EDA自動化アプリ v2.0**  
*Last Updated: 2024年12月*  
*Developed with Claude (Anthropic)*
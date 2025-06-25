# EDA自動化アプリ

データサイエンスチーム向けの探索的データ分析（EDA）自動化ツールです。CSVやExcelファイルをアップロードするだけで、包括的なデータ分析レポートを自動生成します。

## 🚀 主な機能

- **基本統計**: データ概要、基本統計量、欠損値・重複値チェック
- **分布分析**: ヒストグラム、箱ひげ図、外れ値検出
- **相関分析**: 相関行列、散布図マトリックス、ヒートマップ
- **時系列分析**: 時系列プロット、トレンド分析
- **前処理機能**: 欠損値処理、外れ値除去、データ型変換
- **レポート生成**: PDF形式での包括的な分析レポート

## 📋 システム要件

### 共通要件
- Python 3.8以上
- メモリ: 32GB推奨
- 空きディスク容量: 3GB以上

### 対応OS
- **Windows**: 10/11
- **macOS**: 10.15 (Catalina) 以上
- **Linux**: Ubuntu 20.04+, CentOS 8+

## 🔧 セットアップ手順

### 🪟 Windows環境の場合

#### 1. Pythonのインストール（未インストールの場合）
1. [Python公式サイト](https://www.python.org/downloads/)から最新版をダウンロード
2. インストール時に「Add Python to PATH」にチェック
3. 確認: `python --version`

#### 2. セットアップ・起動
```cmd
# リポジトリをクローン
git clone [リポジトリURL]
cd eda-automation-app

# 初回セットアップ
setup.bat

# アプリ起動
run.bat
```

### 🍎 macOS環境の場合

#### 1. 前提条件のインストール
```bash
# Homebrewのインストール（未インストールの場合）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python3のインストール
brew install python3

# 確認
python3 --version
```

#### 2. セットアップ・起動
```bash
# リポジトリをクローン
git clone [リポジトリURL]
cd eda-automation-app

# 実行権限を付与
chmod +x setup.sh run.sh

# 初回セットアップ
./setup.sh

# アプリ起動
./run.sh
```

### 🐧 Linux環境の場合

#### 1. Python3のインストール
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip
```

#### 2. セットアップ・起動
```bash
# リポジトリをクローン
git clone [リポジトリURL]
cd eda-automation-app

# 実行権限を付与
chmod +x setup.sh run.sh

# 初回セットアップ
./setup.sh

# アプリ起動
./run.sh
```

## 🌐 アプリケーションへのアクセス

セットアップ完了後、ブラウザで以下にアクセス：
```
http://localhost:8501
```

## 📝 使い方

### 基本的な流れ
1. **データアップロード**: CSVまたはExcelファイルを選択（最大3GB）
2. **データ読み込み**: "データを読み込む"ボタンをクリック
3. **分析開始**: "分析を開始する"ボタンをクリック
4. **結果確認**: 左のサイドバーから各分析ページにアクセス

### 対応ファイル形式
- **CSV**: カンマ区切り、タブ区切り、セミコロン区切り
- **Excel**: .xlsx, .xls形式
- **文字エンコーディング**: 自動判定（UTF-8, Shift-JIS, CP932等）

### 分析機能
- **📊 基本統計**: データ形状、データ型、欠損値・重複値分析
- **📈 分布分析**: ヒストグラム、箱ひげ図、外れ値検出
- **🔗 相関分析**: 相関行列、ヒートマップ、散布図マトリックス
- **⏰ 時系列分析**: 時系列プロット、トレンド分析
- **🔧 前処理**: 欠損値処理、外れ値除去、データ型変換

## ⚙️ 設定のカスタマイズ

`config/settings.yaml` で各種設定を変更可能：

```yaml
general:
  max_file_size_mb: 3000      # 最大ファイルサイズ
  max_memory_usage_gb: 16     # 最大メモリ使用量
  timeout_seconds: 120        # 処理タイムアウト

analysis:
  basic_stats: true           # 各分析機能のON/OFF
  distribution: true
  correlation: true
  timeseries: true
  preprocessing: true
```

設定変更後は、アプリを再起動してください。

## 🛠️ トラブルシューティング

### よくある問題

#### Pythonが見つからない
**Windows**: `python --version` でエラー
→ Python 3.8以上をインストール、「Add Python to PATH」にチェック

**macOS**: `command not found: python3`
→ `brew install python3` を実行

#### ポート8501が使用中
```
Port 8501 is already in use
```
→ 他のStreamlitアプリを停止、またはポート番号を変更

#### 企業環境でアクセスブロック
```
Access to this site is blocked by the administrator
```
→ IT部門にローカルホストアクセス許可を依頼

#### メモリ不足
→ `config/settings.yaml` で `max_memory_usage_gb` を調整

#### 権限エラー（macOS/Linux）
→ `chmod +x setup.sh run.sh` で実行権限を付与

## 🔄 日常的な使用方法

### 起動
**Windows**: `run.bat`
**macOS/Linux**: `./run.sh`

### 停止
**共通**: ターミナルで `Ctrl+C`

### 再セットアップ
**Windows**: `setup.bat`
**macOS/Linux**: `./setup.sh`

## 🔒 セキュリティ

- アップロードデータはメモリ上でのみ処理
- ブラウザを閉じるとデータは自動削除
- ローカル環境でのみ動作（外部送信なし）
- 仮想環境で本体Python環境を保護

## 🆕 開発・カスタマイズ

### ファイル構成
```
eda-automation-app/
├── setup.bat / setup.sh      # セットアップスクリプト
├── run.bat / run.sh          # 起動スクリプト
├── requirements.txt          # Python依存関係
├── config/settings.yaml      # 設定ファイル
└── app/
    ├── main.py               # メインアプリ
    ├── components/           # 分析機能
    ├── pages/                # UIページ
    └── utils/                # ユーティリティ
```

### 新機能追加
1. `app/components/` に分析クラスを追加
2. `app/pages/` にUIページを追加
3. `config/settings.yaml` に設定項目を追加

## 📊 対応環境一覧

| OS | Python | セットアップ | 起動 | 状態 |
|---|---|---|---|---|
| Windows 10/11 | 3.8+ | `setup.bat` | `run.bat` | ✅ |
| macOS 10.15+ | 3.8+ | `./setup.sh` | `./run.sh` | ✅ |
| Ubuntu 20.04+ | 3.8+ | `./setup.sh` | `./run.sh` | ✅ |
| CentOS 8+ | 3.8+ | `./setup.sh` | `./run.sh` | ✅ |

## 📞 サポート

- **改修依頼・バグ報告**: GitHubのIssuesで管理
- **定期レビュー**: 月1回チーム内で実施
- **ログ確認**: ターミナル/コマンドプロンプトで確認

## 📄 ライセンス

特になし。

---

**EDA自動化アプリ v2.0 (クロスプラットフォーム対応版)**  
*データサイエンスチーム*

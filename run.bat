@echo off
echo ========================================
echo EDA自動化アプリ 起動スクリプト
echo ========================================
echo.

:: 仮想環境が存在するかチェック
if not exist "venv" (
    echo エラー: 仮想環境が見つかりません。
    echo 先に setup.bat を実行してください。
    pause
    exit /b 1
)

:: 仮想環境をアクティベート
echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

:: 設定ファイルのディレクトリを作成
if not exist "config" mkdir config

:: デフォルト設定ファイルが存在しない場合は作成
if not exist "config\settings.yaml" (
    echo デフォルト設定ファイルを作成中...
    (
        echo # EDA自動化アプリ設定ファイル
        echo.
        echo # 全般設定
        echo general:
        echo   max_file_size_mb: 3000  # 最大ファイルサイズ（MB）
        echo   max_memory_usage_gb: 16  # 最大メモリ使用量（GB）
        echo   timeout_seconds: 120     # 処理タイムアウト（秒）
        echo.
        echo # 分析機能の有効/無効
        echo analysis:
        echo   basic_stats: true       # 基本統計
        echo   distribution: true      # 分布分析
        echo   correlation: true       # 相関分析
        echo   timeseries: true        # 時系列分析
        echo   preprocessing: true     # 前処理機能
        echo.
        echo # データ型自動判定設定
        echo data_types:
        echo   auto_detect: true
        echo   datetime_formats:
        echo     - "%%Y-%%m-%%d"
        echo     - "%%Y/%%m/%%d"
        echo     - "%%Y-%%m-%%d %%H:%%M:%%S"
        echo     - "%%Y/%%m/%%d %%H:%%M:%%S"
        echo   categorical_threshold: 10  # カテゴリ変数判定の閾値
        echo.
        echo # 可視化設定
        echo visualization:
        echo   figure_size:
        echo     width: 10
        echo     height: 6
        echo   dpi: 100
        echo   style: "whitegrid"      # seabornスタイル
        echo   color_palette: "husl"   # カラーパレット
        echo   max_categories: 20      # カテゴリ変数の最大表示数
        echo.
        echo # 相関分析設定
        echo correlation:
        echo   method: "pearson"       # pearson, spearman, kendall
        echo   threshold: 0.5          # 強い相関の閾値
        echo   show_heatmap: true
        echo   show_scatter_matrix: true
        echo.
        echo # 前処理設定
        echo preprocessing:
        echo   missing_value_methods:
        echo     - "削除"
        echo     - "平均値補完"
        echo     - "中央値補完"
        echo     - "最頻値補完"
        echo     - "前方補完"
        echo     - "後方補完"
        echo   outlier_methods:
        echo     - "IQR法"
        echo     - "Z-score法"
        echo     - "修正Z-score法"
        echo.
        echo # レポート設定
        echo report:
        echo   include_all_analysis: true
        echo   format: "PDF"           # PDF, HTML
        echo   template: "default"
    ) > config\settings.yaml
)

echo.
echo アプリケーションを起動中...
echo ブラウザで以下のURLにアクセスしてください:
echo.
echo    http://localhost:8501
echo.
echo 停止するには Ctrl+C を押してください。
echo.

:: Streamlitアプリを起動
streamlit run app\main.py --server.port=8501 --server.address=0.0.0.0
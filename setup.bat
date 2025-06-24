@echo off
echo ========================================
echo EDA自動化アプリ セットアップスクリプト
echo ========================================
echo.

:: Pythonがインストールされているかチェック
echo Pythonの状態をチェック中...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: Pythonがインストールされていません。
    echo Python 3.8以上をインストールしてから再実行してください。
    echo ダウンロード: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Pythonが正常にインストールされています。
python --version
echo.

:: 仮想環境が既に存在する場合は削除
if exist "venv" (
    echo 既存の仮想環境を削除中...
    rmdir /s /q venv
)

:: 仮想環境を作成
echo 仮想環境を作成中...
python -m venv venv
if %errorlevel% neq 0 (
    echo エラー: 仮想環境の作成に失敗しました。
    pause
    exit /b 1
)

:: 仮想環境をアクティベート
echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

:: pipをアップグレード
echo pipをアップグレード中...
python -m pip install --upgrade pip

:: 依存関係をインストール
echo 依存関係をインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo エラー: 依存関係のインストールに失敗しました。
    pause
    exit /b 1
)

echo.
echo ========================================
echo セットアップ完了！
echo ========================================
echo.
echo 仮想環境が作成され、依存関係がインストールされました。
echo.
echo アプリケーションを起動するには:
echo    run.bat を実行してください
echo.
echo アプリケーションを停止するには:
echo    Ctrl+C を押してください
echo.
pause
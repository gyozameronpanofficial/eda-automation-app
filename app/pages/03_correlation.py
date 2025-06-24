import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.correlation import Correlation
from utils.config_loader import ConfigLoader
from utils.session_state import SessionStateManager

# ページ設定
st.set_page_config(
    page_title="相関分析 - EDA自動化アプリ",
    page_icon="🔗",
    layout="wide"
)

# 設定とセッション状態の確認
config = ConfigLoader.load_config()

if not SessionStateManager.has_data():
    st.error("❌ データが読み込まれていません。メインページでデータをアップロードしてください。")
    st.stop()

if not SessionStateManager.has_analysis_started():
    st.warning("⚠️ 分析が開始されていません。メインページで「分析を開始する」ボタンをクリックしてください。")
    st.stop()

# 相関分析が無効の場合
if not config['analysis']['correlation']:
    st.info("ℹ️ 相関分析は設定で無効になっています。")
    st.stop()

# データ取得
df = st.session_state.df
file_name = st.session_state.file_name

# タイトル
st.title("🔗 相関分析")
st.markdown(f"**ファイル名:** {file_name}")
st.markdown("---")

# 数値列をチェック
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if len(numeric_cols) < 2:
    st.warning("⚠️ 相関分析には少なくとも2つの数値列が必要です。")
    
    if len(numeric_cols) == 1:
        st.info(f"数値列: {numeric_cols[0]} (1列のみ)")
    elif len(numeric_cols) == 0:
        st.info("数値列が見つかりませんでした。")
    
    st.markdown("### 💡 対処方法")
    st.markdown("""
    - 前処理ページでデータ型を数値型に変換
    - より多くの数値列を含むデータセットを使用
    """)
    st.stop()

# 相関分析オブジェクト作成
correlation = Correlation(config)

try:
    # 相関分析を実行・表示
    correlation.display_correlation_analysis(df)
    
    # 分析結果の保存
    correlation_results = correlation.calculate_correlation_matrix(df)
    if 'error' not in correlation_results:
        SessionStateManager.save_analysis_result('correlation', correlation_results)

except Exception as e:
    st.error(f"❌ 相関分析中にエラーが発生しました: {str(e)}")
    st.write("**エラー詳細:**")
    st.code(str(e))
    
    # デバッグ情報
    with st.expander("🔍 デバッグ情報"):
        st.write("**数値列一覧:**")
        st.write(numeric_cols)
        st.write("**データ形状:**")
        st.write(df.shape)
        st.write("**欠損値数:**")
        st.write(df[numeric_cols].isnull().sum())

# フッター
st.markdown("---")
st.markdown("*相関分析が完了しました。次は「時系列分析」ページをご確認ください。*")
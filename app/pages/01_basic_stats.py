import streamlit as st
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.basic_stats import BasicStats
from utils.config_loader import ConfigLoader
from utils.session_state import SessionStateManager

# ページ設定
st.set_page_config(
    page_title="基本統計 - EDA自動化アプリ",
    page_icon="📊",
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

# 基本統計が無効の場合
if not config['analysis']['basic_stats']:
    st.info("ℹ️ 基本統計分析は設定で無効になっています。")
    st.stop()

# データ取得
df = st.session_state.df
file_name = st.session_state.file_name

# タイトル
st.title("📊 基本統計")
st.markdown(f"**ファイル名:** {file_name}")
st.markdown("---")

# 基本統計分析
basic_stats = BasicStats(config)

try:
    basic_stats.display_basic_statistics(df)
except Exception as e:
    st.error(f"❌ 基本統計の生成中にエラーが発生しました: {str(e)}")
    st.write("**エラー詳細:**")
    st.code(str(e))

# 分析結果の保存
if 'basic_stats_result' not in st.session_state:
    with st.spinner("分析結果を保存中..."):
        try:
            stats_result = basic_stats.generate_basic_statistics(df)
            SessionStateManager.save_analysis_result('basic_stats', stats_result)
        except Exception as e:
            st.error(f"分析結果の保存に失敗しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("*基本統計分析が完了しました。次は「分布分析」ページをご確認ください。*")
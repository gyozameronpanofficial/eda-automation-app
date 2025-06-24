import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.visualization import Visualization
from utils.config_loader import ConfigLoader
from utils.session_state import SessionStateManager

# ページ設定
st.set_page_config(
    page_title="分布分析 - EDA自動化アプリ",
    page_icon="📈",
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

# 分布分析が無効の場合
if not config['analysis']['distribution']:
    st.info("ℹ️ 分布分析は設定で無効になっています。")
    st.stop()

# データ取得
df = st.session_state.df
file_name = st.session_state.file_name

# タイトル
st.title("📈 分布分析")
st.markdown(f"**ファイル名:** {file_name}")
st.markdown("---")

# 可視化オブジェクト作成
viz = Visualization(config)

# 数値列とカテゴリ列を取得
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

if not numeric_cols and not categorical_cols:
    st.warning("⚠️ 分析可能な列が見つかりませんでした。")
    st.stop()

# サイドバーで列選択
with st.sidebar:
    st.header("🔧 分析設定")
    
    analysis_type = st.radio(
        "分析タイプを選択",
        ["数値列分析", "カテゴリ列分析", "全体サマリー"]
    )
    
    if analysis_type == "数値列分析" and numeric_cols:
        selected_numeric_col = st.selectbox(
            "数値列を選択",
            numeric_cols
        )
        
        plot_type = st.radio(
            "プロットタイプ",
            ["標準プロット", "インタラクティブプロット"]
        )
    
    elif analysis_type == "カテゴリ列分析" and categorical_cols:
        selected_categorical_col = st.selectbox(
            "カテゴリ列を選択",
            categorical_cols
        )

# メインコンテンツ
if analysis_type == "数値列分析":
    if not numeric_cols:
        st.info("ℹ️ 数値列が見つかりませんでした。")
    else:
        if plot_type == "標準プロット":
            with st.spinner(f"'{selected_numeric_col}' の分布を分析中..."):
                viz.display_numeric_distribution(df, selected_numeric_col)
        
        elif plot_type == "インタラクティブプロット":
            st.subheader(f"📈 {selected_numeric_col} - インタラクティブ分析")
            
            tab1, tab2 = st.tabs(["ヒストグラム", "箱ひげ図"])
            
            with tab1:
                with st.spinner("インタラクティブヒストグラムを作成中..."):
                    fig_hist = viz.create_plotly_histogram(df, selected_numeric_col)
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            with tab2:
                with st.spinner("インタラクティブ箱ひげ図を作成中..."):
                    fig_box = viz.create_plotly_box_plot(df, selected_numeric_col)
                    st.plotly_chart(fig_box, use_container_width=True)

elif analysis_type == "カテゴリ列分析":
    if not categorical_cols:
        st.info("ℹ️ カテゴリ列が見つかりませんでした。")
    else:
        with st.spinner(f"'{selected_categorical_col}' の分布を分析中..."):
            viz.display_categorical_distribution(df, selected_categorical_col)

elif analysis_type == "全体サマリー":
    st.header("📊 全体分布サマリー")
    
    # 数値列サマリー
    if numeric_cols:
        st.subheader("🔢 数値列サマリー")
        
        progress_bar = st.progress(0)
        total_numeric = len(numeric_cols)
        
        numeric_summary = []
        
        for i, col in enumerate(numeric_cols):
            data = df[col].dropna()
            if len(data) > 0:
                summary = {
                    'カラム名': col,
                    'データ数': len(data),
                    '平均値': round(data.mean(), 3),
                    '中央値': round(data.median(), 3),
                    '標準偏差': round(data.std(), 3),
                    '最小値': round(data.min(), 3),
                    '最大値': round(data.max(), 3),
                    '歪度': round(data.skew(), 3),
                    '尖度': round(data.kurtosis(), 3)
                }
                numeric_summary.append(summary)
            
            progress_bar.progress((i + 1) / total_numeric)
        
        if numeric_summary:
            numeric_summary_df = pd.DataFrame(numeric_summary)
            st.dataframe(numeric_summary_df, use_container_width=True)
            
            # 外れ値サマリー
            st.subheader("🎯 外れ値サマリー")
            
            outlier_summary = []
            for col in numeric_cols:
                data = df[col].dropna()
                if len(data) > 0:
                    outliers = viz._detect_outliers(data)
                    summary = {
                        'カラム名': col,
                        'IQR法外れ値数': outliers['iqr']['count'],
                        'IQR法外れ値率(%)': round(outliers['iqr']['percentage'], 2),
                        'Z-score法外れ値数': outliers['zscore']['count'],
                        'Z-score法外れ値率(%)': round(outliers['zscore']['percentage'], 2),
                        '修正Z-score法外れ値数': outliers['modified_zscore']['count'],
                        '修正Z-score法外れ値率(%)': round(outliers['modified_zscore']['percentage'], 2)
                    }
                    outlier_summary.append(summary)
            
            if outlier_summary:
                outlier_summary_df = pd.DataFrame(outlier_summary)
                st.dataframe(outlier_summary_df, use_container_width=True)
    
    # カテゴリ列サマリー
    if categorical_cols:
        st.subheader("📝 カテゴリ列サマリー")
        
        categorical_summary = []
        max_categories = config['visualization'].get('max_categories', 20)
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            missing_count = df[col].isnull().sum()
            missing_rate = missing_count / len(df) * 100
            
            if unique_count > 0:
                most_frequent = df[col].mode().iloc[0] if len(df[col].dropna()) > 0 else "N/A"
                most_frequent_count = df[col].value_counts().iloc[0] if len(df[col].dropna()) > 0 else 0
                most_frequent_rate = most_frequent_count / len(df[col].dropna()) * 100 if len(df[col].dropna()) > 0 else 0
            else:
                most_frequent = "N/A"
                most_frequent_count = 0
                most_frequent_rate = 0
            
            summary = {
                'カラム名': col,
                'ユニーク値数': unique_count,
                '欠損数': missing_count,
                '欠損率(%)': round(missing_rate, 2),
                '最頻値': most_frequent,
                '最頻値出現数': most_frequent_count,
                '最頻値出現率(%)': round(most_frequent_rate, 2)
            }
            categorical_summary.append(summary)
        
        if categorical_summary:
            categorical_summary_df = pd.DataFrame(categorical_summary)
            st.dataframe(categorical_summary_df, use_container_width=True)

# 分析結果の保存
try:
    distribution_results = viz.create_distribution_plots(df)
    SessionStateManager.save_analysis_result('distribution', distribution_results)
except Exception as e:
    st.error(f"分析結果の保存に失敗しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("*分布分析が完了しました。次は「相関分析」ページをご確認ください。*")'], 2),
                        '修正Z-score法外れ値数': outliers['modified_zscore']['count'],
                        '修正Z-score法外れ値率(%)': round(outliers['modified_zscore']['percentage'], 2)
                    }
                    outlier_summary.append(summary)
            
            if outlier_summary:
                outlier_summary_df = pd.DataFrame(outlier_summary)
                st.dataframe(outlier_summary_df, use_container_width=True)
    
    # カテゴリ列サマリー
    if categorical_cols:
        st.subheader("📝 カテゴリ列サマリー")
        
        categorical_summary = []
        max_categories = config['visualization'].get('max_categories', 20)
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            missing_count = df[col].isnull().sum()
            missing_rate = missing_count / len(df) * 100
            
            if unique_count > 0:
                most_frequent = df[col].mode().iloc[0] if len(df[col].dropna()) > 0 else "N/A"
                most_frequent_count = df[col].value_counts().iloc[0] if len(df[col].dropna()) > 0 else 0
                most_frequent_rate = most_frequent_count / len(df[col].dropna()) * 100 if len(df[col].dropna()) > 0 else 0
            else:
                most_frequent = "N/A"
                most_frequent_count = 0
                most_frequent_rate = 0
            
            summary = {
                'カラム名': col,
                'ユニーク値数': unique_count,
                '欠損数': missing_count,
                '欠損率(%)': round(missing_rate, 2),
                '最頻値': most_frequent,
                '最頻値出現数': most_frequent_count,
                '最頻値出現率(%)': round(most_frequent_rate, 2)
            }
            categorical_summary.append(summary)
        
        if categorical_summary:
            categorical_summary_df = pd.DataFrame(categorical_summary)
            st.dataframe(categorical_summary_df, use_container_width=True)

# 分析結果の保存
try:
    distribution_results = viz.create_distribution_plots(df)
    SessionStateManager.save_analysis_result('distribution', distribution_results)
except Exception as e:
    st.error(f"分析結果の保存に失敗しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("*分布分析が完了しました。次は「相関分析」ページをご確認ください。*")'], 2),
                        '修正Z-score法外れ値数': outliers['modified_zscore']['count'],
                        '修正Z-score法外れ値率(%)': round(outliers['modified_zscore']['percentage'], 2)
                    }
                    outlier_summary.append(summary)
            
            if outlier_summary:
                outlier_summary_df = pd.DataFrame(outlier_summary)
                st.dataframe(outlier_summary_df, use_container_width=True)
    
    # カテゴリ列サマリー
    if categorical_cols:
        st.subheader("📝 カテゴリ列サマリー")
        
        categorical_summary = []
        max_categories = config['visualization'].get('max_categories', 20)
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            missing_count = df[col].isnull().sum()
            missing_rate = missing_count / len(df) * 100
            
            if unique_count > 0:
                most_frequent = df[col].mode().iloc[0] if len(df[col].dropna()) > 0 else "N/A"
                most_frequent_count = df[col].value_counts().iloc[0] if len(df[col].dropna()) > 0 else 0
                most_frequent_rate = most_frequent_count / len(df[col].dropna()) * 100 if len(df[col].dropna()) > 0 else 0
            else:
                most_frequent = "N/A"
                most_frequent_count = 0
                most_frequent_rate = 0
            
            summary = {
                'カラム名': col,
                'ユニーク値数': unique_count,
                '欠損数': missing_count,
                '欠損率(%)': round(missing_rate, 2),
                '最頻値': most_frequent,
                '最頻値出現数': most_frequent_count,
                '最頻値出現率(%)': round(most_frequent_rate, 2)
            }
            categorical_summary.append(summary)
        
        if categorical_summary:
            categorical_summary_df = pd.DataFrame(categorical_summary)
            st.dataframe(categorical_summary_df, use_container_width=True)

# 分析結果の保存
try:
    distribution_results = viz.create_distribution_plots(df)
    SessionStateManager.save_analysis_result('distribution', distribution_results)
except Exception as e:
    st.error(f"分析結果の保存に失敗しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("*分布分析が完了しました。次は「相関分析」ページをご確認ください。*")
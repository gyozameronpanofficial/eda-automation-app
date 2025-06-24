import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.timeseries import TimeSeries
from utils.config_loader import ConfigLoader
from utils.session_state import SessionStateManager

# ページ設定
st.set_page_config(
    page_title="時系列分析 - EDA自動化アプリ",
    page_icon="⏰",
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

# 時系列分析が無効の場合
if not config['analysis']['timeseries']:
    st.info("ℹ️ 時系列分析は設定で無効になっています。")
    st.stop()

# データ取得
df = st.session_state.df
file_name = st.session_state.file_name

# タイトル
st.title("⏰ 時系列分析")
st.markdown(f"**ファイル名:** {file_name}")
st.markdown("---")

# 時系列分析オブジェクト作成
ts_analyzer = TimeSeries(config)

# 日付列の検出
datetime_cols = ts_analyzer.detect_datetime_columns(df)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if not datetime_cols:
    st.warning("⚠️ 日付列が見つかりませんでした。")
    st.info("💡 対処方法:")
    st.markdown("""
    - データに日付列が含まれているか確認してください
    - 前処理ページでデータ型を日付型に変換してください
    - 日付形式が正しいか確認してください（例: 2023-01-01, 2023/01/01）
    """)
    st.stop()

if not numeric_cols:
    st.warning("⚠️ 数値列が見つかりませんでした。")
    st.info("時系列分析には少なくとも1つの数値列が必要です。")
    st.stop()

# サイドバーで設定
with st.sidebar:
    st.header("🔧 時系列分析設定")
    
    # 日付列の選択
    selected_date_col = st.selectbox(
        "📅 日付列を選択",
        datetime_cols,
        help="時系列分析に使用する日付列を選択してください"
    )
    
    # 値列の選択
    selected_value_cols = st.multiselect(
        "📊 値列を選択",
        numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
        help="時系列分析に使用する数値列を選択してください（複数選択可）"
    )
    
    if selected_value_cols:
        # 移動平均の設定
        st.subheader("📈 移動平均設定")
        enable_ma = st.checkbox("移動平均を表示", value=True)
        
        if enable_ma:
            ma_windows = st.multiselect(
                "移動平均の期間",
                [7, 14, 30, 60, 90],
                default=[7, 30],
                help="移動平均を計算する期間を選択してください"
            )
        
        # 予測設定
        st.subheader("🔮 予測設定")
        enable_prediction = st.checkbox("将来値を予測", value=True)
        
        if enable_prediction:
            prediction_periods = st.slider(
                "予測期間",
                min_value=5,
                max_value=100,
                value=30,
                help="将来何期間先まで予測するかを設定してください"
            )

# メインコンテンツ
if not selected_value_cols:
    st.info("👆 サイドバーで値列を選択してください。")
    st.stop()

# 各値列について分析
for value_col in selected_value_cols:
    st.header(f"📊 {value_col} の時系列分析")
    
    # データ準備
    with st.spinner("データを準備中..."):
        ts_data = ts_analyzer.prepare_timeseries_data(df, selected_date_col, [value_col])
    
    if len(ts_data) == 0:
        st.warning(f"⚠️ {value_col} の有効なデータがありません。")
        continue
    
    # 基本情報表示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("データ数", len(ts_data))
    with col2:
        st.metric("期間", f"{ts_data[selected_date_col].min().date()} - {ts_data[selected_date_col].max().date()}")
    with col3:
        st.metric("平均値", f"{ts_data[value_col].mean():.3f}")
    with col4:
        st.metric("標準偏差", f"{ts_data[value_col].std():.3f}")
    
    # トレンド分析
    trend_analysis = ts_analyzer.detect_trend(ts_data, selected_date_col, value_col)
    
    if 'error' not in trend_analysis:
        st.subheader("📈 トレンド分析")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("トレンド方向", trend_analysis['trend_direction'])
        with col2:
            st.metric("傾き", f"{trend_analysis['slope']:.6f}")
        with col3:
            st.metric("決定係数 (R²)", f"{trend_analysis['r2_score']:.3f}")
    
    # 移動平均の計算
    moving_averages = None
    if enable_ma and ma_windows:
        with st.spinner("移動平均を計算中..."):
            moving_averages = ts_analyzer.calculate_moving_averages(ts_data[value_col], ma_windows)
    
    # 予測の実行
    predictions = None
    prediction_info = None
    if enable_prediction:
        with st.spinner("将来値を予測中..."):
            predictions, prediction_info = ts_analyzer.predict_future_values(
                ts_data, selected_date_col, value_col, prediction_periods
            )
            
            if 'error' not in prediction_info:
                st.subheader("🔮 予測結果")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("予測モデル", prediction_info['model_type'].title())
                with col2:
                    st.metric("モデル精度 (R²)", f"{prediction_info['r2_score']:.3f}")
                with col3:
                    st.metric("予測期間", f"{prediction_info['future_periods']} 期間")
    
    # プロット表示
    st.subheader("📈 時系列プロット")
    
    plot_type = st.radio(
        f"プロットタイプ ({value_col})",
        ["標準プロット", "インタラクティブプロット"],
        key=f"plot_type_{value_col}",
        horizontal=True
    )
    
    if plot_type == "標準プロット":
        with st.spinner("標準プロットを作成中..."):
            fig = ts_analyzer.create_timeseries_plot(
                ts_data, selected_date_col, value_col,
                moving_averages, predictions
            )
            st.pyplot(fig)
    
    elif plot_type == "インタラクティブプロット":
        with st.spinner("インタラクティブプロットを作成中..."):
            fig = ts_analyzer.create_interactive_timeseries_plot(
                ts_data, selected_date_col, value_col,
                moving_averages, predictions
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 周期性分析
    st.subheader("🔄 周期性分析")
    
    with st.spinner("周期性を分析中..."):
        periodicity = ts_analyzer.analyze_periodicity(ts_data, selected_date_col, value_col)
    
    tab1, tab2, tab3 = st.tabs(["月別統計", "曜日別統計", "年別統計"])
    
    with tab1:
        if not periodicity['monthly_stats'].empty:
            st.write("**月別の統計**")
            monthly_display = periodicity['monthly_stats'].round(3)
            monthly_display.index = [f"{i}月" for i in monthly_display.index]
            st.dataframe(monthly_display, use_container_width=True)
        else:
            st.info("月別統計を計算するのに十分なデータがありません。")
    
    with tab2:
        if not periodicity['weekday_stats'].empty:
            st.write("**曜日別の統計**")
            st.dataframe(periodicity['weekday_stats'].round(3), use_container_width=True)
        else:
            st.info("曜日別統計を計算するのに十分なデータがありません。")
    
    with tab3:
        if not periodicity['yearly_stats'].empty:
            st.write("**年別の統計**")
            st.dataframe(periodicity['yearly_stats'].round(3), use_container_width=True)
        else:
            st.info("年別統計を計算するのに十分なデータがありません。")
    
    # データの詳細
    with st.expander(f"📋 {value_col} のデータ詳細"):
        st.write("**時系列データ（最初の100行）**")
        display_data = ts_data.head(100)
        st.dataframe(display_data, use_container_width=True)
        
        # データダウンロード
        csv = ts_data.to_csv(index=False)
        st.download_button(
            label=f"📥 {value_col} の時系列データをCSVでダウンロード",
            data=csv,
            file_name=f"timeseries_{value_col}.csv",
            mime="text/csv",
            key=f"download_{value_col}"
        )
    
    st.markdown("---")

# 分析結果の保存
try:
    timeseries_results = {
        'datetime_columns': datetime_cols,
        'selected_date_column': selected_date_col,
        'selected_value_columns': selected_value_cols,
        'analysis_completed': True
    }
    SessionStateManager.save_analysis_result('timeseries', timeseries_results)
except Exception as e:
    st.error(f"分析結果の保存に失敗しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("*時系列分析が完了しました。次は「前処理」ページをご確認ください。*")
import streamlit as st
import pandas as pd
import japanize_matplotlib
import matplotlib.pyplot as plt
from components.file_handler import FileHandler
from components.basic_stats import BasicStats
from utils.config_loader import ConfigLoader
from utils.session_state import SessionStateManager

# ページ設定
st.set_page_config(
    page_title="EDA自動化アプリ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 設定読み込み
@st.cache_resource
def load_config():
    return ConfigLoader.load_config()

config = load_config()

# セッション状態初期化
SessionStateManager.initialize()

# タイトル
st.title("📊 EDA自動化アプリ")
st.markdown("---")

# サイドバー
with st.sidebar:
    st.header("🔧 設定")
    
    # ファイルサイズ制限表示
    max_size = config['general']['max_file_size_mb']
    st.info(f"最大ファイルサイズ: {max_size}MB")
    
    # 有効な分析機能表示
    st.subheader("📋 有効な分析機能")
    analysis_config = config['analysis']
    for key, value in analysis_config.items():
        if value:
            labels = {
                'basic_stats': '基本統計',
                'distribution': '分布分析',
                'correlation': '相関分析',
                'timeseries': '時系列分析',
                'preprocessing': '前処理'
            }
            st.success(f"✅ {labels.get(key, key)}")

# メインコンテンツ
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 データアップロード")
    
    # ファイルアップローダー
    uploaded_file = st.file_uploader(
        "CSVまたはExcelファイルを選択してください",
        type=['csv', 'xlsx', 'xls'],
        help=f"最大ファイルサイズ: {max_size}MB"
    )
    
    if uploaded_file is not None:
        # ファイル情報表示
        file_details = {
            "ファイル名": uploaded_file.name,
            "ファイルサイズ": f"{uploaded_file.size / 1024 / 1024:.2f} MB",
            "ファイル形式": uploaded_file.type
        }
        
        with st.expander("📋 ファイル情報", expanded=True):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        # ファイルサイズチェック
        if uploaded_file.size > max_size * 1024 * 1024:
            st.error(f"❌ ファイルサイズが上限({max_size}MB)を超えています。")
            st.stop()
        
        # データ読み込みボタン
        if st.button("🔄 データを読み込む", type="primary"):
            with st.spinner("データを読み込み中..."):
                try:
                    # ファイル読み込み
                    file_handler = FileHandler(config)
                    df = file_handler.load_file(uploaded_file)
                    
                    # セッション状態に保存
                    st.session_state.df = df
                    st.session_state.original_df = df.copy()
                    st.session_state.file_name = uploaded_file.name
                    
                    st.success("✅ データの読み込みが完了しました！")
                    
                except Exception as e:
                    st.error(f"❌ データの読み込みに失敗しました: {str(e)}")
                    st.stop()

with col2:
    if 'df' in st.session_state:
        st.header("📊 データ概要")
        df = st.session_state.df
        
        # 基本情報
        info_data = {
            "行数": f"{len(df):,}",
            "列数": f"{len(df.columns):,}",
            "メモリ使用量": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        }
        
        for key, value in info_data.items():
            st.metric(key, value)
        
        # データ型情報
        with st.expander("📋 データ型情報"):
            dtype_counts = df.dtypes.value_counts()
            for dtype, count in dtype_counts.items():
                st.write(f"**{dtype}:** {count}列")

# データが読み込まれている場合の操作
if 'df' in st.session_state:
    st.markdown("---")
    
    # データプレビュー
    st.header("👀 データプレビュー")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        show_head = st.number_input("先頭行数", min_value=1, max_value=100, value=5)
    with col2:
        show_tail = st.number_input("末尾行数", min_value=1, max_value=100, value=5)
    with col3:
        show_sample = st.number_input("ランダム抽出行数", min_value=1, max_value=100, value=5)
    
    tab1, tab2, tab3, tab4 = st.tabs(["先頭データ", "末尾データ", "ランダム抽出", "データ型"])
    
    with tab1:
        st.dataframe(st.session_state.df.head(show_head), use_container_width=True)
    
    with tab2:
        st.dataframe(st.session_state.df.tail(show_tail), use_container_width=True)
    
    with tab3:
        st.dataframe(st.session_state.df.sample(n=min(show_sample, len(st.session_state.df))), use_container_width=True)
    
    with tab4:
        dtype_df = pd.DataFrame({
            'カラム名': st.session_state.df.columns,
            'データ型': st.session_state.df.dtypes.astype(str),
            '非null数': st.session_state.df.count(),
            'null数': st.session_state.df.isnull().sum(),
            'null率(%)': (st.session_state.df.isnull().sum() / len(st.session_state.df) * 100).round(2)
        })
        st.dataframe(dtype_df, use_container_width=True)
    
    # 分析開始ボタン
    st.markdown("---")
    st.header("🚀 分析開始")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📈 分析を開始する", type="primary", use_container_width=True):
            st.session_state.analysis_started = True
            st.success("✅ 分析が開始されました！左のサイドバーから各分析ページをご覧ください。")
            st.balloons()

# 分析未開始の場合の案内
else:
    st.info("👆 まずはCSVまたはExcelファイルをアップロードしてください。")
    
    # サンプルデータの案内
    st.markdown("---")
    st.header("💡 使い方")
    
    with st.expander("📚 アプリの使い方", expanded=True):
        st.markdown("""
        1. **データアップロード**: CSVまたはExcelファイルを選択
        2. **データ読み込み**: "データを読み込む"ボタンをクリック
        3. **データ確認**: データプレビューで内容を確認
        4. **分析開始**: "分析を開始する"ボタンをクリック
        5. **結果確認**: 左のサイドバーから各分析ページを選択
        
        ### 📋 対応ファイル形式
        - CSV（カンマ区切り、タブ区切り、セミコロン区切り）
        - Excel（.xlsx, .xls）
        
        ### 🔧 主な機能
        - **基本統計**: データの概要、基本統計量、欠損値チェック
        - **分布分析**: ヒストグラム、箱ひげ図、外れ値検出
        - **相関分析**: 相関行列、散布図マトリックス
        - **時系列分析**: 時系列プロット、トレンド分析
        - **前処理**: 欠損値処理、外れ値除去、データ型変換
        """)

# フッター
st.markdown("---")
st.markdown("*EDA自動化アプリ - データサイエンスチーム*")
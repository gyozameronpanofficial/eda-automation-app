import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.preprocessor import Preprocessor
from utils.config_loader import ConfigLoader
from utils.session_state import SessionStateManager

# ページ設定
st.set_page_config(
    page_title="前処理 - EDA自動化アプリ",
    page_icon="🔧",
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

# 前処理が無効の場合
if not config['analysis']['preprocessing']:
    st.info("ℹ️ 前処理機能は設定で無効になっています。")
    st.stop()

# データ取得
original_df = st.session_state.df
file_name = st.session_state.file_name

# セッション状態の初期化
if 'current_df' not in st.session_state:
    st.session_state.current_df = original_df.copy()

if 'df_history' not in st.session_state:
    st.session_state.df_history = [original_df.copy()]

if 'preprocessor' not in st.session_state:
    st.session_state.preprocessor = Preprocessor(config)

# タイトル
st.title("🔧 前処理")
st.markdown(f"**ファイル名:** {file_name}")
st.markdown("---")

# 前処理オブジェクト
preprocessor = st.session_state.preprocessor
current_df = st.session_state.current_df

# メインレイアウト
col1, col2, col3 = st.columns([1, 2, 1])

# 左側: 前処理メニュー
with col1:
    st.header("🛠️ 前処理メニュー")
    
    # データ概要
    with st.expander("📊 データ概要", expanded=True):
        summary = preprocessor.get_data_summary(current_df)
        st.metric("行数", f"{summary['shape'][0]:,}")
        st.metric("列数", f"{summary['shape'][1]:,}")
        st.metric("メモリ使用量", f"{summary['memory_usage']:.2f} MB")
        st.metric("重複行数", summary['duplicate_rows'])
    
    # 前処理タイプの選択
    preprocessing_type = st.selectbox(
        "前処理タイプを選択",
        ["欠損値処理", "外れ値除去", "データ型変換", "重複行除去"]
    )
    
    if preprocessing_type == "欠損値処理":
        st.subheader("🕳️ 欠損値処理")
        
        # 欠損値のある列を検出
        missing_info = preprocessor.detect_missing_values(current_df)
        
        if not missing_info:
            st.success("✅ 欠損値はありません")
        else:
            # 欠損値のある列を選択
            missing_columns = list(missing_info.keys())
            selected_column = st.selectbox("対象列を選択", missing_columns)
            
            if selected_column:
                col_info = missing_info[selected_column]
                st.write(f"**欠損数:** {col_info['count']} ({col_info['percentage']:.1f}%)")
                st.write(f"**データ型:** {col_info['dtype']}")
                
                # 補完方法の選択
                missing_methods = config['preprocessing']['missing_value_methods']
                selected_method = st.selectbox("補完方法を選択", missing_methods)
                
                # カスタム値の場合
                custom_value = None
                if selected_method == "カスタム値":
                    custom_value = st.text_input("補完する値を入力")
                
                # プレビューボタン
                if st.button("🔍 プレビュー", key="missing_preview"):
                    if selected_method == "カスタム値" and custom_value:
                        preview_df, preview_info = preprocessor.handle_missing_values_custom(
                            current_df, selected_column, custom_value
                        )
                    else:
                        preview_df, preview_info = preprocessor.handle_missing_values(
                            current_df, selected_column, selected_method
                        )
                    
                    if 'error' not in preview_info:
                        st.session_state.preview_df = preview_df
                        st.session_state.preview_info = preview_info
                        st.session_state.show_preview = True
                    else:
                        st.error(preview_info['error'])
                
                # 実行ボタン
                if st.button("✅ 実行", key="missing_execute"):
                    if selected_method == "カスタム値" and custom_value:
                        new_df, operation_info = preprocessor.handle_missing_values_custom(
                            current_df, selected_column, custom_value
                        )
                    else:
                        new_df, operation_info = preprocessor.handle_missing_values(
                            current_df, selected_column, selected_method
                        )
                    
                    if 'error' not in operation_info:
                        st.session_state.current_df = new_df
                        st.session_state.df_history.append(new_df.copy())
                        preprocessor.add_operation_to_history(operation_info)
                        st.success("✅ 欠損値処理が完了しました")
                        st.rerun()
                    else:
                        st.error(operation_info['error'])
    
    elif preprocessing_type == "外れ値除去":
        st.subheader("🎯 外れ値除去")
        
        # 数値列のみを対象
        numeric_columns = current_df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_columns:
            st.warning("数値列が見つかりません")
        else:
            selected_column = st.selectbox("対象列を選択", numeric_columns)
            
            # 外れ値検出方法の選択
            outlier_methods = config['preprocessing']['outlier_methods']
            method_mapping = {
                'IQR法': 'iqr',
                'Z-score法': 'zscore', 
                '修正Z-score法': 'modified_zscore'
            }
            
            selected_method_label = st.selectbox("検出方法を選択", outlier_methods)
            selected_method = method_mapping[selected_method_label]
            
            # 外れ値情報の表示
            outlier_info = preprocessor.detect_outliers(current_df, selected_column, selected_method)
            
            if 'error' not in outlier_info:
                st.write(f"**外れ値数:** {outlier_info['outlier_count']} ({outlier_info['outlier_percentage']:.1f}%)")
                
                if outlier_info['outlier_count'] > 0:
                    # プレビューボタン
                    if st.button("🔍 プレビュー", key="outlier_preview"):
                        preview_df, preview_info = preprocessor.remove_outliers(
                            current_df, selected_column, selected_method
                        )
                        st.session_state.preview_df = preview_df
                        st.session_state.preview_info = preview_info
                        st.session_state.show_preview = True
                    
                    # 実行ボタン
                    if st.button("✅ 実行", key="outlier_execute"):
                        new_df, operation_info = preprocessor.remove_outliers(
                            current_df, selected_column, selected_method
                        )
                        
                        if 'error' not in operation_info:
                            st.session_state.current_df = new_df
                            st.session_state.df_history.append(new_df.copy())
                            preprocessor.add_operation_to_history(operation_info)
                            st.success("✅ 外れ値除去が完了しました")
                            st.rerun()
                        else:
                            st.error(operation_info['error'])
                else:
                    st.info("外れ値は検出されませんでした")
            else:
                st.error(outlier_info['error'])
    
    elif preprocessing_type == "データ型変換":
        st.subheader("🔄 データ型変換")
        
        selected_column = st.selectbox("対象列を選択", current_df.columns.tolist())
        
        if selected_column:
            current_type = str(current_df[selected_column].dtype)
            st.write(f"**現在の型:** {current_type}")
            
            # 変換先の型を選択
            type_options = ['int64', 'float64', 'object', 'datetime64[ns]', 'category', 'bool']
            target_type = st.selectbox("変換先の型を選択", type_options)
            
            # プレビューボタン
            if st.button("🔍 プレビュー", key="dtype_preview"):
                preview_df, preview_info = preprocessor.convert_data_type(
                    current_df, selected_column, target_type
                )
                
                if 'error' not in preview_info:
                    st.session_state.preview_df = preview_df
                    st.session_state.preview_info = preview_info
                    st.session_state.show_preview = True
                else:
                    st.error(preview_info['error'])
            
            # 実行ボタン
            if st.button("✅ 実行", key="dtype_execute"):
                new_df, operation_info = preprocessor.convert_data_type(
                    current_df, selected_column, target_type
                )
                
                if 'error' not in operation_info:
                    st.session_state.current_df = new_df
                    st.session_state.df_history.append(new_df.copy())
                    preprocessor.add_operation_to_history(operation_info)
                    st.success("✅ データ型変換が完了しました")
                    st.rerun()
                else:
                    st.error(operation_info['error'])
    
    elif preprocessing_type == "重複行除去":
        st.subheader("🔄 重複行除去")
        
        duplicate_count = current_df.duplicated().sum()
        st.write(f"**重複行数:** {duplicate_count}")
        
        if duplicate_count > 0:
            keep_option = st.selectbox(
                "保持する行を選択", 
                ['first', 'last'],
                format_func=lambda x: '最初の行を保持' if x == 'first' else '最後の行を保持'
            )
            
            if st.button("✅ 重複行を除去", key="duplicate_execute"):
                new_df = current_df.drop_duplicates(keep=keep_option)
                
                operation_info = {
                    'operation': 'duplicate_removal',
                    'method': f'keep_{keep_option}',
                    'rows_removed': duplicate_count,
                    'original_shape': current_df.shape,
                    'final_shape': new_df.shape,
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                st.session_state.current_df = new_df
                st.session_state.df_history.append(new_df.copy())
                preprocessor.add_operation_to_history(operation_info)
                st.success("✅ 重複行除去が完了しました")
                st.rerun()
        else:
            st.info("重複行はありません")
    
    # 操作ボタン
    st.markdown("---")
    
    # 戻るボタン
    if len(st.session_state.df_history) > 1:
        if st.button("↶ 前の状態に戻る", key="undo"):
            st.session_state.df_history.pop()  # 現在の状態を削除
            st.session_state.current_df = st.session_state.df_history[-1].copy()
            if len(preprocessor.get_processing_history()) > 0:
                preprocessor.get_processing_history().pop()  # 履歴からも削除
            st.success("前の状態に戻りました")
            st.rerun()
    
    # リセットボタン
    if st.button("🔄 最初の状態にリセット", key="reset"):
        st.session_state.current_df = original_df.copy()
        st.session_state.df_history = [original_df.copy()]
        preprocessor.clear_history()
        st.success("最初の状態にリセットしました")
        st.rerun()

# 中央: データプレビュー
with col2:
    st.header("👀 データプレビュー")
    
    # プレビュー表示の切り替え
    if st.session_state.get('show_preview', False) and 'preview_df' in st.session_state:
        tab1, tab2 = st.tabs(["処理後プレビュー", "現在のデータ"])
        
        with tab1:
            st.subheader("🔍 処理後のプレビュー")
            preview_df = st.session_state.preview_df
            preview_info = st.session_state.preview_info
            
            # 処理情報の表示
            if 'operation' in preview_info:
                st.info(f"**操作:** {preview_info['operation']}")
                if 'processed_count' in preview_info:
                    st.write(f"**処理された項目数:** {preview_info['processed_count']}")
                if 'rows_removed' in preview_info:
                    st.write(f"**削除される行数:** {preview_info['rows_removed']}")
            
            # プレビューデータ表示
            st.dataframe(preview_df.head(100), use_container_width=True)
            
            # 処理前後の比較
            comparison = preprocessor.compare_dataframes(current_df, preview_df)
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("行数変化", 
                         f"{comparison['shape_after'][0]:,}", 
                         f"{-comparison['rows_changed']:,}")
            with col_b:
                st.metric("メモリ使用量", 
                         f"{comparison['memory_after']:.1f}MB",
                         f"{comparison['memory_after']-comparison['memory_before']:.1f}MB")
            with col_c:
                if st.button("✅ この処理を確定", key="confirm_preview"):
                    st.session_state.current_df = preview_df
                    st.session_state.df_history.append(preview_df.copy())
                    preprocessor.add_operation_to_history(preview_info)
                    st.session_state.show_preview = False
                    st.success("✅ 処理が確定されました")
                    st.rerun()
        
        with tab2:
            st.subheader("📊 現在のデータ")
            st.dataframe(current_df.head(100), use_container_width=True)
        
        # プレビューを閉じるボタン
        if st.button("❌ プレビューを閉じる", key="close_preview"):
            st.session_state.show_preview = False
            st.rerun()
    
    else:
        # 通常のデータ表示
        st.subheader("📊 現在のデータ")
        
        # データ表示オプション
        col_a, col_b = st.columns(2)
        with col_a:
            display_rows = st.selectbox("表示行数", [50, 100, 200, 500], index=1)
        with col_b:
            show_info = st.checkbox("列情報を表示", value=False)
        
        # データフレーム表示
        st.dataframe(current_df.head(display_rows), use_container_width=True)
        
        # 列情報表示
        if show_info:
            st.subheader("📋 列情報")
            col_info_data = []
            for col in current_df.columns:
                info = preprocessor.get_column_info(current_df, col)
                if 'error' not in info:
                    col_info_data.append({
                        '列名': info['name'],
                        'データ型': info['dtype'],
                        '非null数': info['non_null_count'],
                        'null数': info['null_count'],
                        'ユニーク数': info['unique_count']
                    })
            
            if col_info_data:
                info_df = pd.DataFrame(col_info_data)
                st.dataframe(info_df, use_container_width=True)

# 右側: 処理履歴と操作
with col3:
    st.header("📝 処理履歴")
    
    history = preprocessor.get_processing_history()
    
    if history:
        st.write(f"**実行済み操作: {len(history)} 件**")
        
        for i, operation in enumerate(reversed(history)):
            with st.expander(f"Step {len(history)-i}: {operation.get('operation', 'Unknown')}", expanded=False):
                st.write(f"**時刻:** {operation.get('timestamp', 'Unknown')}")
                
                if operation['operation'] == 'missing_value_handling':
                    st.write(f"**対象列:** {operation.get('column', 'Unknown')}")
                    st.write(f"**方法:** {operation.get('method', 'Unknown')}")
                    st.write(f"**処理数:** {operation.get('processed_count', 0)}")
                    if 'fill_value' in operation:
                        st.write(f"**補完値:** {operation['fill_value']}")
                
                elif operation['operation'] == 'outlier_removal':
                    st.write(f"**対象列:** {operation.get('column', 'Unknown')}")
                    st.write(f"**方法:** {operation.get('method', 'Unknown')}")
                    st.write(f"**除去数:** {operation.get('outlier_count', 0)}")
                
                elif operation['operation'] == 'data_type_conversion':
                    st.write(f"**対象列:** {operation.get('column', 'Unknown')}")
                    st.write(f"**変換:** {operation.get('original_type', 'Unknown')} → {operation.get('target_type', 'Unknown')}")
                    if operation.get('conversion_errors', 0) > 0:
                        st.warning(f"変換エラー: {operation['conversion_errors']} 件")
                
                elif operation['operation'] == 'duplicate_removal':
                    st.write(f"**方法:** {operation.get('method', 'Unknown')}")
                    st.write(f"**除去数:** {operation.get('rows_removed', 0)}")
    else:
        st.info("まだ処理履歴がありません")
    
    # データダウンロード
    st.markdown("---")
    st.subheader("📥 データダウンロード")
    
    # 現在のデータをCSVでダウンロード
    csv_data = current_df.to_csv(index=False)
    st.download_button(
        label="📁 処理済みデータをダウンロード",
        data=csv_data,
        file_name=f"processed_{file_name}",
        mime="text/csv",
        help="現在の処理済みデータをCSVファイルとしてダウンロードします"
    )
    
    # 処理履歴をダウンロード
    if history:
        history_text = "前処理履歴レポート\n" + "="*50 + "\n\n"
        for i, operation in enumerate(history):
            history_text += f"Step {i+1}: {operation.get('operation', 'Unknown')}\n"
            history_text += f"時刻: {operation.get('timestamp', 'Unknown')}\n"
            
            if operation['operation'] == 'missing_value_handling':
                history_text += f"対象列: {operation.get('column', 'Unknown')}\n"
                history_text += f"方法: {operation.get('method', 'Unknown')}\n"
                history_text += f"処理数: {operation.get('processed_count', 0)}\n"
                if 'fill_value' in operation:
                    history_text += f"補完値: {operation['fill_value']}\n"
            
            elif operation['operation'] == 'outlier_removal':
                history_text += f"対象列: {operation.get('column', 'Unknown')}\n"
                history_text += f"方法: {operation.get('method', 'Unknown')}\n"
                history_text += f"除去数: {operation.get('outlier_count', 0)}\n"
            
            elif operation['operation'] == 'data_type_conversion':
                history_text += f"対象列: {operation.get('column', 'Unknown')}\n"
                history_text += f"変換: {operation.get('original_type', 'Unknown')} → {operation.get('target_type', 'Unknown')}\n"
                if operation.get('conversion_errors', 0) > 0:
                    history_text += f"変換エラー: {operation['conversion_errors']} 件\n"
            
            elif operation['operation'] == 'duplicate_removal':
                history_text += f"方法: {operation.get('method', 'Unknown')}\n"
                history_text += f"除去数: {operation.get('rows_removed', 0)}\n"
            
            history_text += "\n" + "-"*30 + "\n\n"
        
        st.download_button(
            label="📋 処理履歴をダウンロード",
            data=history_text,
            file_name=f"preprocessing_history_{file_name.replace('.csv', '.txt')}",
            mime="text/plain",
            help="実行した前処理の履歴をテキストファイルとしてダウンロードします"
        )

# 分析結果の保存
try:
    preprocessing_results = {
        'original_shape': original_df.shape,
        'current_shape': current_df.shape,
        'processing_steps': len(history),
        'history': history
    }
    SessionStateManager.save_analysis_result('preprocessing', preprocessing_results)
    
    # 処理済みデータをセッションに保存
    if len(history) > 0:
        st.session_state.preprocessed_df = current_df
except Exception as e:
    st.error(f"分析結果の保存に失敗しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("*前処理が完了しました。処理済みデータをダウンロードしてご活用ください。*")
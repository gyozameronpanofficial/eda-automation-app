import streamlit as st
from typing import Any, Optional

class SessionStateManager:
    """Streamlitセッション状態の管理を担当するクラス"""
    
    @staticmethod
    def initialize():
        """セッション状態の初期化"""
        if 'df' not in st.session_state:
            st.session_state.df = None
        
        if 'original_df' not in st.session_state:
            st.session_state.original_df = None
        
        if 'file_name' not in st.session_state:
            st.session_state.file_name = None
        
        if 'analysis_started' not in st.session_state:
            st.session_state.analysis_started = False
        
        if 'preprocessed_df' not in st.session_state:
            st.session_state.preprocessed_df = None
        
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        
        if 'selected_datetime_column' not in st.session_state:
            st.session_state.selected_datetime_column = None
    
    @staticmethod
    def set_value(key: str, value: Any):
        """セッション状態に値を設定"""
        st.session_state[key] = value
    
    @staticmethod
    def get_value(key: str, default: Any = None) -> Any:
        """セッション状態から値を取得"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def has_data() -> bool:
        """データが読み込まれているかチェック"""
        return st.session_state.get('df') is not None
    
    @staticmethod
    def has_analysis_started() -> bool:
        """分析が開始されているかチェック"""
        return st.session_state.get('analysis_started', False)
    
    @staticmethod
    def clear_analysis_results():
        """分析結果をクリア"""
        st.session_state.analysis_results = {}
    
    @staticmethod
    def save_analysis_result(analysis_type: str, result: Any):
        """分析結果を保存"""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        st.session_state.analysis_results[analysis_type] = result
    
    @staticmethod
    def get_analysis_result(analysis_type: str) -> Optional[Any]:
        """分析結果を取得"""
        return st.session_state.analysis_results.get(analysis_type)
    
    @staticmethod
    def reset_session():
        """セッション状態をリセット"""
        keys_to_reset = [
            'df', 'original_df', 'file_name', 'analysis_started',
            'preprocessed_df', 'analysis_results', 'selected_datetime_column'
        ]
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
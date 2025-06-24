import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
from typing import Dict, Any, Tuple

class BasicStats:
    """基本統計の分析を担当するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.viz_config = config.get('visualization', {})
        
        # matplotlib設定
        plt.style.use('default')
        sns.set_style(self.viz_config.get('style', 'whitegrid'))
        
    def generate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        基本統計量を生成
        
        Args:
            df: 分析対象のデータフレーム
            
        Returns:
            Dict[str, Any]: 基本統計の結果
        """
        results = {}
        
        # データ形状
        results['shape'] = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        }
        
        # データ型情報
        results['dtypes'] = self._analyze_dtypes(df)
        
        # 欠損値情報
        results['missing_values'] = self._analyze_missing_values(df)
        
        # 重複値情報
        results['duplicates'] = self._analyze_duplicates(df)
        
        # 数値列の基本統計量
        results['numeric_stats'] = self._analyze_numeric_columns(df)
        
        # カテゴリ列の基本統計量
        results['categorical_stats'] = self._analyze_categorical_columns(df)
        
        return results
    
    def _analyze_dtypes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データ型の分析"""
        dtype_counts = df.dtypes.value_counts()
        
        return {
            'dtype_counts': dtype_counts.to_dict(),
            'column_dtypes': df.dtypes.to_dict(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist()
        }
    
    def _analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """欠損値の分析"""
        missing_count = df.isnull().sum()
        missing_percent = (missing_count / len(df)) * 100
        
        missing_summary = pd.DataFrame({
            'カラム名': df.columns,
            '欠損数': missing_count.values,
            '欠損率(%)': missing_percent.values
        })
        missing_summary = missing_summary[missing_summary['欠損数'] > 0].sort_values('欠損数', ascending=False)
        
        return {
            'total_missing': missing_count.sum(),
            'missing_percentage': (missing_count.sum() / (len(df) * len(df.columns))) * 100,
            'missing_summary': missing_summary,
            'columns_with_missing': missing_summary['カラム名'].tolist()
        }
    
    def _analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """重複値の分析"""
        duplicate_count = df.duplicated().sum()
        duplicate_percent = (duplicate_count / len(df)) * 100
        
        return {
            'duplicate_count': duplicate_count,
            'duplicate_percentage': duplicate_percent,
            'unique_count': len(df) - duplicate_count
        }
    
    def _analyze_numeric_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """数値列の分析"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {'message': '数値列が見つかりませんでした'}
        
        # 基本統計量
        basic_stats = numeric_df.describe()
        
        # 追加統計量
        additional_stats = pd.DataFrame({
            'データ型': numeric_df.dtypes,
            '欠損数': numeric_df.isnull().sum(),
            '欠損率(%)': (numeric_df.isnull().sum() / len(numeric_df)) * 100,
            '歪度': numeric_df.skew(),
            '尖度': numeric_df.kurtosis(),
            'ゼロ値数': (numeric_df == 0).sum(),
            '負値数': (numeric_df < 0).sum(),
            '無限大数': np.isinf(numeric_df).sum()
        })
        
        return {
            'basic_stats': basic_stats,
            'additional_stats': additional_stats,
            'column_count': len(numeric_df.columns)
        }
    
    def _analyze_categorical_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """カテゴリ列の分析"""
        categorical_df = df.select_dtypes(include=['object', 'category'])
        
        if categorical_df.empty:
            return {'message': 'カテゴリ列が見つかりませんでした'}
        
        categorical_stats = pd.DataFrame({
            'データ型': categorical_df.dtypes,
            '欠損数': categorical_df.isnull().sum(),
            '欠損率(%)': (categorical_df.isnull().sum() / len(categorical_df)) * 100,
            'ユニーク値数': categorical_df.nunique(),
            'ユニーク率(%)': (categorical_df.nunique() / len(categorical_df)) * 100,
            '最頻値': categorical_df.mode().iloc[0] if len(categorical_df) > 0 else None,
            '最頻値出現数': [categorical_df[col].value_counts().iloc[0] if len(categorical_df[col].dropna()) > 0 else 0 
                           for col in categorical_df.columns]
        })
        
        return {
            'categorical_stats': categorical_stats,
            'column_count': len(categorical_df.columns)
        }
    
    def display_basic_statistics(self, df: pd.DataFrame) -> None:
        """基本統計量をStreamlitで表示"""
        st.header("📊 基本統計")
        
        with st.spinner("基本統計を計算中..."):
            stats = self.generate_basic_statistics(df)
        
        # データ形状情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("行数", f"{stats['shape']['rows']:,}")
        with col2:
            st.metric("列数", f"{stats['shape']['columns']:,}")
        with col3:
            st.metric("メモリ使用量", f"{stats['shape']['memory_usage_mb']:.2f} MB")
        
        st.markdown("---")
        
        # タブで情報を整理
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "データ型", "欠損値", "重複値", "数値列統計", "カテゴリ列統計"
        ])
        
        with tab1:
            self._display_dtype_info(stats['dtypes'])
        
        with tab2:
            self._display_missing_values(stats['missing_values'])
        
        with tab3:
            self._display_duplicates(stats['duplicates'])
        
        with tab4:
            self._display_numeric_stats(stats['numeric_stats'])
        
        with tab5:
            self._display_categorical_stats(stats['categorical_stats'])
    
    def _display_dtype_info(self, dtype_info: Dict[str, Any]) -> None:
        """データ型情報の表示"""
        st.subheader("📋 データ型情報")
        
        # データ型別カウント
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**データ型別カウント**")
            dtype_counts_df = pd.DataFrame(
                list(dtype_info['dtype_counts'].items()),
                columns=['データ型', '列数']
            )
            st.dataframe(dtype_counts_df, use_container_width=True)
        
        with col2:
            st.write("**列の分類**")
            classification = {
                '数値列': len(dtype_info['numeric_columns']),
                'カテゴリ列': len(dtype_info['categorical_columns']),
                '日時列': len(dtype_info['datetime_columns'])
            }
            for key, value in classification.items():
                st.metric(key, value)
        
        # 全列のデータ型
        st.write("**全列のデータ型**")
        column_dtypes_df = pd.DataFrame(
            list(dtype_info['column_dtypes'].items()),
            columns=['カラム名', 'データ型']
        )
        st.dataframe(column_dtypes_df, use_container_width=True)
    
    def _display_missing_values(self, missing_info: Dict[str, Any]) -> None:
        """欠損値情報の表示"""
        st.subheader("🕳️ 欠損値情報")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総欠損数", f"{missing_info['total_missing']:,}")
        with col2:
            st.metric("欠損率", f"{missing_info['missing_percentage']:.2f}%")
        with col3:
            st.metric("欠損ありカラム数", len(missing_info['columns_with_missing']))
        
        if missing_info['total_missing'] > 0:
            st.write("**欠損値詳細**")
            st.dataframe(missing_info['missing_summary'], use_container_width=True)
        else:
            st.success("✅ 欠損値はありません")
    
    def _display_duplicates(self, duplicate_info: Dict[str, Any]) -> None:
        """重複値情報の表示"""
        st.subheader("🔄 重複値情報")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("重複行数", f"{duplicate_info['duplicate_count']:,}")
        with col2:
            st.metric("重複率", f"{duplicate_info['duplicate_percentage']:.2f}%")
        with col3:
            st.metric("ユニーク行数", f"{duplicate_info['unique_count']:,}")
        
        if duplicate_info['duplicate_count'] > 0:
            st.warning(f"⚠️ {duplicate_info['duplicate_count']}行の重複が検出されました")
        else:
            st.success("✅ 重複行はありません")
    
    def _display_numeric_stats(self, numeric_info: Dict[str, Any]) -> None:
        """数値列統計の表示"""
        st.subheader("🔢 数値列統計")
        
        if 'message' in numeric_info:
            st.info(numeric_info['message'])
            return
        
        st.write(f"**数値列数: {numeric_info['column_count']}**")
        
        # 基本統計量
        st.write("**基本統計量**")
        st.dataframe(numeric_info['basic_stats'], use_container_width=True)
        
        # 追加統計量
        st.write("**追加統計量**")
        st.dataframe(numeric_info['additional_stats'], use_container_width=True)
    
    def _display_categorical_stats(self, categorical_info: Dict[str, Any]) -> None:
        """カテゴリ列統計の表示"""
        st.subheader("📝 カテゴリ列統計")
        
        if 'message' in categorical_info:
            st.info(categorical_info['message'])
            return
        
        st.write(f"**カテゴリ列数: {categorical_info['column_count']}**")
        st.dataframe(categorical_info['categorical_stats'], use_container_width=True)
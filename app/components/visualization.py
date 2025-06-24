import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import japanize_matplotlib
from typing import Dict, Any, List, Optional
from scipy import stats

class Visualization:
    """データ可視化を担当するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.viz_config = config.get('visualization', {})
        
        # matplotlib日本語フォント設定
        plt.style.use('default')
        sns.set_style(self.viz_config.get('style', 'whitegrid'))
        
        # 日本語フォントの設定を強制
        import matplotlib.font_manager as fm
        
        # システムで利用可能な日本語フォントを探す
        font_candidates = [
            'Hiragino Sans',           # macOS
            'Hiragino Kaku Gothic Pro', # macOS
            'Yu Gothic',               # Windows
            'Meiryo',                  # Windows
            'Takao Gothic',            # Linux
            'IPAexGothic',             # Linux
            'Noto Sans CJK JP',        # Universal
            'DejaVu Sans'              # Fallback
        ]
        
        available_font = None
        for font_name in font_candidates:
            if any(font_name in f.name for f in fm.fontManager.ttflist):
                available_font = font_name
                break
        
        if available_font:
            plt.rcParams['font.family'] = available_font
        
        # その他の設定
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け防止
        
        plt.rcParams['figure.figsize'] = (
            self.viz_config.get('figure_size', {}).get('width', 10),
            self.viz_config.get('figure_size', {}).get('height', 6)
        )
        plt.rcParams['figure.dpi'] = self.viz_config.get('dpi', 100)
        
    def create_distribution_plots(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分布プロットを作成"""
        results = {}
        
        # 数値列の分布
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            results['numeric_distributions'] = self._create_numeric_distributions(df, numeric_cols)
        
        # カテゴリ列の分布
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            results['categorical_distributions'] = self._create_categorical_distributions(df, categorical_cols)
        
        return results
    
    def _create_numeric_distributions(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """数値列の分布プロット作成"""
        results = {}
        
        for col in columns:
            if df[col].notna().sum() == 0:
                continue
                
            # データ準備
            data = df[col].dropna()
            
            # 統計情報
            stats_info = {
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'skewness': data.skew(),
                'kurtosis': data.kurtosis(),
                'min': data.min(),
                'max': data.max(),
                'q25': data.quantile(0.25),
                'q75': data.quantile(0.75),
                'iqr': data.quantile(0.75) - data.quantile(0.25)
            }
            
            # 外れ値検出
            outliers = self._detect_outliers(data)
            
            results[col] = {
                'stats': stats_info,
                'outliers': outliers,
                'data_length': len(data)
            }
        
        return results
    
    def _create_categorical_distributions(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """カテゴリ列の分布プロット作成"""
        results = {}
        max_categories = self.viz_config.get('max_categories', 20)
        
        for col in columns:
            if df[col].notna().sum() == 0:
                continue
                
            # データ準備
            value_counts = df[col].value_counts()
            
            # カテゴリ数が多い場合は上位のみ表示
            if len(value_counts) > max_categories:
                value_counts = value_counts.head(max_categories)
                truncated = True
            else:
                truncated = False
            
            results[col] = {
                'value_counts': value_counts,
                'unique_count': df[col].nunique(),
                'truncated': truncated,
                'missing_count': df[col].isnull().sum()
            }
        
        return results
    
    def _detect_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """外れ値を検出"""
        outliers = {}
        
        # IQR法
        q1, q3 = data.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        # Z-score法（閾値3）
        z_scores = np.abs(stats.zscore(data))
        z_outliers = data[z_scores > 3]
        
        # 修正Z-score法
        median = data.median()
        mad = np.median(np.abs(data - median))
        modified_z_scores = 0.6745 * (data - median) / mad
        modified_z_outliers = data[np.abs(modified_z_scores) > 3.5]
        
        outliers = {
            'iqr': {
                'count': len(iqr_outliers),
                'percentage': len(iqr_outliers) / len(data) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'values': iqr_outliers.tolist()
            },
            'zscore': {
                'count': len(z_outliers),
                'percentage': len(z_outliers) / len(data) * 100,
                'values': z_outliers.tolist()
            },
            'modified_zscore': {
                'count': len(modified_z_outliers),
                'percentage': len(modified_z_outliers) / len(data) * 100,
                'values': modified_z_outliers.tolist()
            }
        }
        
        return outliers
    
    def display_numeric_distribution(self, df: pd.DataFrame, column: str) -> None:
        """数値列の分布を表示"""
        if column not in df.columns:
            st.error(f"列 '{column}' が見つかりません")
            return
        
        data = df[column].dropna()
        if len(data) == 0:
            st.warning(f"列 '{column}' にデータがありません")
            return
        
        st.subheader(f"📈 {column} の分布分析")
        
        # 統計情報表示
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均値", f"{data.mean():.3f}")
            st.metric("標準偏差", f"{data.std():.3f}")
        with col2:
            st.metric("中央値", f"{data.median():.3f}")
            st.metric("IQR", f"{data.quantile(0.75) - data.quantile(0.25):.3f}")
        with col3:
            st.metric("最小値", f"{data.min():.3f}")
            st.metric("最大値", f"{data.max():.3f}")
        with col4:
            st.metric("歪度", f"{data.skew():.3f}")
            st.metric("尖度", f"{data.kurtosis():.3f}")
        
        # プロット作成
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # ヒストグラム
        axes[0, 0].hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].axvline(data.mean(), color='red', linestyle='--', label=f'Mean: {data.mean():.3f}')
        axes[0, 0].axvline(data.median(), color='green', linestyle='--', label=f'Median: {data.median():.3f}')
        axes[0, 0].set_title(f'{column} - Histogram')
        axes[0, 0].set_xlabel(column)
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        
        # 箱ひげ図
        box_plot = axes[0, 1].boxplot(data, patch_artist=True)
        box_plot['boxes'][0].set_facecolor('lightblue')
        axes[0, 1].set_title(f'{column} - Box Plot')
        axes[0, 1].set_ylabel(column)
        
        # Q-Qプロット
        stats.probplot(data, dist="norm", plot=axes[1, 0])
        axes[1, 0].set_title(f'{column} - Q-Q Plot (Normal Distribution)')
        
        # 密度プロット
        data.plot.density(ax=axes[1, 1], color='purple', alpha=0.7)
        axes[1, 1].set_title(f'{column} - Density Plot')
        axes[1, 1].set_xlabel(column)
        axes[1, 1].set_ylabel('Density')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 外れ値情報
        outliers = self._detect_outliers(data)
        
        st.subheader("🎯 外れ値検出結果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**IQR法**")
            st.metric("外れ値数", outliers['iqr']['count'])
            st.metric("外れ値率", f"{outliers['iqr']['percentage']:.2f}%")
            if outliers['iqr']['count'] > 0:
                st.write(f"範囲: {outliers['iqr']['lower_bound']:.3f} ～ {outliers['iqr']['upper_bound']:.3f}")
        
        with col2:
            st.write("**Z-score法**")
            st.metric("外れ値数", outliers['zscore']['count'])
            st.metric("外れ値率", f"{outliers['zscore']['percentage']:.2f}%")
            st.write("閾値: |Z| > 3")
        
        with col3:
            st.write("**修正Z-score法**")
            st.metric("外れ値数", outliers['modified_zscore']['count'])
            st.metric("外れ値率", f"{outliers['modified_zscore']['percentage']:.2f}%")
            st.write("閾値: |修正Z| > 3.5")
    
    def display_categorical_distribution(self, df: pd.DataFrame, column: str) -> None:
        """カテゴリ列の分布を表示"""
        if column not in df.columns:
            st.error(f"列 '{column}' が見つかりません")
            return
        
        st.subheader(f"📊 {column} の分布分析")
        
        # 基本情報
        unique_count = df[column].nunique()
        missing_count = df[column].isnull().sum()
        missing_rate = missing_count / len(df) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ユニーク値数", unique_count)
        with col2:
            st.metric("欠損数", missing_count)
        with col3:
            st.metric("欠損率", f"{missing_rate:.2f}%")
        with col4:
            st.metric("データ数", len(df) - missing_count)
        
        # 値の分布
        value_counts = df[column].value_counts()
        max_display = self.viz_config.get('max_categories', 20)
        
        if len(value_counts) > max_display:
            st.warning(f"カテゴリ数が多いため、上位{max_display}個のみ表示します")
            display_counts = value_counts.head(max_display)
            others_count = value_counts.iloc[max_display:].sum()
        else:
            display_counts = value_counts
            others_count = 0
        
        # プロット作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 棒グラフ
        display_counts.plot(kind='bar', ax=ax1, color='lightcoral')
        ax1.set_title(f'{column} - 頻度分布')
        ax1.set_xlabel(column)
        ax1.set_ylabel('頻度')
        ax1.tick_params(axis='x', rotation=45)
        
        # 円グラフ
        if others_count > 0:
            pie_data = list(display_counts.values) + [others_count]
            pie_labels = list(display_counts.index) + ['その他']
        else:
            pie_data = display_counts.values
            pie_labels = display_counts.index
        
        ax2.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title(f'{column} - 割合分布')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 詳細統計
        st.subheader("📋 詳細統計")
        
        stats_df = pd.DataFrame({
            'カテゴリ': display_counts.index,
            '頻度': display_counts.values,
            '割合(%)': (display_counts.values / len(df[column].dropna()) * 100).round(2),
            '累積割合(%)': (display_counts.values / len(df[column].dropna()) * 100).cumsum().round(2)
        })
        
        if others_count > 0:
            others_row = pd.DataFrame({
                'カテゴリ': ['その他'],
                '頻度': [others_count],
                '割合(%)': [others_count / len(df[column].dropna()) * 100],
                '累積割合(%)': [100.0]
            })
            stats_df = pd.concat([stats_df, others_row], ignore_index=True)
        
        st.dataframe(stats_df, use_container_width=True)
    
    def create_plotly_histogram(self, df: pd.DataFrame, column: str) -> go.Figure:
        """Plotlyでインタラクティブなヒストグラムを作成"""
        data = df[column].dropna()
        
        fig = px.histogram(
            x=data,
            nbins=30,
            title=f'{column} - インタラクティブヒストグラム',
            labels={'x': column, 'y': '頻度'}
        )
        
        # 平均線と中央値線を追加
        fig.add_vline(x=data.mean(), line_dash="dash", line_color="red", 
                     annotation_text=f"平均: {data.mean():.3f}")
        fig.add_vline(x=data.median(), line_dash="dash", line_color="green", 
                     annotation_text=f"中央値: {data.median():.3f}")
        
        fig.update_layout(
            xaxis_title=column,
            yaxis_title='頻度',
            showlegend=False
        )
        
        return fig
    
    def create_plotly_box_plot(self, df: pd.DataFrame, column: str) -> go.Figure:
        """Plotlyでインタラクティブな箱ひげ図を作成"""
        data = df[column].dropna()
        
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=data,
            name=column,
            boxpoints='outliers',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title=f'{column} - インタラクティブ箱ひげ図',
            yaxis_title=column
        )
        
        return fig
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import japanize_matplotlib
from typing import Dict, Any, List, Tuple
from scipy.stats import pearsonr, spearmanr, kendalltau

class Correlation:
    """相関分析を担当するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.correlation_config = config.get('correlation', {})
        self.viz_config = config.get('visualization', {})
        
        # matplotlib設定
        plt.style.use('default')
        sns.set_style(self.viz_config.get('style', 'whitegrid'))
    
    def calculate_correlation_matrix(self, df: pd.DataFrame, method: str = None) -> Dict[str, Any]:
        """
        相関行列を計算
        
        Args:
            df: 分析対象のデータフレーム
            method: 相関係数の計算方法（pearson, spearman, kendall）
            
        Returns:
            Dict[str, Any]: 相関分析の結果
        """
        if method is None:
            method = self.correlation_config.get('method', 'pearson')
        
        # 数値列のみを抽出
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {'error': '数値列が見つかりませんでした'}
        
        if len(numeric_df.columns) < 2:
            return {'error': '相関分析には少なくとも2つの数値列が必要です'}
        
        # 欠損値を含む列の処理
        numeric_df = numeric_df.dropna()
        
        if len(numeric_df) == 0:
            return {'error': '有効なデータが不足しています（欠損値除去後）'}
        
        # 相関行列の計算
        correlation_matrix = numeric_df.corr(method=method)
        
        # 強い相関の検出
        threshold = self.correlation_config.get('threshold', 0.5)
        strong_correlations = self._find_strong_correlations(correlation_matrix, threshold)
        
        # p値の計算（pearsonの場合のみ）
        p_values = None
        if method == 'pearson':
            p_values = self._calculate_p_values(numeric_df)
        
        return {
            'correlation_matrix': correlation_matrix,
            'strong_correlations': strong_correlations,
            'p_values': p_values,
            'method': method,
            'columns': numeric_df.columns.tolist(),
            'data_shape': numeric_df.shape
        }
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float) -> List[Dict]:
        """強い相関を検出"""
        strong_corr = []
        
        # 上三角行列のみを確認（重複を避ける）
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corr.append({
                        'variable1': corr_matrix.columns[i],
                        'variable2': corr_matrix.columns[j],
                        'correlation': corr_value,
                        'strength': self._categorize_correlation_strength(abs(corr_value))
                    })
        
        # 相関の強さでソート
        strong_corr.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return strong_corr
    
    def _categorize_correlation_strength(self, abs_corr: float) -> str:
        """相関の強さを分類"""
        if abs_corr >= 0.9:
            return '非常に強い'
        elif abs_corr >= 0.7:
            return '強い'
        elif abs_corr >= 0.5:
            return '中程度'
        elif abs_corr >= 0.3:
            return '弱い'
        else:
            return '非常に弱い'
    
    def _calculate_p_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """p値を計算（pearson相関）"""
        columns = df.columns
        p_values = np.zeros((len(columns), len(columns)))
        
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i == j:
                    p_values[i, j] = 0
                else:
                    _, p_val = pearsonr(df[col1].dropna(), df[col2].dropna())
                    p_values[i, j] = p_val
        
        return pd.DataFrame(p_values, columns=columns, index=columns)
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame, method: str) -> plt.Figure:
        """相関ヒートマップを作成"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # ヒートマップ作成
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(
            correlation_matrix,
            mask=mask,
            annot=True,
            cmap='RdBu_r',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
            fmt='.3f'
        )
        
        ax.set_title(f'相関ヒートマップ ({method})', fontsize=16, pad=20)
        plt.tight_layout()
        
        return fig
    
    def create_interactive_heatmap(self, correlation_matrix: pd.DataFrame, method: str) -> go.Figure:
        """インタラクティブ相関ヒートマップを作成"""
        # 上三角マスク
        mask = np.triu(np.ones_like(correlation_matrix))
        masked_corr = correlation_matrix.mask(mask.astype(bool))
        
        fig = px.imshow(
            masked_corr,
            color_continuous_scale='RdBu_r',
            aspect='auto',
            title=f'相関ヒートマップ ({method})',
            labels={'color': '相関係数'}
        )
        
        fig.update_layout(
            title_x=0.5,
            width=800,
            height=600
        )
        
        return fig
    
    def create_scatter_matrix(self, df: pd.DataFrame, selected_columns: List[str] = None) -> plt.Figure:
        """散布図マトリックスを作成"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if selected_columns:
            available_columns = [col for col in selected_columns if col in numeric_df.columns]
            if available_columns:
                numeric_df = numeric_df[available_columns]
        
        # 列数が多い場合は制限
        max_cols = 6
        if len(numeric_df.columns) > max_cols:
            numeric_df = numeric_df.iloc[:, :max_cols]
            st.warning(f"列数が多いため、最初の{max_cols}列のみ表示します")
        
        # 散布図マトリックス作成
        fig = plt.figure(figsize=(15, 15))
        
        # サブプロット作成
        n_cols = len(numeric_df.columns)
        
        for i, col1 in enumerate(numeric_df.columns):
            for j, col2 in enumerate(numeric_df.columns):
                ax = plt.subplot(n_cols, n_cols, i * n_cols + j + 1)
                
                if i == j:
                    # 対角線はヒストグラム
                    ax.hist(numeric_df[col1].dropna(), bins=20, alpha=0.7, color='skyblue')
                    ax.set_title(col1)
                else:
                    # 散布図
                    valid_data = numeric_df[[col1, col2]].dropna()
                    if len(valid_data) > 0:
                        ax.scatter(valid_data[col2], valid_data[col1], alpha=0.6, s=20)
                        
                        # 回帰線を追加
                        if len(valid_data) > 1:
                            z = np.polyfit(valid_data[col2], valid_data[col1], 1)
                            p = np.poly1d(z)
                            ax.plot(valid_data[col2], p(valid_data[col2]), "r--", alpha=0.8)
                
                # ラベル設定
                if i == n_cols - 1:
                    ax.set_xlabel(col2)
                if j == 0:
                    ax.set_ylabel(col1)
                
                # ティック調整
                ax.tick_params(labelsize=8)
        
        plt.tight_layout()
        return fig
    
    def display_correlation_analysis(self, df: pd.DataFrame) -> None:
        """相関分析をStreamlitで表示"""
        st.header("🔗 相関分析")
        
        # 相関係数の選択
        method = st.selectbox(
            "相関係数の種類を選択",
            ['pearson', 'spearman', 'kendall'],
            help="""
            - Pearson: 線形関係を測定
            - Spearman: 順位相関（非線形関係も検出）
            - Kendall: 順位相関（外れ値に頑健）
            """
        )
        
        with st.spinner("相関分析を実行中..."):
            correlation_results = self.calculate_correlation_matrix(df, method)
        
        if 'error' in correlation_results:
            st.error(f"❌ {correlation_results['error']}")
            return
        
        correlation_matrix = correlation_results['correlation_matrix']
        strong_correlations = correlation_results['strong_correlations']
        
        # 基本情報表示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("分析対象列数", len(correlation_results['columns']))
        with col2:
            st.metric("データ数", correlation_results['data_shape'][0])
        with col3:
            threshold = self.correlation_config.get('threshold', 0.5)
            st.metric(f"強い相関数（|r|≥{threshold}）", len(strong_correlations))
        
        # タブで結果を整理
        tab1, tab2, tab3, tab4 = st.tabs([
            "相関ヒートマップ", "強い相関", "散布図マトリックス", "詳細データ"
        ])
        
        with tab1:
            self._display_heatmap_tab(correlation_matrix, method)
        
        with tab2:
            self._display_strong_correlations_tab(strong_correlations)
        
        with tab3:
            self._display_scatter_matrix_tab(df, correlation_results['columns'])
        
        with tab4:
            self._display_detailed_data_tab(correlation_matrix, correlation_results.get('p_values'))
    
    def _display_heatmap_tab(self, correlation_matrix: pd.DataFrame, method: str) -> None:
        """ヒートマップタブの表示"""
        st.subheader("🌡️ 相関ヒートマップ")
        
        plot_type = st.radio(
            "プロットタイプ",
            ["標準ヒートマップ", "インタラクティブヒートマップ"],
            horizontal=True
        )
        
        if plot_type == "標準ヒートマップ":
            fig = self.create_correlation_heatmap(correlation_matrix, method)
            st.pyplot(fig)
        else:
            fig = self.create_interactive_heatmap(correlation_matrix, method)
            st.plotly_chart(fig, use_container_width=True)
    
    def _display_strong_correlations_tab(self, strong_correlations: List[Dict]) -> None:
        """強い相関タブの表示"""
        st.subheader("💪 強い相関関係")
        
        if not strong_correlations:
            st.info("強い相関関係は検出されませんでした。")
            return
        
        # 強い相関をデータフレームで表示
        strong_corr_df = pd.DataFrame(strong_correlations)
        strong_corr_df['相関係数'] = strong_corr_df['correlation'].round(3)
        strong_corr_df['相関の強さ'] = strong_corr_df['strength']
        strong_corr_df['変数1'] = strong_corr_df['variable1']
        strong_corr_df['変数2'] = strong_corr_df['variable2']
        
        display_df = strong_corr_df[['変数1', '変数2', '相関係数', '相関の強さ']]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # 相関の分布
        st.subheader("📊 相関の分布")
        
        corr_values = [abs(corr['correlation']) for corr in strong_correlations]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(corr_values, bins=15, alpha=0.7, color='lightcoral', edgecolor='black')
        ax.set_xlabel('相関係数の絶対値')
        ax.set_ylabel('頻度')
        ax.set_title('強い相関の分布')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
    
    def _display_scatter_matrix_tab(self, df: pd.DataFrame, columns: List[str]) -> None:
        """散布図マトリックスタブの表示"""
        st.subheader("🔍 散布図マトリックス")
        
        # 列選択（最大6列まで）
        max_display = 6
        if len(columns) > max_display:
            st.warning(f"列数が多いため、最大{max_display}列まで選択可能です")
            selected_columns = st.multiselect(
                "表示する列を選択（最大6列）",
                columns,
                default=columns[:max_display]
            )
            
            if len(selected_columns) > max_display:
                st.warning(f"選択できるのは最大{max_display}列です")
                selected_columns = selected_columns[:max_display]
        else:
            selected_columns = columns
        
        if len(selected_columns) >= 2:
            with st.spinner("散布図マトリックスを作成中..."):
                fig = self.create_scatter_matrix(df, selected_columns)
                st.pyplot(fig)
        else:
            st.info("散布図マトリックスには少なくとも2列が必要です")
    
    def _display_detailed_data_tab(self, correlation_matrix: pd.DataFrame, p_values: pd.DataFrame = None) -> None:
        """詳細データタブの表示"""
        st.subheader("📋 詳細な相関データ")
        
        # 相関行列の表示
        st.write("**相関行列**")
        st.dataframe(correlation_matrix.round(3), use_container_width=True)
        
        # p値の表示（pearsonの場合のみ）
        if p_values is not None:
            st.write("**p値（有意性検定）**")
            st.dataframe(p_values.round(4), use_container_width=True)
            st.caption("p < 0.05 で統計的に有意")
        
        # ダウンロードボタン
        csv = correlation_matrix.to_csv()
        st.download_button(
            label="📥 相関行列をCSVでダウンロード",
            data=csv,
            file_name="correlation_matrix.csv",
            mime="text/csv"
        )
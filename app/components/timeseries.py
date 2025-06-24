import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import japanize_matplotlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

class TimeSeries:
    """時系列分析を担当するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.viz_config = config.get('visualization', {})
        
        # matplotlib日本語フォント設定
        plt.style.use('default')
        sns.set_style(self.viz_config.get('style', 'whitegrid'))
        
        # 日本語フォントの設定を強制
        import matplotlib.font_manager as fm
        
        font_candidates = [
            'Hiragino Sans', 'Hiragino Kaku Gothic Pro', 'Yu Gothic', 
            'Meiryo', 'Takao Gothic', 'IPAexGothic', 'Noto Sans CJK JP', 'DejaVu Sans'
        ]
        
        available_font = None
        for font_name in font_candidates:
            if any(font_name in f.name for f in fm.fontManager.ttflist):
                available_font = font_name
                break
        
        if available_font:
            plt.rcParams['font.family'] = available_font
        
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.unicode_minus'] = False
    
    def detect_datetime_columns(self, df: pd.DataFrame) -> List[str]:
        """日付時刻列を検出"""
        datetime_cols = []
        
        # 既にdatetime型の列
        datetime_cols.extend(df.select_dtypes(include=['datetime64']).columns.tolist())
        
        # object型の列で日付らしいものを検出
        for col in df.select_dtypes(include=['object']).columns:
            # カラム名で判定
            if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', '日付', '時刻']):
                datetime_cols.append(col)
                continue
                
            # データ内容で判定
            valid_data = df[col].dropna()
            valid_data = valid_data[valid_data != '']
            valid_data = valid_data[valid_data != 'None']
            valid_data = valid_data[valid_data != 'null']
            
            if len(valid_data) > 0:
                sample_size = min(50, len(valid_data))
                sample_data = valid_data.iloc[:sample_size]
                
                try:
                    # pandas.to_datetimeで変換を試行
                    converted = pd.to_datetime(sample_data, errors='coerce')
                    success_rate = converted.notna().sum() / len(sample_data)
                    
                    # 60%以上変換できたら日付列と判定（さらに閾値を下げる）
                    if success_rate >= 0.6:
                        datetime_cols.append(col)
                except:
                    continue
        
        return list(set(datetime_cols))  # 重複除去
    
    def prepare_timeseries_data(self, df: pd.DataFrame, date_col: str, value_cols: List[str]) -> pd.DataFrame:
        """時系列データの準備"""
        # 必要な列のみ抽出
        columns_to_use = [date_col] + value_cols
        ts_df = df[columns_to_use].copy()
        
        # 日付列を変換
        if ts_df[date_col].dtype != 'datetime64[ns]':
            ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors='coerce')
        
        # 欠損値を含む行を削除
        ts_df = ts_df.dropna()
        
        # 日付でソート
        ts_df = ts_df.sort_values(date_col).reset_index(drop=True)
        
        return ts_df
    
    def calculate_moving_averages(self, data: pd.Series, windows: List[int]) -> Dict[str, pd.Series]:
        """移動平均を計算"""
        moving_averages = {}
        for window in windows:
            if len(data) >= window:
                moving_averages[f'MA_{window}'] = data.rolling(window=window).mean()
        return moving_averages
    
    def detect_trend(self, df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        """トレンド分析"""
        # 数値データに変換（日付を数値として扱う）
        df_trend = df[[date_col, value_col]].dropna().copy()
        
        # 日付を数値に変換（エポック時間）
        df_trend['date_numeric'] = pd.to_datetime(df_trend[date_col]).astype('int64') // 10**9
        
        X = df_trend[['date_numeric']]
        y = df_trend[value_col]
        
        if len(X) < 2:
            return {'error': 'データが不足しています'}
        
        # 線形回帰でトレンドを計算
        lr = LinearRegression()
        lr.fit(X, y)
        
        # トレンドの傾き
        slope = lr.coef_[0]
        
        # 決定係数
        r2_score = lr.score(X, y)
        
        # トレンドの判定
        if abs(slope) < 1e-10:
            trend_direction = 'Flat'
        elif slope > 0:
            trend_direction = 'Increasing'
        else:
            trend_direction = 'Decreasing'
        
        return {
            'slope': slope,
            'r2_score': r2_score,
            'trend_direction': trend_direction,
            'model': lr
        }
    
    def predict_future_values(self, df: pd.DataFrame, date_col: str, value_col: str, 
                            future_periods: int = 30) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """将来値の予測"""
        df_pred = df[[date_col, value_col]].dropna().copy()
        
        if len(df_pred) < 5:
            return None, {'error': 'データが不足しています（最低5個必要）'}
        
        # 日付を数値に変換
        df_pred['date_numeric'] = pd.to_datetime(df_pred[date_col]).astype('int64') // 10**9
        
        X = df_pred[['date_numeric']]
        y = df_pred[value_col]
        
        # 多項式回帰（2次）でより良い予測を試行
        try:
            poly_model = Pipeline([
                ('poly', PolynomialFeatures(degree=2)),
                ('linear', LinearRegression())
            ])
            poly_model.fit(X, y)
            
            # 線形回帰も試行
            linear_model = LinearRegression()
            linear_model.fit(X, y)
            
            # どちらが良いかR²スコアで判定
            poly_score = poly_model.score(X, y)
            linear_score = linear_model.score(X, y)
            
            if poly_score > linear_score and poly_score > 0.3:
                model = poly_model
                model_type = 'polynomial'
                score = poly_score
            else:
                model = linear_model
                model_type = 'linear'
                score = linear_score
        
        except:
            # エラーの場合は線形回帰
            model = LinearRegression()
            model.fit(X, y)
            model_type = 'linear'
            score = model.score(X, y)
        
        # 将来の日付を生成
        last_date = pd.to_datetime(df_pred[date_col]).max()
        freq = self._estimate_frequency(df_pred[date_col])
        
        # 頻度に応じた日付生成
        if freq == 'D':
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=future_periods,
                freq='D'
            )
        elif freq == 'W':
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(weeks=1),
                periods=future_periods,
                freq='W'
            )
        elif freq == 'M':
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(months=1),
                periods=future_periods,
                freq='M'
            )
        elif freq == 'Q':
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(months=3),
                periods=future_periods,
                freq='Q'
            )
        elif freq == 'Y':
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(years=1),
                periods=future_periods,
                freq='Y'
            )
        else:
            # デフォルトは日次
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=future_periods,
                freq='D'
            )
        
        # 将来の数値データ
        future_numeric = future_dates.astype('int64') // 10**9
        
        # 予測実行
        predictions = model.predict(future_numeric.values.reshape(-1, 1))
        
        # 予測結果をデータフレームに
        future_df = pd.DataFrame({
            date_col: future_dates,
            value_col: predictions,
            'is_prediction': True
        })
        
        # 実際のデータに予測フラグを追加
        df_pred['is_prediction'] = False
        
        # 結合
        result_df = pd.concat([
            df_pred[[date_col, value_col, 'is_prediction']],
            future_df
        ], ignore_index=True)
        
        return result_df, {
            'model_type': model_type,
            'r2_score': score,
            'future_periods': future_periods,
            'model': model
        }
    
    def _estimate_frequency(self, date_series: pd.Series) -> str:
        """データの頻度を推定"""
        date_series = pd.to_datetime(date_series).sort_values()
        
        if len(date_series) < 2:
            return 'D'  # デフォルトは日次
        
        # 日付間隔の中央値を計算
        intervals = date_series.diff().dropna()
        median_interval = intervals.median()
        
        # 頻度を判定
        if median_interval <= timedelta(days=1):
            return 'D'  # 日次
        elif median_interval <= timedelta(days=7):
            return 'W'  # 週次
        elif median_interval <= timedelta(days=31):
            return 'M'  # 月次
        elif median_interval <= timedelta(days=92):
            return 'Q'  # 四半期
        else:
            return 'Y'  # 年次
    
    def create_timeseries_plot(self, df: pd.DataFrame, date_col: str, value_col: str, 
                              moving_averages: Dict[str, pd.Series] = None,
                              predictions: pd.DataFrame = None) -> plt.Figure:
        """時系列プロットを作成"""
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 実際のデータをプロット
        ax.plot(pd.to_datetime(df[date_col]), df[value_col], 
               label='Actual Values', color='blue', linewidth=2)
        
        # 移動平均をプロット
        if moving_averages:
            colors = ['red', 'green', 'orange', 'purple']
            for i, (ma_name, ma_values) in enumerate(moving_averages.items()):
                color = colors[i % len(colors)]
                ax.plot(pd.to_datetime(df[date_col]), ma_values, 
                       label=ma_name, color=color, linestyle='--', alpha=0.7)
        
        # 予測値をプロット
        if predictions is not None:
            pred_data = predictions[predictions['is_prediction'] == True]
            if len(pred_data) > 0:
                ax.plot(pd.to_datetime(pred_data[date_col]), pred_data[value_col],
                       label='Predictions', color='red', linestyle=':', linewidth=2, alpha=0.8)
        
        ax.set_title(f'Time Series Analysis: {value_col}')
        ax.set_xlabel('Date')
        ax.set_ylabel(value_col)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # x軸の日付フォーマット調整
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return fig
    
    def create_interactive_timeseries_plot(self, df: pd.DataFrame, date_col: str, value_col: str,
                                         moving_averages: Dict[str, pd.Series] = None,
                                         predictions: pd.DataFrame = None) -> go.Figure:
        """インタラクティブ時系列プロットを作成"""
        fig = go.Figure()
        
        # 実際のデータ
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df[date_col]),
            y=df[value_col],
            mode='lines',
            name='Actual Values',
            line=dict(color='blue', width=2)
        ))
        
        # 移動平均
        if moving_averages:
            colors = ['red', 'green', 'orange', 'purple']
            for i, (ma_name, ma_values) in enumerate(moving_averages.items()):
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(df[date_col]),
                    y=ma_values,
                    mode='lines',
                    name=ma_name,
                    line=dict(color=colors[i % len(colors)], width=1, dash='dash')
                ))
        
        # 予測値
        if predictions is not None:
            pred_data = predictions[predictions['is_prediction'] == True]
            if len(pred_data) > 0:
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(pred_data[date_col]),
                    y=pred_data[value_col],
                    mode='lines',
                    name='Predictions',
                    line=dict(color='red', width=2, dash='dot')
                ))
        
        fig.update_layout(
            title=f'Interactive Time Series Analysis: {value_col}',
            xaxis_title='Date',
            yaxis_title=value_col,
            hovermode='x unified',
            width=1000,
            height=600
        )
        
        return fig
    
    def analyze_periodicity(self, df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        """周期性の簡単な分析"""
        df_period = df[[date_col, value_col]].dropna().copy()
        df_period[date_col] = pd.to_datetime(df_period[date_col])
        
        # 月別統計
        df_period['month'] = df_period[date_col].dt.month
        monthly_stats = df_period.groupby('month')[value_col].agg(['mean', 'std', 'count'])
        
        # 曜日別統計（データが日次の場合）
        df_period['weekday'] = df_period[date_col].dt.day_name()
        weekday_stats = df_period.groupby('weekday')[value_col].agg(['mean', 'std', 'count'])
        
        # 年別統計
        df_period['year'] = df_period[date_col].dt.year
        yearly_stats = df_period.groupby('year')[value_col].agg(['mean', 'std', 'count'])
        
        return {
            'monthly_stats': monthly_stats,
            'weekday_stats': weekday_stats,
            'yearly_stats': yearly_stats
        }
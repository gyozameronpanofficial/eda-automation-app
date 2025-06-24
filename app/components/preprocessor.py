import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from scipy import stats

class Preprocessor:
    """前処理を担当するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.preprocessing_config = config.get('preprocessing', {})
        self.processing_history = []
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データの概要を取得"""
        return {
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            'duplicate_rows': df.duplicated().sum()
        }
    
    def detect_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """欠損値の詳細分析"""
        missing_info = {}
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_info[col] = {
                    'count': missing_count,
                    'percentage': (missing_count / len(df)) * 100,
                    'dtype': str(df[col].dtype),
                    'sample_values': df[col].dropna().head(5).tolist()
                }
        
        return missing_info
    
    def detect_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> Dict[str, Any]:
        """外れ値の検出"""
        if column not in df.columns:
            return {'error': f'列 {column} が見つかりません'}
        
        if not pd.api.types.is_numeric_dtype(df[column]):
            return {'error': f'列 {column} は数値型ではありません'}
        
        data = df[column].dropna()
        if len(data) == 0:
            return {'error': f'列 {column} に有効なデータがありません'}
        
        outlier_indices = []
        bounds = {}
        
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_indices = data[(data < lower_bound) | (data > upper_bound)].index.tolist()
            bounds = {'lower': lower_bound, 'upper': upper_bound}
            
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            outlier_indices = data[z_scores > 3].index.tolist()
            bounds = {'threshold': 3}
            
        elif method == 'modified_zscore':
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z_scores = 0.6745 * (data - median) / mad
            outlier_indices = data[np.abs(modified_z_scores) > 3.5].index.tolist()
            bounds = {'threshold': 3.5}
        
        return {
            'outlier_indices': outlier_indices,
            'outlier_count': len(outlier_indices),
            'outlier_percentage': (len(outlier_indices) / len(data)) * 100,
            'bounds': bounds,
            'method': method
        }
    
    def handle_missing_values(self, df: pd.DataFrame, column: str, method: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """欠損値処理"""
        df_processed = df.copy()
        original_missing = df[column].isnull().sum()
        
        operation_info = {
            'operation': 'missing_value_handling',
            'column': column,
            'method': method,
            'original_missing_count': original_missing,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if method == '削除':
            df_processed = df_processed.dropna(subset=[column])
            operation_info['rows_removed'] = len(df) - len(df_processed)
            
        elif method == '平均値補完':
            if pd.api.types.is_numeric_dtype(df[column]):
                mean_value = df[column].mean()
                df_processed[column] = df_processed[column].fillna(mean_value)
                operation_info['fill_value'] = mean_value
            else:
                return df, {'error': '平均値補完は数値列にのみ適用できます'}
                
        elif method == '中央値補完':
            if pd.api.types.is_numeric_dtype(df[column]):
                median_value = df[column].median()
                df_processed[column] = df_processed[column].fillna(median_value)
                operation_info['fill_value'] = median_value
            else:
                return df, {'error': '中央値補完は数値列にのみ適用できます'}
                
        elif method == '最頻値補完':
            mode_value = df[column].mode()
            if len(mode_value) > 0:
                df_processed[column] = df_processed[column].fillna(mode_value.iloc[0])
                operation_info['fill_value'] = mode_value.iloc[0]
            else:
                return df, {'error': '最頻値が見つかりませんでした'}
                
        elif method == '前方補完':
            df_processed[column] = df_processed[column].fillna(method='ffill')
            
        elif method == '後方補完':
            df_processed[column] = df_processed[column].fillna(method='bfill')
            
        elif method == 'カスタム値':
            # この場合は別途カスタム値を指定する必要がある
            return df, {'error': 'カスタム値が指定されていません'}
        
        operation_info['final_missing_count'] = df_processed[column].isnull().sum()
        operation_info['processed_count'] = original_missing - operation_info['final_missing_count']
        
        return df_processed, operation_info
    
    def handle_missing_values_custom(self, df: pd.DataFrame, column: str, custom_value: Any) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """カスタム値での欠損値補完"""
        df_processed = df.copy()
        original_missing = df[column].isnull().sum()
        
        # データ型に応じてカスタム値を変換
        try:
            if pd.api.types.is_numeric_dtype(df[column]):
                custom_value = float(custom_value)
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                custom_value = pd.to_datetime(custom_value)
            else:
                custom_value = str(custom_value)
        except:
            return df, {'error': f'カスタム値 "{custom_value}" は列 "{column}" の型に適合しません'}
        
        df_processed[column] = df_processed[column].fillna(custom_value)
        
        operation_info = {
            'operation': 'missing_value_handling',
            'column': column,
            'method': 'カスタム値',
            'fill_value': custom_value,
            'original_missing_count': original_missing,
            'final_missing_count': df_processed[column].isnull().sum(),
            'processed_count': original_missing,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return df_processed, operation_info
    
    def remove_outliers(self, df: pd.DataFrame, column: str, method: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """外れ値除去"""
        outlier_info = self.detect_outliers(df, column, method)
        
        if 'error' in outlier_info:
            return df, outlier_info
        
        df_processed = df.copy()
        outlier_indices = outlier_info['outlier_indices']
        
        # 外れ値の行を除去
        df_processed = df_processed.drop(outlier_indices)
        
        operation_info = {
            'operation': 'outlier_removal',
            'column': column,
            'method': method,
            'outlier_count': len(outlier_indices),
            'rows_removed': len(outlier_indices),
            'original_shape': df.shape,
            'final_shape': df_processed.shape,
            'bounds': outlier_info['bounds'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return df_processed, operation_info
    
    def convert_data_type(self, df: pd.DataFrame, column: str, target_type: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """データ型変換"""
        df_processed = df.copy()
        original_type = str(df[column].dtype)
        conversion_errors = 0
        
        operation_info = {
            'operation': 'data_type_conversion',
            'column': column,
            'original_type': original_type,
            'target_type': target_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            if target_type == 'int64':
                df_processed[column] = pd.to_numeric(df_processed[column], errors='coerce').astype('Int64')
                conversion_errors = df_processed[column].isnull().sum() - df[column].isnull().sum()
                
            elif target_type == 'float64':
                df_processed[column] = pd.to_numeric(df_processed[column], errors='coerce')
                conversion_errors = df_processed[column].isnull().sum() - df[column].isnull().sum()
                
            elif target_type == 'object':
                df_processed[column] = df_processed[column].astype(str)
                
            elif target_type == 'datetime64[ns]':
                df_processed[column] = pd.to_datetime(df_processed[column], errors='coerce')
                conversion_errors = df_processed[column].isnull().sum() - df[column].isnull().sum()
                
            elif target_type == 'category':
                df_processed[column] = df_processed[column].astype('category')
                
            elif target_type == 'bool':
                # ブール型への変換
                df_processed[column] = df_processed[column].astype(bool)
                
            else:
                return df, {'error': f'サポートされていないデータ型: {target_type}'}
                
        except Exception as e:
            return df, {'error': f'データ型変換に失敗しました: {str(e)}'}
        
        operation_info['final_type'] = str(df_processed[column].dtype)
        operation_info['conversion_errors'] = conversion_errors
        
        return df_processed, operation_info
    
    def add_operation_to_history(self, operation_info: Dict[str, Any]):
        """操作履歴に追加"""
        self.processing_history.append(operation_info)
    
    def get_processing_history(self) -> List[Dict[str, Any]]:
        """処理履歴を取得"""
        return self.processing_history
    
    def clear_history(self):
        """履歴をクリア"""
        self.processing_history = []
    
    def undo_last_operation(self, df_history: List[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """最後の操作を取り消し"""
        if len(self.processing_history) > 0 and len(df_history) > 1:
            self.processing_history.pop()
            return df_history[-2]  # 一つ前の状態に戻る
        return None
    
    def get_column_info(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """列の詳細情報を取得"""
        if column not in df.columns:
            return {'error': f'列 {column} が見つかりません'}
        
        col_data = df[column]
        
        info = {
            'name': column,
            'dtype': str(col_data.dtype),
            'non_null_count': col_data.count(),
            'null_count': col_data.isnull().sum(),
            'unique_count': col_data.nunique(),
            'memory_usage': col_data.memory_usage(deep=True)
        }
        
        # 数値型の場合の統計情報
        if pd.api.types.is_numeric_dtype(col_data):
            info.update({
                'mean': col_data.mean(),
                'median': col_data.median(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'q25': col_data.quantile(0.25),
                'q75': col_data.quantile(0.75)
            })
        
        # カテゴリ型の場合
        elif pd.api.types.is_categorical_dtype(col_data) or col_data.dtype == 'object':
            value_counts = col_data.value_counts().head(10)
            info.update({
                'top_values': value_counts.to_dict(),
                'most_frequent': col_data.mode().iloc[0] if len(col_data.mode()) > 0 else None
            })
        
        return info
    
    def compare_dataframes(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> Dict[str, Any]:
        """前処理前後のデータフレームを比較"""
        comparison = {
            'shape_before': df_before.shape,
            'shape_after': df_after.shape,
            'rows_changed': df_before.shape[0] - df_after.shape[0],
            'memory_before': df_before.memory_usage(deep=True).sum() / 1024 / 1024,
            'memory_after': df_after.memory_usage(deep=True).sum() / 1024 / 1024
        }
        
        # 列ごとの変化
        column_changes = {}
        for col in df_before.columns:
            if col in df_after.columns:
                before_nulls = df_before[col].isnull().sum()
                after_nulls = df_after[col].isnull().sum()
                column_changes[col] = {
                    'null_count_before': before_nulls,
                    'null_count_after': after_nulls,
                    'null_count_change': before_nulls - after_nulls,
                    'dtype_before': str(df_before[col].dtype),
                    'dtype_after': str(df_after[col].dtype),
                    'dtype_changed': str(df_before[col].dtype) != str(df_after[col].dtype)
                }
        
        comparison['column_changes'] = column_changes
        return comparison
import pandas as pd
import chardet
import streamlit as st
from typing import Optional, Dict, Any
import io

class FileHandler:
    """ファイル読み込みと前処理を担当するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.general_config = config.get('general', {})
        self.data_types_config = config.get('data_types', {})
    
    def load_file(self, uploaded_file) -> pd.DataFrame:
        """
        アップロードされたファイルを読み込む
        
        Args:
            uploaded_file: Streamlitのファイルアップローダーオブジェクト
            
        Returns:
            pd.DataFrame: 読み込まれたデータフレーム
            
        Raises:
            Exception: ファイル読み込みエラー
        """
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                return self._load_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return self._load_excel(uploaded_file)
            else:
                raise ValueError(f"サポートされていないファイル形式: {file_extension}")
                
        except Exception as e:
            raise Exception(f"ファイル読み込みエラー: {str(e)}")
    
    def _load_csv(self, uploaded_file) -> pd.DataFrame:
        """CSVファイルを読み込む"""
        # バイトデータを取得
        bytes_data = uploaded_file.read()
        
        # 文字エンコーディングを自動検出
        encoding = self._detect_encoding(bytes_data)
        
        # 区切り文字を自動検出
        delimiter = self._detect_delimiter(bytes_data, encoding)
        
        # CSVを読み込み
        df = pd.read_csv(
            io.BytesIO(bytes_data),
            encoding=encoding,
            delimiter=delimiter,
            low_memory=False,
            na_values=['None', 'null', 'NULL', '', 'nan', 'NaN']  # より多くのNone値を認識
        )
        
        # データ型を自動判定
        if self.data_types_config.get('auto_detect', True):
            df = self._auto_detect_dtypes(df)
        
        return df
    
    def _load_excel(self, uploaded_file) -> pd.DataFrame:
        """Excelファイルを読み込む"""
        # Excelファイルを読み込み
        excel_file = pd.ExcelFile(uploaded_file)
        
        # シートが複数ある場合は最初のシートを使用
        sheet_name = excel_file.sheet_names[0]
        
        if len(excel_file.sheet_names) > 1:
            st.warning(f"複数のシートが検出されました。'{sheet_name}'シートを使用します。")
        
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        
        # データ型を自動判定
        if self.data_types_config.get('auto_detect', True):
            df = self._auto_detect_dtypes(df)
        
        return df
    
    def _detect_encoding(self, bytes_data: bytes) -> str:
        """文字エンコーディングを自動検出"""
        # サンプルデータで検出（大容量ファイル対応）
        sample_size = min(10000, len(bytes_data))
        sample_data = bytes_data[:sample_size]
        
        detected = chardet.detect(sample_data)
        encoding = detected['encoding']
        
        # 一般的なエンコーディングにフォールバック
        if encoding is None or detected['confidence'] < 0.7:
            encodings_to_try = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
            for enc in encodings_to_try:
                try:
                    sample_data.decode(enc)
                    encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
        
        return encoding or 'utf-8'
    
    def _detect_delimiter(self, bytes_data: bytes, encoding: str) -> str:
        """区切り文字を自動検出"""
        # サンプルデータを文字列に変換
        sample_size = min(1000, len(bytes_data))
        try:
            sample_text = bytes_data[:sample_size].decode(encoding)
        except:
            sample_text = bytes_data[:sample_size].decode('utf-8', errors='ignore')
        
        # 最初の数行を取得
        lines = sample_text.split('\n')[:5]
        
        # 区切り文字の候補
        delimiters = [',', '\t', ';', '|']
        delimiter_counts = {}
        
        for delimiter in delimiters:
            counts = []
            for line in lines:
                if line.strip():
                    counts.append(line.count(delimiter))
            
            # 各行で区切り文字の数が一致している場合、そのスコアを高く評価
            if counts and len(set(counts)) == 1 and counts[0] > 0:
                delimiter_counts[delimiter] = counts[0] * 10
            elif counts:
                delimiter_counts[delimiter] = sum(counts)
            else:
                delimiter_counts[delimiter] = 0
        
        # 最も多く使われている区切り文字を選択
        best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        
        return best_delimiter if delimiter_counts[best_delimiter] > 0 else ','
    
    def _auto_detect_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """データ型を自動判定して変換"""
        df_converted = df.copy()
        
        for column in df_converted.columns:
            # 日付時刻型の判定
            if self._is_datetime_column(df_converted[column]):
                df_converted[column] = self._convert_to_datetime(df_converted[column])
            
            # カテゴリ型の判定
            elif self._is_categorical_column(df_converted[column]):
                df_converted[column] = df_converted[column].astype('category')
            
            # 数値型の判定・変換
            elif self._is_numeric_column(df_converted[column]):
                df_converted[column] = pd.to_numeric(df_converted[column], errors='coerce')
        
        return df_converted
    
    def _is_datetime_column(self, series: pd.Series) -> bool:
        """列が日付時刻型かどうか判定"""
        if series.dtype == 'object':
            # Noneや空文字列を除外
            valid_data = series.dropna()
            valid_data = valid_data[valid_data != '']
            valid_data = valid_data[valid_data != 'None']
            
            if len(valid_data) == 0:
                return False
            
            # サンプルデータで日付フォーマットをチェック
            sample_size = min(100, len(valid_data))
            sample_data = valid_data.iloc[:sample_size]
            
            # まず指定フォーマットで試行
            for datetime_format in self.data_types_config.get('datetime_formats', []):
                try:
                    pd.to_datetime(sample_data, format=datetime_format, errors='raise')
                    return True
                except:
                    continue
            
            # フォーマット指定なしでの変換も試行
            try:
                converted = pd.to_datetime(sample_data, errors='coerce')
                # 変換成功率が70%以上なら日付型と判定（閾値を下げる）
                success_rate = converted.notna().sum() / len(sample_data)
                return success_rate >= 0.7
            except:
                return False
        
        return False
    
    def _is_categorical_column(self, series: pd.Series) -> bool:
        """列がカテゴリ型かどうか判定"""
        if series.dtype == 'object':
            unique_count = series.nunique()
            total_count = len(series)
            threshold = self.data_types_config.get('categorical_threshold', 10)
            
            # ユニーク値が閾値以下、かつ全体の50%以下の場合はカテゴリ型
            return unique_count <= threshold and unique_count <= total_count * 0.5
        
        return False
    
    def _is_numeric_column(self, series: pd.Series) -> bool:
        """列が数値型かどうか判定"""
        if series.dtype in ['int64', 'float64']:
            return True
        
        if series.dtype == 'object':
            # サンプルデータで数値変換をテスト
            sample_size = min(100, len(series.dropna()))
            if sample_size == 0:
                return False
            
            sample_data = series.dropna().iloc[:sample_size]
            
            try:
                converted = pd.to_numeric(sample_data, errors='coerce')
                # 変換成功率が80%以上なら数値型と判定
                success_rate = converted.notna().sum() / len(sample_data)
                return success_rate >= 0.8
            except:
                return False
        
        return False
    
    def _convert_to_datetime(self, series: pd.Series) -> pd.Series:
        """日付時刻型に変換"""
        # Noneや空文字列を処理
        series_clean = series.copy()
        series_clean = series_clean.replace(['None', '', 'null', 'NULL'], pd.NaT)
        
        # まず指定フォーマットで試行
        for datetime_format in self.data_types_config.get('datetime_formats', []):
            try:
                converted = pd.to_datetime(series_clean, format=datetime_format, errors='coerce')
                # 変換成功率をチェック
                success_rate = converted.notna().sum() / len(series_clean.dropna())
                if success_rate >= 0.7:
                    return converted
            except:
                continue
        
        # フォーマット指定なしで変換
        try:
            return pd.to_datetime(series_clean, errors='coerce')
        except:
            return series_clean
    
    def get_file_info(self, df: pd.DataFrame, file_name: str) -> Dict[str, Any]:
        """ファイル情報を取得"""
        return {
            'file_name': file_name,
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum()
        }
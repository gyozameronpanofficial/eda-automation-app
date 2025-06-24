import yaml
import os
from typing import Dict, Any

class ConfigLoader:
    """設定ファイルの読み込みを担当するクラス"""
    
    @staticmethod
    def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
        """
        YAML設定ファイルを読み込む
        
        Args:
            config_path: 設定ファイルのパス
            
        Returns:
            Dict[str, Any]: 設定辞書
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                return config
            else:
                # デフォルト設定を返す
                return ConfigLoader._get_default_config()
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return ConfigLoader._get_default_config()
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """デフォルト設定を返す"""
        return {
            'general': {
                'max_file_size_mb': 3000,
                'max_memory_usage_gb': 16,
                'timeout_seconds': 120
            },
            'analysis': {
                'basic_stats': True,
                'distribution': True,
                'correlation': True,
                'timeseries': True,
                'preprocessing': True
            },
            'data_types': {
                'auto_detect': True,
                'datetime_formats': [
                    "%Y-%m-%d",
                    "%Y/%m/%d",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y/%m/%d %H:%M:%S"
                ],
                'categorical_threshold': 10
            },
            'visualization': {
                'figure_size': {'width': 10, 'height': 6},
                'dpi': 100,
                'style': 'whitegrid',
                'color_palette': 'husl',
                'max_categories': 20
            },
            'correlation': {
                'method': 'pearson',
                'threshold': 0.5,
                'show_heatmap': True,
                'show_scatter_matrix': True
            },
            'preprocessing': {
                'missing_value_methods': [
                    '削除',
                    '平均値補完',
                    '中央値補完',
                    '最頻値補完',
                    '前方補完',
                    '後方補完'
                ],
                'outlier_methods': [
                    'IQR法',
                    'Z-score法',
                    '修正Z-score法'
                ]
            },
            'report': {
                'include_all_analysis': True,
                'format': 'PDF',
                'template': 'default'
            }
        }
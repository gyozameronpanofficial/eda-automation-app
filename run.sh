#!/bin/bash
echo "========================================"
echo "EDA Automation App Startup Script"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found."
    echo "Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Create config directory if it doesn't exist
if [ ! -d "config" ]; then
    mkdir config
fi

# Create default settings file if it doesn't exist
if [ ! -f "config/settings.yaml" ]; then
    echo "Creating default settings file..."
    cat > config/settings.yaml << 'EOF'
# EDA Automation App Configuration File

# General Settings
general:
  max_file_size_mb: 3000  # Maximum file size in MB
  max_memory_usage_gb: 16  # Maximum memory usage in GB
  timeout_seconds: 120     # Processing timeout in seconds

# Analysis Features Enable/Disable
analysis:
  basic_stats: true       # Basic statistics
  distribution: true      # Distribution analysis
  correlation: true       # Correlation analysis
  timeseries: true        # Time series analysis
  preprocessing: true     # Preprocessing features

# Data Type Auto-Detection Settings
data_types:
  auto_detect: true
  datetime_formats:
    - "%Y-%m-%d"
    - "%Y/%m/%d"
    - "%Y-%m-%d %H:%M:%S"
    - "%Y/%m/%d %H:%M:%S"
  categorical_threshold: 10  # Categorical variable threshold

# Visualization Settings
visualization:
  figure_size:
    width: 10
    height: 6
  dpi: 100
  style: "whitegrid"      # seaborn style
  color_palette: "husl"   # color palette
  max_categories: 20      # max categories to display

# Correlation Analysis Settings
correlation:
  method: "pearson"       # pearson, spearman, kendall
  threshold: 0.5          # strong correlation threshold
  show_heatmap: true
  show_scatter_matrix: true

# Preprocessing Settings
preprocessing:
  missing_value_methods:
    - "Delete"
    - "Mean Imputation"
    - "Median Imputation"
    - "Mode Imputation"
    - "Forward Fill"
    - "Backward Fill"
  outlier_methods:
    - "IQR Method"
    - "Z-score Method"
    - "Modified Z-score Method"

# Report Settings
report:
  include_all_analysis: true
  format: "PDF"           # PDF, HTML
  template: "default"
EOF
fi

echo
echo "Starting application..."
echo "Access the application in your browser:"
echo
echo "    http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application."
echo

# Start Streamlit application
streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
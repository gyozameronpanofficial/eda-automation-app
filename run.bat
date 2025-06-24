@echo off
echo ========================================
echo EDA�������A�v�� �N���X�N���v�g
echo ========================================
echo.

:: ���z�������݂��邩�`�F�b�N
if not exist "venv" (
    echo �G���[: ���z����������܂���B
    echo ��� setup.bat �����s���Ă��������B
    pause
    exit /b 1
)

:: ���z�����A�N�e�B�x�[�g
echo ���z�����A�N�e�B�x�[�g��...
call venv\Scripts\activate.bat

:: �ݒ�t�@�C���̃f�B���N�g�����쐬
if not exist "config" mkdir config

:: �f�t�H���g�ݒ�t�@�C�������݂��Ȃ��ꍇ�͍쐬
if not exist "config\settings.yaml" (
    echo �f�t�H���g�ݒ�t�@�C�����쐬��...
    (
        echo # EDA�������A�v���ݒ�t�@�C��
        echo.
        echo # �S�ʐݒ�
        echo general:
        echo   max_file_size_mb: 3000  # �ő�t�@�C���T�C�Y�iMB�j
        echo   max_memory_usage_gb: 16  # �ő僁�����g�p�ʁiGB�j
        echo   timeout_seconds: 120     # �����^�C���A�E�g�i�b�j
        echo.
        echo # ���͋@�\�̗L��/����
        echo analysis:
        echo   basic_stats: true       # ��{���v
        echo   distribution: true      # ���z����
        echo   correlation: true       # ���֕���
        echo   timeseries: true        # ���n�񕪐�
        echo   preprocessing: true     # �O�����@�\
        echo.
        echo # �f�[�^�^��������ݒ�
        echo data_types:
        echo   auto_detect: true
        echo   datetime_formats:
        echo     - "%%Y-%%m-%%d"
        echo     - "%%Y/%%m/%%d"
        echo     - "%%Y-%%m-%%d %%H:%%M:%%S"
        echo     - "%%Y/%%m/%%d %%H:%%M:%%S"
        echo   categorical_threshold: 10  # �J�e�S���ϐ������臒l
        echo.
        echo # �����ݒ�
        echo visualization:
        echo   figure_size:
        echo     width: 10
        echo     height: 6
        echo   dpi: 100
        echo   style: "whitegrid"      # seaborn�X�^�C��
        echo   color_palette: "husl"   # �J���[�p���b�g
        echo   max_categories: 20      # �J�e�S���ϐ��̍ő�\����
        echo.
        echo # ���֕��͐ݒ�
        echo correlation:
        echo   method: "pearson"       # pearson, spearman, kendall
        echo   threshold: 0.5          # �������ւ�臒l
        echo   show_heatmap: true
        echo   show_scatter_matrix: true
        echo.
        echo # �O�����ݒ�
        echo preprocessing:
        echo   missing_value_methods:
        echo     - "�폜"
        echo     - "���ϒl�⊮"
        echo     - "�����l�⊮"
        echo     - "�ŕp�l�⊮"
        echo     - "�O���⊮"
        echo     - "����⊮"
        echo   outlier_methods:
        echo     - "IQR�@"
        echo     - "Z-score�@"
        echo     - "�C��Z-score�@"
        echo.
        echo # ���|�[�g�ݒ�
        echo report:
        echo   include_all_analysis: true
        echo   format: "PDF"           # PDF, HTML
        echo   template: "default"
    ) > config\settings.yaml
)

echo.
echo �A�v���P�[�V�������N����...
echo �u���E�U�ňȉ���URL�ɃA�N�Z�X���Ă�������:
echo.
echo    http://localhost:8501
echo.
echo ��~����ɂ� Ctrl+C �������Ă��������B
echo.

:: Streamlit�A�v�����N��
streamlit run app\main.py --server.port=8501 --server.address=0.0.0.0
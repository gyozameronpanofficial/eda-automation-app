@echo off
echo ========================================
echo EDA�������A�v�� �Z�b�g�A�b�v�X�N���v�g
echo ========================================
echo.

:: Python���C���X�g�[������Ă��邩�`�F�b�N
echo Python�̏�Ԃ��`�F�b�N��...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo �G���[: Python���C���X�g�[������Ă��܂���B
    echo Python 3.8�ȏ���C���X�g�[�����Ă���Ď��s���Ă��������B
    echo �_�E�����[�h: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python������ɃC���X�g�[������Ă��܂��B
python --version
echo.

:: ���z�������ɑ��݂���ꍇ�͍폜
if exist "venv" (
    echo �����̉��z�����폜��...
    rmdir /s /q venv
)

:: ���z�����쐬
echo ���z�����쐬��...
python -m venv venv
if %errorlevel% neq 0 (
    echo �G���[: ���z���̍쐬�Ɏ��s���܂����B
    pause
    exit /b 1
)

:: ���z�����A�N�e�B�x�[�g
echo ���z�����A�N�e�B�x�[�g��...
call venv\Scripts\activate.bat

:: pip���A�b�v�O���[�h
echo pip���A�b�v�O���[�h��...
python -m pip install --upgrade pip

:: �ˑ��֌W���C���X�g�[��
echo �ˑ��֌W���C���X�g�[����...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo �G���[: �ˑ��֌W�̃C���X�g�[���Ɏ��s���܂����B
    pause
    exit /b 1
)

echo.
echo ========================================
echo �Z�b�g�A�b�v�����I
echo ========================================
echo.
echo ���z�����쐬����A�ˑ��֌W���C���X�g�[������܂����B
echo.
echo �A�v���P�[�V�������N������ɂ�:
echo    run.bat �����s���Ă�������
echo.
echo �A�v���P�[�V�������~����ɂ�:
echo    Ctrl+C �������Ă�������
echo.
pause
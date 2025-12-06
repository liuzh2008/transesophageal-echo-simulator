@echo off
chcp 65001 >nul
echo ========================================
echo   经食管超声心动图模拟器
echo ========================================
echo.

REM 检查DICOM文件夹
set DICOM_FOLDER=D:\patients\SE7
if exist "%DICOM_FOLDER%" (
    echo [信息] 检测到DICOM文件夹: %DICOM_FOLDER%
    echo       将在启动时自动加载
) else (
    echo [警告] 未找到DICOM文件夹: %DICOM_FOLDER%
    echo       应用程序将以空状态启动
)

echo.
echo [信息] 启动应用程序...
echo ========================================
echo.

REM 直接启动应用程序
py src/main.py

REM 如果应用程序退出，显示消息
echo.
echo ========================================
echo [信息] 应用程序已退出
echo 按任意键关闭窗口...
echo ========================================
pause >nul

@echo off
color 0a

REM 确保我们在脚本所在的目录中
cd /d "%~dp0"
echo 当前工作目录: %cd%

REM 检查Python是否安装
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0c
    echo 错误: 未找到Python。请安装Python 3.6+后再试。
    pause
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        color 0c
        echo 错误: 创建虚拟环境失败。
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    color 0c
    echo 错误: 安装依赖失败。
    call venv\Scripts\deactivate.bat
    pause
    exit /b 1
)

REM 运行模拟器
color 0a
echo 启动弹球模拟器...
echo 按ESC键退出模拟器
python bouncing_balls.py

REM 退出虚拟环境
call venv\Scripts\deactivate.bat

echo 模拟器已关闭
pause

@echo off
echo 启动车牌识别后端服务...
cd /d %~dp0
call conda activate Simulation_of_the_parking_license_plate_recognition_system  REM 根据你的 conda 环境名修改
python app.py
pause
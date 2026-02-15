#!/bin/bash
# 树莓派开机自启脚本

cd /home/pi/Simulation_of_the_parking_license_plate_recognition_system/v2/raspberry_pi

# 激活虚拟环境（如果使用）
# source /home/pi/venv/bin/activate

# 运行主程序
python3 detect.py >> logs/autostart.log 2>&1
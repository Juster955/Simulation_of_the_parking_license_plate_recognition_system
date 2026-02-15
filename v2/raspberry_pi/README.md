# 树莓派端使用说明

## 1. 环境准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
pip install -r requirements.txt

# 如果是CSI摄像头，安装picamera2
sudo apt install python3-picamera2
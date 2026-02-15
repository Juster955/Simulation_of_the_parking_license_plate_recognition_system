"""
树莓派端配置文件
"""
import os

# ===== 门卫电脑（Windows PC）地址 =====
# 修改为你的门卫电脑实际IP地址（局域网内固定IP）
PC_IP = "192.168.1.100"      # ⚠️ 【请根据实际情况修改】
PC_PORT = 5000
PC_URL = f"http://{PC_IP}:{PC_PORT}/api/recognize"

# ===== 摄像头配置 =====
# 摄像头类型: 'usb' 或 'csi'
CAMERA_TYPE = 'usb'          # 【USB摄像头用0，CSI摄像头用picamera2】
USB_CAMERA_ID = 0             # 多个USB摄像头时修改索引
FRAME_WIDTH = 640             # 采集宽度
FRAME_HEIGHT = 480            # 采集高度
FRAME_SKIP = 3                # 跳帧处理（每3帧处理1帧）

# ===== YOLO 模型配置 =====
# 模型路径（如果使用默认预训练模型，会自动下载）
YOLO_MODEL = 'yolov8n.pt'     # 可选 yolov8n.pt, yolov8s.pt
CONFIDENCE_THRESHOLD = 0.5    # 检测置信度阈值

# ===== 调试模式 =====
DEBUG = True                  # 是否打印调试信息
SAVE_CROPS = False            # 是否保存裁剪的车牌图片（用于调试）
SAVE_PATH = './crops/'        # 保存路径（仅在SAVE_CROPS=True时有效）

# ===== 日志 =====
LOG_FILE = './logs/detect.log'
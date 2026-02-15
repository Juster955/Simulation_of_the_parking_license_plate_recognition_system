"""
树莓派端主程序：摄像头采集 -> YOLO检测车牌 -> 裁剪 -> HTTP上传到门卫电脑
"""
import cv2
import numpy as np
import requests
import time
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# 导入配置
import config

# 尝试导入YOLO（ultralytics）
try:
    from ultralytics import YOLO
except ImportError:
    print("请先安装 ultralytics: pip install ultralytics")
    sys.exit(1)

# 根据摄像头类型导入相应库
if config.CAMERA_TYPE == 'csi':
    try:
        from picamera2 import Picamera2
    except ImportError:
        print("请先安装 picamera2: sudo apt install python3-picamera2")
        sys.exit(1)

# ===== 日志配置 =====
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 创建保存目录（如果需要）=====
if config.SAVE_CROPS:
    os.makedirs(config.SAVE_PATH, exist_ok=True)


class PlateDetector:
    """树莓派端车牌检测器"""

    def __init__(self):
        """初始化摄像头和YOLO模型"""
        logger.info("初始化车牌检测系统...")

        # 1. 初始化YOLO模型
        try:
            self.model = YOLO(config.YOLO_MODEL)
            logger.info(f"YOLO模型加载成功: {config.YOLO_MODEL}")
        except Exception as e:
            logger.error(f"YOLO模型加载失败: {e}")
            sys.exit(1)

        # 2. 初始化摄像头
        self.cap = None
        if config.CAMERA_TYPE == 'usb':
            self._init_usb_camera()
        else:
            self._init_csi_camera()

        if self.cap is None:
            logger.error("摄像头初始化失败")
            sys.exit(1)

        # 3. 统计信息
        self.frame_count = 0
        self.detect_count = 0
        self.upload_count = 0

        logger.info("初始化完成，开始检测循环")

    def _init_usb_camera(self):
        """初始化USB摄像头"""
        self.cap = cv2.VideoCapture(config.USB_CAMERA_ID)
        if not self.cap.isOpened():
            logger.error(f"无法打开USB摄像头 (ID: {config.USB_CAMERA_ID})")
            return

        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        logger.info(f"USB摄像头初始化成功，分辨率: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")

    def _init_csi_camera(self):
        """初始化树莓派CSI摄像头"""
        try:
            self.cap = Picamera2()
            camera_config = self.cap.create_preview_configuration(
                main={"size": (config.FRAME_WIDTH, config.FRAME_HEIGHT)}
            )
            self.cap.configure(camera_config)
            self.cap.start()
            logger.info(f"CSI摄像头初始化成功，分辨率: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
            # 为统一接口，Picamera2需要单独处理读取，我们将在主循环中特殊处理
        except Exception as e:
            logger.error(f"CSI摄像头初始化失败: {e}")
            self.cap = None

    def read_frame(self):
        """读取一帧图像"""
        if config.CAMERA_TYPE == 'usb':
            ret, frame = self.cap.read()
            return ret, frame
        else:  # CSI摄像头
            frame = self.cap.capture_array()
            return True, frame

    def detect_plate(self, frame):
        """
        使用YOLO检测车牌
        返回: (是否检测到, 车牌区域裁剪图列表)
        """
        # YOLO推理
        results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD)

        plates = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                # 确保坐标在图像范围内
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                if x2 > x1 and y2 > y1:
                    plate_crop = frame[y1:y2, x1:x2]
                    plates.append(plate_crop)

                    if config.DEBUG:
                        logger.debug(f"检测到车牌区域: ({x1},{y1})-({x2},{y2})")

        return len(plates) > 0, plates

    def upload_plate(self, plate_img):
        """
        上传车牌图片到门卫电脑
        返回: (是否成功, 响应数据)
        """
        # 将图片编码为JPEG
        _, img_encoded = cv2.imencode('.jpg', plate_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_bytes = img_encoded.tobytes()

        try:
            # 发送HTTP POST请求
            files = {'image': ('plate.jpg', img_bytes, 'image/jpeg')}
            response = requests.post(config.PC_URL, files=files, timeout=5)

            if response.status_code == 200:
                result = response.json()
                if config.DEBUG:
                    logger.debug(f"上传成功: {result}")
                return True, result
            else:
                logger.warning(f"上传失败，HTTP状态码: {response.status_code}")
                return False, None

        except requests.exceptions.ConnectionError:
            logger.error(f"无法连接到门卫电脑: {config.PC_URL}")
            return False, None
        except requests.exceptions.Timeout:
            logger.error("连接超时")
            return False, None
        except Exception as e:
            logger.error(f"上传异常: {e}")
            return False, None

    def run(self):
        """主循环"""
        logger.info("开始主循环...")

        try:
            while True:
                # 读取一帧
                ret, frame = self.read_frame()
                if not ret:
                    logger.warning("读取摄像头失败")
                    time.sleep(0.1)
                    continue

                self.frame_count += 1

                # 跳帧处理
                if self.frame_count % config.FRAME_SKIP != 0:
                    continue

                # YOLO检测
                detected, plates = self.detect_plate(frame)

                if detected:
                    self.detect_count += 1
                    logger.info(f"检测到 {len(plates)} 个车牌")

                    # 对每个检测到的车牌进行处理
                    for i, plate_img in enumerate(plates):
                        # 可选：保存裁剪的图片（调试用）
                        if config.SAVE_CROPS:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                            filename = f"{config.SAVE_PATH}/plate_{timestamp}_{i}.jpg"
                            cv2.imwrite(filename, plate_img)
                            logger.debug(f"保存裁剪图片: {filename}")

                        # 上传到门卫电脑
                        success, result = self.upload_plate(plate_img)
                        if success:
                            self.upload_count += 1
                            if result.get('allowed'):
                                logger.info(f"✅ 允许通行 - 车牌: {result.get('plate', 'unknown')}")
                            else:
                                logger.info(f"❌ 禁止通行 - 车牌: {result.get('plate', 'unknown')}")
                        else:
                            logger.warning("上传失败")

                # 显示调试信息
                if config.DEBUG and self.frame_count % 30 == 0:
                    logger.info(f"统计: 总帧数={self.frame_count}, "
                                f"检测次数={self.detect_count}, "
                                f"上传成功={self.upload_count}")

        except KeyboardInterrupt:
            logger.info("用户中断程序")
        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        if config.CAMERA_TYPE == 'usb' and self.cap:
            self.cap.release()
        logger.info(f"最终统计: 总帧数={self.frame_count}, "
                    f"检测次数={self.detect_count}, "
                    f"上传成功={self.upload_count}")
        logger.info("程序退出")


# ===== 程序入口 =====
if __name__ == "__main__":
    print("=" * 50)
    print("树莓派车牌检测系统 v2")
    print("=" * 50)
    print(f"门卫电脑地址: {config.PC_URL}")
    print(f"摄像头类型: {config.CAMERA_TYPE}")
    print(f"跳帧处理: 每{config.FRAME_SKIP}帧处理1帧")
    print(f"调试模式: {'开启' if config.DEBUG else '关闭'}")
    print("=" * 50)

    detector = PlateDetector()
    detector.run()
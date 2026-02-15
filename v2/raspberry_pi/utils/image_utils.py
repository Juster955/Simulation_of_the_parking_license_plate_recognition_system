"""
图像处理工具函数（可选）
"""
import cv2
import numpy as np


def enhance_plate(image):
    """
    对车牌图像进行增强处理（可选）
    可在上传前调用，提高识别率
    """
    # 转为灰度
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # CLAHE 增强对比度
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 锐化
    kernel = np.array([[-1, -1, -1],
                       [-1, 9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened


def rotate_plate(image, angle):
    """
    旋转校正车牌（如果倾斜严重）
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h))
    return rotated
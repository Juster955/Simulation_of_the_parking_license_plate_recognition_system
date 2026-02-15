import re
import easyocr
import cv2
import numpy as np

class EasyOCRPlateRecognizer:
    """使用 EasyOCR 检测并识别车牌，提取字母数字部分作为车牌号"""

    def __init__(self, lang_list=None, gpu=False):
        if lang_list is None:
            lang_list = ['ch_sim', 'en']
        self.reader = easyocr.Reader(lang_list, gpu=gpu)

    def _preprocess(self, image):
        """图像预处理（可选，当前未启用）"""
        # 保持原图，注释掉预处理
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        # gray = clahe.apply(gray)
        # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        # gray = cv2.filter2D(gray, -1, kernel)
        # processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        # return processed
        return image  # 直接返回原图

    def recognize(self, image):
        """
        输入图像（BGR格式 numpy 数组），返回 (车牌号字符串, 置信度) 的列表，按以下规则排序：
        1. 长度优先（越长越可能是车牌）
        2. 同长度下置信度高者优先
        """
        # 使用原图，不预处理
        results = self.reader.readtext(
            image,
            text_threshold=0.01,    # 极低阈值，确保低置信度结果也能进入
            low_text=0.01,
            link_threshold=0.1,
            canvas_size=2560,
            contrast_ths=0.1,
            adjust_contrast=0.5,
            decoder='beamsearch',
            beamWidth=10,
        )

        found_plates = []
        for (bbox, text, confidence) in results:
            # 提取所有 ASCII 字母数字字符
            ascii_alnum = ''.join(c for c in text if c.isascii() and c.isalnum())
            # 如果提取结果长度在合理范围内（4-7位），作为候选
            if 4 <= len(ascii_alnum) <= 7:
                found_plates.append((ascii_alnum.upper(), confidence))
            else:
                # 可能有多段字母数字，尝试用正则提取最长连续段（备用）
                candidates = re.findall(r'[A-Z0-9]+', text.upper())
                if candidates:
                    longest = max(candidates, key=len)
                    if 4 <= len(longest) <= 7:
                        found_plates.append((longest, confidence))

        # 排序：先按长度降序，再按置信度降序
        found_plates.sort(key=lambda x: (len(x[0]), x[1]), reverse=True)
        return found_plates

    def recognize_best(self, image):
        """返回最佳车牌号字符串，若无返回 None"""
        plates = self.recognize(image)
        return plates[0][0] if plates else None


# ========== 测试入口 ==========
if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = "test_car.jpg"
        if not os.path.exists(img_path):
            print(f"请提供图片路径或放置 test_car.jpg")
            sys.exit(1)

    img = cv2.imread(img_path)
    if img is None:
        print("无法读取图片")
        sys.exit(1)

    recognizer = EasyOCRPlateRecognizer(gpu=False)

    # 打印原始识别结果（使用与 recognize 相同的低阈值参数）
    raw_results_low = recognizer.reader.readtext(
        img,
        text_threshold=0.01,
        low_text=0.01,
        link_threshold=0.1,
        canvas_size=2560,
        contrast_ths=0.1,
        adjust_contrast=0.5,
        decoder='beamsearch',
        beamWidth=10,
    )
    print("EasyOCR 原始识别结果（低阈值）：")
    for (bbox, text, conf) in raw_results_low:
        print(f"  文本: '{text}', 置信度: {conf:.4f}")

    # 提取车牌
    plates = recognizer.recognize(img)
    if plates:
        print("\n提取的车牌（字母+数字）：")
        for plate, conf in plates:
            print(f"  {plate} (置信度: {conf:.2f})")
    else:
        print("未提取到车牌")
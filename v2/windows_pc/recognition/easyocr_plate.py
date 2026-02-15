import re
import easyocr
import cv2
import numpy as np

class EasyOCRPlateRecognizer:
    """使用 EasyOCR 检测并识别车牌，提取字母数字部分作为车牌号"""

    def __init__(self, lang_list=None, gpu=False):
        """
        :param lang_list: 语言列表，默认 ['ch_sim', 'en']
        :param gpu: 是否使用 GPU
        """
        if lang_list is None:
            lang_list = ['ch_sim', 'en']
        self.reader = easyocr.Reader(lang_list, gpu=gpu)

    def _preprocess(self, image):
        """图像预处理：CLAHE + 锐化"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # CLAHE 自适应直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        # 锐化
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel)
        # 转为 RGB（EasyOCR 需要）
        processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        return processed

    def recognize(self, image):
        """
        输入图像（BGR格式 numpy 数组），返回 (车牌号字符串, 置信度) 的列表，按置信度降序。
        车牌号仅包含字母和数字（例如 'AF0236'），忽略汉字和符号。
        """
        # 预处理
        processed = self._preprocess(image)

        # 使用优化参数进行识别
        results = self.reader.readtext(
            processed,
            text_threshold=0.2,
            low_text=0.1,
            link_threshold=0.2,
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

        # 按置信度排序
        found_plates.sort(key=lambda x: x[1], reverse=True)
        return found_plates

    def recognize_best(self, image):
        """返回最佳车牌号字符串，若无返回 None"""
        plates = self.recognize(image)
        return plates[0][0] if plates else None


# ========== 测试入口（可选，用于独立测试）==========
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
        text_threshold=0.2,
        low_text=0.1,
        link_threshold=0.2,
        canvas_size=2560,
        contrast_ths=0.1,
        adjust_contrast=0.5,
        decoder='beamsearch',
        beamWidth=10,
    )
    print("EasyOCR 原始识别结果（低阈值）：")
    for (bbox, text, conf) in raw_results_low:
        print(f"  文本: '{text}', 置信度: {conf:.4f}")

    plates = recognizer.recognize(img)
    if plates:
        print("\n提取的车牌（字母+数字）：")
        for plate, conf in plates:
            print(f"  {plate} (置信度: {conf:.2f})")
    else:
        print("未提取到车牌")
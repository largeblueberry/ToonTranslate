import easyocr
import numpy as np

class OCRProcessor:
    def __init__(self):
        # 한국어와 영어 인식 모델 로드
        self.reader = easyocr.Reader(['ko', 'en'])

    def detect_and_recognize(self, img_np):
        """
        이미지에서 텍스트와 좌표를 추출합니다.
        return: list of dict [{"box": (xmin, ymin, xmax, ymax), "text": "...", "prob": 0.9}]
        """
        results = self.reader.readtext(img_np)
        ocr_results = []
        
        for bbox, text, prob in results:
            if prob < 0.25:  # 신뢰도가 너무 낮은 것은 제외
                continue
            
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            xmin, xmax = int(min(x_coords)), int(max(x_coords))
            ymin, ymax = int(min(y_coords)), int(max(y_coords))
            
            ocr_results.append({
                "box": (xmin, ymin, xmax, ymax),
                "text": text,
                "prob": prob
            })
        return ocr_results

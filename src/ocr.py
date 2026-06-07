import cv2
import easyocr
import numpy as np

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['ko', 'en'])

    def detect_and_recognize(self, img_np):
        """
        이미지에서 텍스트와 좌표를 추출합니다.
        return: list of dict [{"box": (xmin, ymin, xmax, ymax), "text": "...", "prob": 0.9}]
        """
        # [OpenCV #1] 전처리로 OCR 인식률 향상
        preprocessed = self._preprocess(img_np)

        results = self.reader.readtext(preprocessed)
        ocr_results = []

        for bbox, text, prob in results:
            if prob < 0.25:
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

        # [OpenCV #2] dilate + connectedComponents 기반 병합
        merged = self._merge_nearby_boxes(ocr_results, img_np.shape)
        return merged

    def _preprocess(self, img_np):
        """
        [OpenCV] OCR 인식률을 높이기 위한 이미지 전처리
        1. 그레이스케일 변환
        2. CLAHE로 대비 향상 (어두운 말풍선, 스캔 노이즈 대응)
        3. 가우시안 블러로 노이즈 제거
        """
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        # CLAHE: 지역적 대비 향상 (전체 히스토그램 평활화보다 만화에 적합)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 가우시안 블러로 고주파 노이즈 제거
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)

        # EasyOCR은 3채널 입력을 선호하므로 다시 BGR로 변환
        return cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    def _merge_nearby_boxes(self, ocr_results, img_shape, x_gap_ratio=0.3, y_gap_ratio=0.6):
        """
        [OpenCV] dilate + connectedComponents 기반 박스 병합
        - 기존 O(n²) Python 루프 → 형태학적 연산으로 대체
        - 팽창(dilate)으로 인접 박스를 연결한 뒤 연결 컴포넌트로 그룹화
        """
        if not ocr_results:
            return []

        img_h, img_w = img_shape[:2]

        # 빈 마스크에 OCR 박스를 흰색으로 그림
        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        for r in ocr_results:
            x1, y1, x2, y2 = r["box"]
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

        # 커널 크기: X축은 이미지 너비 기준, Y축은 평균 박스 높이 기준
        avg_box_h = int(np.mean([r["box"][3] - r["box"][1] for r in ocr_results]))
        kx = max(int(img_w * x_gap_ratio), 1)
        ky = max(int(avg_box_h * y_gap_ratio), 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kx, ky))

        # 팽창(dilate): 가까운 박스들이 서로 붙어 하나의 덩어리가 됨
        dilated = cv2.dilate(mask, kernel)

        # connectedComponents: 붙은 덩어리를 각각 다른 레이블로 분류
        num_labels, labels = cv2.connectedComponents(dilated)

        # 각 OCR 결과를 해당 레이블 그룹에 배정
        groups = [[] for _ in range(num_labels)]
        for r in ocr_results:
            x1, y1, x2, y2 = r["box"]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            # 중심점이 이미지 범위를 벗어나지 않도록 클리핑
            cy = np.clip(cy, 0, img_h - 1)
            cx = np.clip(cx, 0, img_w - 1)
            label = labels[cy, cx]
            groups[label].append(r)

        # 각 그룹을 하나의 박스로 병합
        merged_results = []
        for group in groups:
            if not group:
                continue
            group_sorted = sorted(group, key=lambda b: b["box"][1])
            merged_text = " ".join(b["text"] for b in group_sorted)
            avg_prob = sum(b["prob"] for b in group) / len(group)

            merged_results.append({
                "box": (
                    min(b["box"][0] for b in group),
                    min(b["box"][1] for b in group),
                    max(b["box"][2] for b in group),
                    max(b["box"][3] for b in group),
                ),
                "text": merged_text,
                "prob": avg_prob
            })

        return merged_results
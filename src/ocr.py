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
        results = self.reader.readtext(img_np)
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
        
        # 가까운 박스들을 말풍선 단위로 병합
        merged = self._merge_nearby_boxes(ocr_results, img_np.shape)
        return merged

    def _merge_nearby_boxes(self, ocr_results, img_shape, x_gap_ratio=0.3, y_gap_ratio=0.6):
        """
        서로 가까운 텍스트 박스들을 하나의 말풍선 단위로 병합        
        x_gap_ratio: 이미지 너비 대비 허용 X축 간격 비율
        y_gap_ratio: 박스 높이 대비 허용 Y축 간격 비율 (줄간격 허용치)
        """
        if not ocr_results:
            return []

        img_h, img_w = img_shape[:2]
        x_gap_threshold = img_w * x_gap_ratio   # X축: 이미지 너비의 30% 이내면 같은 그룹
        
        # Y축 기준으로 정렬 (위에서 아래로)
        sorted_boxes = sorted(ocr_results, key=lambda b: b["box"][1])
        
        groups = []  # 각 그룹 = 병합될 박스들의 리스트
        used = [False] * len(sorted_boxes)

        for i, box_i in enumerate(sorted_boxes):
            if used[i]:
                continue
            
            group = [box_i]
            used[i] = True
            xi1, yi1, xi2, yi2 = box_i["box"]
            box_h = max(yi2 - yi1, 1)
            y_gap_threshold = box_h * y_gap_ratio  # Y축: 박스 높이의 60% 이내면 같은 그룹

            for j, box_j in enumerate(sorted_boxes):
                if used[j]:
                    continue
                xj1, yj1, xj2, yj2 = box_j["box"]

                # 현재 그룹의 전체 바운딩 박스 계산
                group_xmin = min(b["box"][0] for b in group)
                group_xmax = max(b["box"][2] for b in group)
                group_ymin = min(b["box"][1] for b in group)
                group_ymax = max(b["box"][3] for b in group)

                # X축 겹침 또는 근접 여부 확인
                x_overlap = not (xj2 < group_xmin - x_gap_threshold or xj1 > group_xmax + x_gap_threshold)
                # Y축 근접 여부 확인
                y_close = (yj1 <= group_ymax + y_gap_threshold) and (yj2 >= group_ymin - y_gap_threshold)

                if x_overlap and y_close:
                    group.append(box_j)
                    used[j] = True

            groups.append(group)

        # 각 그룹을 하나의 박스로 병합
        merged_results = []
        for group in groups:
            # 텍스트는 Y 좌표 순으로 이어붙임
            group_sorted = sorted(group, key=lambda b: b["box"][1])
            merged_text = " ".join(b["text"] for b in group_sorted)
            avg_prob = sum(b["prob"] for b in group) / len(group)

            merged_xmin = min(b["box"][0] for b in group)
            merged_ymin = min(b["box"][1] for b in group)
            merged_xmax = max(b["box"][2] for b in group)
            merged_ymax = max(b["box"][3] for b in group)

            merged_results.append({
                "box": (merged_xmin, merged_ymin, merged_xmax, merged_ymax),
                "text": merged_text,
                "prob": avg_prob
            })

        return merged_results
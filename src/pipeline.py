from PIL import Image, ImageDraw
import numpy as np
from src.ocr import OCRProcessor
from src.translation import translate_text
from src.inpainting import clean_text_area
from src.text_fitting import fit_text_to_box

class TranslationPipeline:
    def __init__(self):
        self.ocr_processor = OCRProcessor()

    def run_ocr_and_translate(self, image: Image.Image, api_key=None, target_lang="EN"):
        img_np = np.array(image)
        ocr_results = self.ocr_processor.detect_and_recognize(img_np)
        
        pipeline_data = []
        for item in ocr_results:
            translated = translate_text(item["text"], api_key, target_lang)
            pipeline_data.append({
                "box": item["box"],
                "original": item["text"],
                "translated": translated
            })
        return pipeline_data

    def render_image(self, image: Image.Image, pipeline_data, bg_color=(255, 255, 255), text_color=(0, 0, 0), font_size_limit=30):
        edited_image = image.copy()

        # 모든 텍스트 영역을 먼저 다 지운다
        for item in pipeline_data:
            clean_text_area(edited_image, item["box"], bg_color)

        # 깨끗해진 이미지 위에 draw 객체 한 번만 생성
        draw = ImageDraw.Draw(edited_image)

        # 텍스트 렌더링
        for item in pipeline_data:
            xmin, ymin, xmax, ymax = item["box"]
            box_w = xmax - xmin
            box_h = ymax - ymin

            font, lines = fit_text_to_box(draw, item["translated"], box_w, box_h, max_font_size=font_size_limit)

            # 세로 중앙 정렬 계산
            line_heights = []
            total_lines_height = 0
            for line in lines:
                lb = draw.textbbox((0, 0), line, font=font)
                h = lb[3] - lb[1]
                line_heights.append(h)
                total_lines_height += h + 4

            current_y = ymin + (box_h - total_lines_height) / 2

            # 가로 중앙 정렬하여 그리기
            for i, line in enumerate(lines):
                lb = draw.textbbox((0, 0), line, font=font)
                line_w = lb[2] - lb[0]
                draw.text(
                    (xmin + (box_w - line_w) / 2, current_y),
                    line,
                    fill=text_color,
                    font=font
                )
                current_y += line_heights[i] + 4

        return edited_image

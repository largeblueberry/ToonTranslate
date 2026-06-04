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
        """
        1단계: 이미지에서 글자를 찾고 번역을 수행하여 데이터를 구조화합니다.
        """
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
        """
        2단계: 번역된 데이터(수정본 포함)를 바탕으로 최종 이미지를 그립니다.
        """
        edited_image = image.copy()
        draw = ImageDraw.Draw(edited_image)
        
        for item in pipeline_data:
            xmin, ymin, xmax, ymax = item["box"]
            box_w = xmax - xmin
            box_h = ymax - ymin
            
            # 1. 배경 지우기
            edited_image = clean_text_area(edited_image, item["box"], bg_color)
            
            # 2. 텍스트 피팅
            font, lines = fit_text_to_box(draw, item["translated"], box_w, box_h, max_font_size=font_size_limit)
            
            # 3. 세로 정렬을 위한 높이 계산
            total_lines_height = 0
            line_heights = []
            for line in lines:
                line_bbox = draw.textbbox((0, 0), line, font=font)
                h = line_bbox[3] - line_bbox[1]
                line_heights.append(h)
                total_lines_height += h + 4
                
            current_y = ymin + (box_h - total_lines_height) / 2
            
            # 4. 가로 정렬(가운데 정렬)하여 그리기
            for i, line in enumerate(lines):
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_w = line_bbox[2] - line_bbox[0]
                
                draw.text(
                    (xmin + (box_w - line_w) / 2, current_y), 
                    line, 
                    fill=text_color, 
                    font=font
                )
                current_y += line_heights[i] + 4
                
        return edited_image

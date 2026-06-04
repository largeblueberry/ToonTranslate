import textwrap
from PIL import ImageFont

def fit_text_to_box(draw, text, box_width, box_height, font_path="malgun.ttf", max_font_size=35):
    """
    말풍선 크기(가로/세로)에 맞춰 폰트 크기를 줄이고 줄바꿈을 적용합니다.
    """
    try:
        font = ImageFont.truetype(font_path, max_font_size)
    except:
        font = ImageFont.load_default()
        return font, [text]

    # 말풍선 곡률을 고려한 안전 영역 설정 (가로세로 85%만 사용)
    safe_width = max(int(box_width * 0.85), 10)
    safe_height = max(int(box_height * 0.85), 10)
    
    best_font_size = max_font_size
    best_lines = [text]
    
    # 폰트 크기를 줄여가며 박스 안에 들어가는지 확인
    for size in range(max_font_size, 8, -2):
        try:
            current_font = ImageFont.truetype(font_path, size)
        except:
            current_font = ImageFont.load_default()
            
        # 평균 글자 너비 측정 (영어 대문자 W 기준)
        sample_bbox = draw.textbbox((0, 0), "W", font=current_font)
        char_width = max(sample_bbox[2] - sample_bbox[0], 1)
        
        # 한 줄에 들어갈 글자 수 계산 및 래핑
        max_chars = max(int(safe_width / char_width), 1)
        lines = textwrap.wrap(text, width=max_chars)
        
        # 전체 줄의 높이 합산
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=current_font)
            total_height += (bbox[3] - bbox[1]) + 4  # 행간 4px 포함
            
        if total_height <= safe_height:
            best_font_size = size
            best_lines = lines
            break
            
    final_font = ImageFont.truetype(font_path, best_font_size)
    return final_font, best_lines
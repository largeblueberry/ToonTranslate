import textwrap
from PIL import ImageFont

def fit_text_to_box(
    draw, 
    text, 
    box_width, 
    box_height, 
    font_path="malgun.ttf", 
    max_font_size=50, 
    min_font_size=12,
    safe_area_ratio=0.85,
    line_spacing_ratio=0.15
):
    """
    말풍선 영역 내에서 가독성이 가장 좋은 (가장 큰) 폰트 크기와 줄바꿈을 찾습니다.
    ★핵심: 줄 수가 너무 많아지는 것을 절대적으로 방지합니다. (최대 4~5줄 제한)
    """
    try:
        font = ImageFont.truetype(font_path, max_font_size)
    except:
        font = ImageFont.load_default()
        return font, [text]

    words = text.split()
    if not words:
        return font, []

    # 안전 영역 계산
    safe_width = max(int(box_width * safe_area_ratio), 10)
    safe_height = max(int(box_height * safe_area_ratio), 10)

    best_font_size = min_font_size
    best_lines = [text]
    
    # 최적의 폰트 크기를 찾기 위한 이진 탐색
    low = min_font_size
    high = max_font_size
    
    while low <= high:
        mid_size = (low + high) // 2
        try:
            current_font = ImageFont.truetype(font_path, mid_size)
        except:
            current_font = ImageFont.load_default()

        # 폰트 높이 및 행간 계산
        sample_bbox = draw.textbbox((0, 0), "Aygqj", font=current_font)
        line_height = sample_bbox[3] - sample_bbox[1]
        line_spacing = int(line_height * line_spacing_ratio)

        # 단어별 너비 측정
        word_widths = [draw.textbbox((0, 0), w, font=current_font)[2] - draw.textbbox((0, 0), w, font=current_font)[0] for w in words]
        max_word_width = max(word_widths) if word_widths else 0
        
        # 단어 하나가 이미 안전 너비를 초과하면 이 크기는 불가능
        if max_word_width > safe_width:
            high = mid_size - 1
            continue

        # 텍스트 래핑 시도
        avg_char_width = max(draw.textbbox((0, 0), "a", font=current_font)[2] - draw.textbbox((0, 0), "a", font=current_font)[0], 1)
        max_chars = max(int(safe_width / avg_char_width), 1)
        lines = textwrap.wrap(text, width=max_chars)

        # 전체 높이 계산
        total_height = len(lines) * (line_height + line_spacing) - line_spacing

        # [핵심 조건 추가] 
        # 1. 전체 높이가 세로 영역 안에 들어오는가?
        # 2. 동시에, 줄 수가 만화 가독성 한계인 '5줄' 이하인가?
        if total_height <= safe_height and len(lines) <= 5:
            # 성공적인 조합 발견 -> 더 큰 폰트 크기가 가능한지 계속 탐색
            best_font_size = mid_size
            best_lines = lines
            low = mid_size + 1
        else:
            # 박스를 벗어나거나 줄 수가 너무 많음 -> 폰트 크기를 줄이거나 조절
            high = mid_size - 1

    # [안전장치] 만약 문장이 너무 길어서 위 루프에서 최적 크기를 못 찾고 
    # 너무 작은 폰트(예: 15px 이하)가 선택되었다면, 강제로 줄 수를 줄이고 글자를 키웁니다.
    if best_font_size < 18:
        best_font_size = 18
        try:
            current_font = ImageFont.truetype(font_path, best_font_size)
        except:
            current_font = ImageFont.load_default()
        
        # 가로 안전 영역을 살짝 넓혀서 글자 수를 더 많이 배치하게 유도 (줄 수 감소 효과)
        expanded_width = max(int(box_width * 0.95), 10)
        avg_char_width = max(draw.textbbox((0, 0), "a", font=current_font)[2] - draw.textbbox((0, 0), "a", font=current_font)[0], 1)
        max_chars = max(int(expanded_width / avg_char_width), 1)
        best_lines = textwrap.wrap(text, width=max_chars)

    final_font = ImageFont.truetype(font_path, best_font_size)
    return final_font, best_lines
import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

# 1. OCR 모델 로드 (캐싱하여 속도 향상)
@st.cache_resource
def load_ocr():
    # 한국어(ko)와 영어(en) 인식
    return easyocr.Reader(['ko', 'en'])

reader = load_ocr()

# 2. 간단한 번역 함수 (DeepL API 또는 임시 무료 번역 API 사용)
# *실제 사용 시 DEEPL_API_KEY를 입력하세요. 테스트용으로 작동 안 하면 원본 텍스트를 그대로 반환하게 해둠.
def translate_text(text, target_lang="EN"):
    api_key = "YOUR_DEEPL_API_KEY"  # 본인의 API 키 입력
    if api_key == "YOUR_DEEPL_API_KEY" or not api_key:
        return f"[Translated] {text}" # API 키가 없을 때 임시 반환
    
    url = "https://api-free.deepl.com/v2/translate"
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
    data = {"text": [text], "target_lang": target_lang}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.json()["translations"][0]["text"]
    except Exception as e:
        return f"[Error] {text}"

# 3. 텍스트 피팅 함수 (박스 크기에 맞춰 글자 크기 조절)
def fit_text(draw, text, box_width, box_height, max_font_size=40):
    # 시스템에 있는 기본 폰트 사용 (Windows: malgun.ttf, Mac: AppleGothic.ttf 등)
    # 여기서는 폰트 경로를 직접 지정하거나 기본 폰트를 로드해야 합니다.
    try:
        font_path = "malgun.ttf" # Windows 기준 (Mac은 "Arial.ttf" 등 사용)
        font = ImageFont.truetype(font_path, max_font_size)
    except:
        font = ImageFont.load_default()
        return font, [text] # 폰트 로드 실패 시 기본 폰트와 원본 텍스트 반환

    # 간단한 줄바꿈 및 크기 조절 로직
    font_size = max_font_size
    while font_size > 8:
        font = ImageFont.truetype(font_path, font_size)
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            # 텍스트 가로 길이 측정
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= box_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
            
        # 전체 높이 측정
        total_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
        if total_height <= box_height:
            return font, lines
        
        font_size -= 2 # 박스보다 크면 폰트 사이즈를 줄임
        
    return font, [text]

# --- Streamlit UI 구성 ---
st.title("🫧 BubbleFit - 초간단 MVP")
st.write("웹툰 이미지를 업로드하면 글자를 인식해 번역하고 덮어씌웁니다.")

uploaded_file = st.file_uploader("웹툰 이미지 업로드 (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("원본 이미지")
        st.image(image, use_container_width=True)
        
    if st.button("자동 번역 시작"):
        with st.spinner("글자 분석 및 번역 중..."):
            # PIL 이미지를 numpy 배열로 변환 (EasyOCR 입력용)
            img_np = np.array(image)
            
            # 1. OCR 실행 (텍스트와 좌표 추출)
            ocr_results = reader.readtext(img_np)
            
            # 편집할 이미지 복사
            edited_image = image.copy()
            draw = ImageDraw.Draw(edited_image)
            
            for bbox, text, prob in ocr_results:
                if prob < 0.3: # 인식 신뢰도가 너무 낮으면 패스
                    continue
                    
                # bbox 구조: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                xmin, xmax = int(min(x_coords)), int(max(x_coords))
                ymin, ymax = int(min(y_coords)), int(max(y_coords))
                
                box_w = xmax - xmin
                box_h = ymax - ymin
                
                # 2. Inpainting 대체: 텍스트 영역을 흰색(배경)으로 덮어쓰기
                # (실제 웹툰 말풍선은 대개 흰색이므로 이 방법이 MVP에서 잘 통합니다)
                draw.rectangle([xmin, ymin, xmax, ymax], fill=(255, 255, 255))
                
                # 3. 번역
                translated = translate_text(text, target_lang="EN")
                
                # 4. 텍스트 피팅 및 그리기
                font, lines = fit_text(draw, translated, box_w, box_h)
                
                # 줄바꿈된 텍스트 그리기
                current_y = ymin
                for line in lines:
                    line_bbox = draw.textbbox((0, 0), line, font=font)
                    line_w = line_bbox[2] - line_bbox[0]
                    line_h = line_bbox[3] - line_bbox[1]
                    
                    # 가운데 정렬하여 그리기
                    draw.text((xmin + (box_w - line_w)/2, current_y), line, fill=(0, 0, 0), font=font)
                    current_y += line_h + 2
            
            with col2:
                st.subheader("번역 결과")
                st.image(edited_image, use_container_width=True)

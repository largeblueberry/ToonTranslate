import sys
import os
# 프로젝트 루트 디렉토리를 Python Path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from PIL import Image
import io
from src.pipeline import TranslationPipeline

st.set_page_config(layout="wide")

st.title("🫧 BubbleFit - 작가용 초고속 번역 식자 MVP")
st.write("웹툰 이미지를 업로드하고 번역 결과를 미세조정하세요.")

# 파이프라인 싱글톤 로드 (캐싱으로 속도 향상)
@st.cache_resource
def get_pipeline():
    return TranslationPipeline()

pipeline = get_pipeline()

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정 및 도구")
    deepl_key = st.text_input("DeepL API Key (선택)", type="password", placeholder="api-free 키 입력")
    target_lang = st.selectbox("번역 언어", ["EN", "KO", "JA", "ZH"])
    font_size_limit = st.slider("최대 글자 크기", 10, 60, 30)
    bg_color = st.color_picker("말풍선 배경 색상", "#FFFFFF")
    text_color = st.color_picker("글자 색상", "#000000")

uploaded_file = st.file_uploader("웹툰 이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("원본 이미지")
        st.image(image, use_container_width=True)
        
    # 세션 상태 관리
    if "pipeline_data" not in st.session_state or st.button("🔍 자동 번역 및 식자 시작"):
        with st.spinner("글자 분석 및 번역 중..."):
            # 1단계: OCR 및 번역 파이프라인 실행
            st.session_state.pipeline_data = pipeline.run_ocr_and_translate(
                image, api_key=deepl_key, target_lang=target_lang
            )
            st.session_state.ocr_done = True

    if st.session_state.get("ocr_done"):
        # RGB 변환
        bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_rgb = tuple(int(text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        st.subheader("✍️ 번역 텍스트 수동 미세조정")
        
        # 작가가 직접 텍스트를 수정할 수 있는 폼
        with st.form("edit_form"):
            updated_data = []
            for idx, item in enumerate(st.session_state.pipeline_data):
                xmin, ymin, _, _ = item["box"]
                st.write(f"**말풍선 #{idx+1}** (위치: X={xmin}, Y={ymin})")
                col_orig, col_trans = st.columns(2)
                with col_orig:
                    st.text(f"원본: {item['original']}")
                with col_trans:
                    new_text = st.text_input(f"번역문 수정", value=item["translated"], key=f"input_{idx}")
                
                updated_data.append({
                    "box": item["box"],
                    "original": item["original"],
                    "translated": new_text
                })
            
            if st.form_submit_button("🎨 변경사항 적용 및 이미지 갱신"):
                st.session_state.pipeline_data = updated_data

        # 2단계: 최종 이미지 렌더링
        final_image = pipeline.render_image(
            image, 
            st.session_state.pipeline_data, 
            bg_color=bg_rgb, 
            text_color=text_rgb, 
            font_size_limit=font_size_limit
        )

        with col2:
            st.subheader("번역 및 식자 결과")
            st.image(final_image, use_container_width=True)
            
            # 다운로드 기능
            buf = io.BytesIO()
            final_image.save(buf, format="PNG")
            st.download_button(
                label="📥 완성 이미지 다운로드", 
                data=buf.getvalue(), 
                file_name="translated_webtoon.png", 
                mime="image/png"
            )
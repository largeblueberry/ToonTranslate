import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from PIL import Image
import io
from src.pipeline import TranslationPipeline

st.set_page_config(layout="wide")

st.title("🫧 BubbleFit - 작가용 초고속 번역 식자 MVP")
st.write("웹툰 이미지를 업로드하고 번역 결과를 미세조정하세요.")

@st.cache_resource
def get_pipeline():
    return TranslationPipeline()

pipeline = get_pipeline()

uploaded_file = st.file_uploader("웹툰 이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("원본 이미지")
        st.image(image, use_container_width=True)

    if "pipeline_data" not in st.session_state or st.button("🔍 자동 번역 및 식자 시작"):
        with st.spinner("글자 분석 및 번역 중..."):
            st.session_state.pipeline_data = pipeline.run_ocr_and_translate(
                image, api_key=None, target_lang="EN"
            )
            st.session_state.ocr_done = True

    if st.session_state.get("ocr_done"):
        st.subheader("✍️ 번역 텍스트 수동 미세조정")

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

        # 고정값으로 렌더링
        final_image = pipeline.render_image(
            image,
            st.session_state.pipeline_data,
            bg_color=(255, 255, 255),
            text_color=(0, 0, 0),
            font_size_limit=30
        )

        with col2:
            st.subheader("번역 및 식자 결과")
            st.image(final_image, use_container_width=True)

            buf = io.BytesIO()
            final_image.save(buf, format="PNG")
            st.download_button(
                label="📥 완성 이미지 다운로드",
                data=buf.getvalue(),
                file_name="translated_webtoon.png",
                mime="image/png"
            )
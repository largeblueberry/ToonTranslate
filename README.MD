# 🫧 BubbleFit

> **웹툰 이미지를 업로드하면, 말풍선 내 텍스트를 자동으로 인식·번역하고 말풍선 크기에 맞게 자동 배치해주는 작가 도구**

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

---

## 📌 프로젝트 소개

웹툰을 다른 언어로 번역할 때, 번역된 텍스트의 길이가 원문과 달라져 **말풍선 내부 배치가 어려워지는 문제**가 있습니다.

예를 들어 한국어 "안녕"은 2글자지만, 영어로 번역하면 "Hello"로 5글자가 됩니다.  
반대로 긴 문장이 짧아지는 경우도 있어, 번역 후 말풍선 레이아웃을 **수작업으로 일일이 조정**해야 하는 번거로움이 있습니다.

**BubbleFit**은 이 과정을 컴퓨터 비전 기술로 자동화합니다.

```
웹툰 이미지 업로드
      ↓
말풍선 영역 자동 탐지  (Object Detection)
      ↓
말풍선 내 텍스트 인식  (OCR)
      ↓
텍스트 자동 번역       (Translation API)
      ↓
번역 텍스트 자동 배치  (Text Fitting Algorithm)
      ↓
완성된 번역 이미지 출력
```

---

## 🎯 주요 기능

| 기능 | 설명 |
|------|------|
| 🔍 **말풍선 탐지** | YOLOv8 기반으로 말풍선 영역을 자동 검출 |
| ✂️ **말풍선 세그멘테이션** | SAM(Segment Anything Model)으로 말풍선 내부 영역 정밀 분리 |
| 📝 **텍스트 인식 (OCR)** | EasyOCR로 말풍선 내 텍스트 자동 추출 |
| 🧹 **텍스트 제거 (Inpainting)** | 원본 텍스트 제거 후 배경 자동 복원 |
| 🌐 **자동 번역** | DeepL API를 활용한 고품질 번역 |
| 📐 **텍스트 자동 피팅** | 말풍선 크기에 맞춰 폰트 크기·줄바꿈 자동 조정 |
| 🖼️ **이미지 합성** | 번역 텍스트를 원본 이미지에 자연스럽게 합성 출력 |

---

## 🛠️ 기술 스택

### Computer Vision
| 분류 | 기술 | 용도 |
|------|------|------|
| 이미지 처리 | OpenCV, Pillow | 전처리, 렌더링 |
| 객체 탐지 | YOLOv8 (Ultralytics) | 말풍선 영역 검출 |
| 세그멘테이션 | SAM (Segment Anything) | 말풍선 내부 정밀 분리 |
| OCR | EasyOCR, PaddleOCR | 텍스트 인식 |
| Inpainting | LaMa | 텍스트 제거 후 배경 복원 |
| 딥러닝 | PyTorch | 모델 추론 |

### Translation & Rendering
| 분류 | 기술 | 용도 |
|------|------|------|
| 번역 | DeepL API | 고품질 텍스트 번역 |
| 텍스트 렌더링 | Pillow, FreeType | 폰트 렌더링 |
| 영역 계산 | Shapely | 말풍선 폴리곤 영역 계산 |

### Demo & Backend
| 분류 | 기술 | 용도 |
|------|------|------|
| 데모 UI | Streamlit | 웹 데모 앱 |
| 백엔드 | FastAPI | API 서버 |
| 환경 관리 | Docker | 실행 환경 통일 |

---

## 🗂️ 프로젝트 구조

```
BubbleFit/
├── data/
│   ├── raw/                  # 원본 웹툰 이미지
│   └── output/               # 번역 결과 이미지
├── models/
│   ├── bubble_detector/      # 말풍선 탐지 모델 가중치
│   └── inpainting/           # Inpainting 모델 가중치
├── src/
│   ├── ocr.py                # 텍스트 인식 모듈
│   ├── detection.py          # 말풍선 탐지 모듈
│   ├── segmentation.py       # 세그멘테이션 모듈
│   ├── translation.py        # 번역 모듈
│   ├── text_fitting.py       # 텍스트 자동 피팅 모듈
│   ├── inpainting.py         # 텍스트 제거 모듈
│   └── pipeline.py           # 전체 파이프라인
├── app/
│   └── streamlit_app.py      # Streamlit 데모 앱
├── notebooks/                # 실험 및 분석 노트북
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/BubbleFit.git
cd BubbleFit
```

### 2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
cp .env.example .env
# .env 파일에 DEEPL_API_KEY 입력
```

### 5. 데모 앱 실행
```bash
streamlit run app/streamlit_app.py
```

---

## 🔄 파이프라인 상세

```
┌─────────────────────────────────────────────────────┐
│                   Input Image                       │
│                  (웹툰 이미지)                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         [1] Speech Bubble Detection                 │
│              YOLOv8 Object Detection                │
│         → 말풍선 바운딩 박스 좌표 추출               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         [2] Segmentation                            │
│         Segment Anything Model (SAM)                │
│         → 말풍선 내부 마스크 생성                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         [3] OCR (Text Recognition)                  │
│              EasyOCR                                │
│         → 말풍선 내 텍스트 추출                      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         [4] Inpainting (Text Removal)               │
│              LaMa Model                             │
│         → 텍스트 제거 후 배경 복원                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         [5] Translation                             │
│              DeepL API                              │
│         → 번역 텍스트 생성                           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         [6] Text Fitting & Rendering                │
│         Auto Font Sizing + Line Wrapping            │
│         → 말풍선 크기에 맞게 텍스트 자동 배치        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Output Image                       │
│              (번역 완성 이미지)                       │
└─────────────────────────────────────────────────────┘
```

---

## 📅 개발 로드맵

- [x] **Week 1** : 환경 세팅, OCR 파이프라인 구축, 번역 API 연동
- [ ] **Week 2** : 말풍선 탐지 모델 적용, 텍스트 피팅 알고리즘 개발
- [ ] **Week 3** : Inpainting 모듈 개발, 전체 파이프라인 통합
- [ ] **Week 4** : Streamlit 데모 완성, 성능 평가, 최종 발표 준비

---

## 👥 팀원

| 이름 | 역할 |
|------|------|
| - | 말풍선 탐지 / 세그멘테이션 |
| - | OCR / 번역 파이프라인 |
| - | 텍스트 피팅 / UI 개발 |

---

## 📄 라이선스

This project is licensed under the MIT License.

---

## 🙏 참고 자료

- [YOLOv8 - Ultralytics](https://github.com/ultralytics/ultralytics)
- [Segment Anything Model (SAM) - Meta AI](https://github.com/facebookresearch/segment-anything)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [LaMa - Resolution-robust Large Mask Inpainting](https://github.com/advimman/lama)
- [DeepL API](https://www.deepl.com/docs-api)
- [Manga109 Dataset](http://www.manga109.org/en/)
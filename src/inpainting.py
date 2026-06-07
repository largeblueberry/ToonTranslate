import cv2
import numpy as np
from PIL import Image

def clean_text_area(image: Image.Image, box, bg_color=(255, 255, 255)):

    img_np = np.array(image)
    xmin, ymin, xmax, ymax = box

    # 이미지 경계 클리핑
    h, w = img_np.shape[:2]
    xmin, ymin = max(xmin, 0), max(ymin, 0)
    xmax, ymax = min(xmax, w), min(ymax, h)

    # [OpenCV #1] 박스 주변 테두리 픽셀로 배경색 자동 추정
    margin = 6  # 테두리 샘플링 두께 (px)
    border_pixels = []

    top    = img_np[max(ymin-margin, 0):ymin,       xmin:xmax]
    bottom = img_np[ymax:min(ymax+margin, h),       xmin:xmax]
    left   = img_np[ymin:ymax, max(xmin-margin, 0):xmin      ]
    right  = img_np[ymin:ymax, xmax:min(xmax+margin, w)      ]

    for region in [top, bottom, left, right]:
        if region.size > 0:
            border_pixels.append(region.reshape(-1, region.shape[-1]))

    if border_pixels:
        all_pixels = np.vstack(border_pixels)
        # 중앙값(median)으로 배경색 추정 → 이상치(텍스트 픽셀)에 강건함
        estimated_bg = tuple(np.median(all_pixels, axis=0).astype(int).tolist())
    else:
        estimated_bg = bg_color

    # [OpenCV #2] 추정된 배경색으로 영역 채우기
    fill_color = estimated_bg if len(img_np.shape) == 3 else int(np.mean(estimated_bg))
    cv2.rectangle(img_np, (xmin, ymin), (xmax, ymax), fill_color, thickness=-1)

    # [OpenCV #3] 경계 스무딩: 채운 영역 테두리만 살짝 블러 처리
    pad = 4
    bx1, by1 = max(xmin - pad, 0), max(ymin - pad, 0)
    bx2, by2 = min(xmax + pad, w), min(ymax + pad, h)
    border_region = img_np[by1:by2, bx1:bx2]
    blurred = cv2.GaussianBlur(border_region, (5, 5), 0)

    # 내부는 원본(채운 색) 유지, 테두리 부분만 블러 적용
    blend_mask = np.zeros(border_region.shape[:2], dtype=np.float32)
    inner_y1 = ymin - by1 + pad
    inner_x1 = xmin - bx1 + pad
    inner_y2 = inner_y1 + (ymax - ymin) - pad * 2
    inner_x2 = inner_x1 + (xmax - xmin) - pad * 2
    if inner_y2 > inner_y1 and inner_x2 > inner_x1:
        blend_mask[inner_y1:inner_y2, inner_x1:inner_x2] = 1.0
    blend_mask_3ch = np.stack([blend_mask] * (img_np.shape[2] if img_np.ndim == 3 else 1), axis=-1)
    img_np[by1:by2, bx1:bx2] = (
        border_region * blend_mask_3ch + blurred * (1 - blend_mask_3ch)
    ).astype(np.uint8)

    # numpy → PIL 변환 후 in-place 업데이트
    result = Image.fromarray(img_np)
    image.paste(result)
from PIL import ImageDraw

def clean_text_area(image, box, bg_color=(255, 255, 255)):
    """
    말풍선 내부의 글자 영역을 배경색(기본 흰색)으로 덮어씌웁니다.
    """
    draw = ImageDraw.Draw(image)
    xmin, ymin, xmax, ymax = box
    # 글자 경계보다 살짝 여유있게(Padding) 지워줍니다.
    padding = 6
    draw.rectangle(
        [xmin - padding, ymin - padding, xmax + padding, ymax + padding], 
        fill=bg_color
    )
    return image

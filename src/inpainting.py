from PIL import ImageDraw

def clean_text_area(image, box, bg_color=(255, 255, 255)):
    """
    말풍선 내부의 글자 영역을 배경색으로 덮어씌운다.
    """
    draw = ImageDraw.Draw(image)
    xmin, ymin, xmax, ymax = box
    padding = 6
    draw.rectangle(
        [xmin - padding, ymin - padding, xmax + padding, ymax + padding],
        fill=bg_color
    )

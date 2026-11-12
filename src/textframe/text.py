from PIL import Image, ImageDraw, ImageFont

from textframe.core.interfaces import IRenderer, ITexture


def create_text_texture(
    renderer: IRenderer,
    text: str,
    font_size: int,
    color_rgba: tuple[int, int, int, int],
) -> tuple[ITexture, int, int]:
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    # Вычисляем размер текста
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = max(1, bbox[2] - bbox[0])
    text_h = max(1, bbox[3] - bbox[1])

    # Рисуем текст в RGBA-буфер
    img = Image.new("RGBA", (text_w, text_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((-bbox[0], -bbox[1]), text, font=font, fill=color_rgba)

    rgba_bytes = img.tobytes("raw", "RGBA")
    texture = renderer.create_texture(text_w, text_h, rgba_bytes)
    return texture, text_w, text_h

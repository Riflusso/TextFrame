from OpenGL import GL
from PIL import Image, ImageDraw, ImageFont


def create_text_texture(text: str, font_size: int = 32) -> tuple[int, int, int]:
    """Рендерит текст через системный шрифт в текстуру OpenGL. Возвращает (texture_id, width, height)."""
    try:
        # Берем стандартный шрифт Windows (поддерживает и русский, и английский)
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    # Узнаем точный размер текста в пикселях
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0] + 4
    height = bbox[3] - bbox[1] + 4

    # Рисуем белый текст на прозрачном фоне
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((-bbox[0] + 2, -bbox[1] + 2), text, font=font, fill=(240, 245, 255, 255))

    # Загружаем пиксели в OpenGL текстуру
    tex_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image.tobytes()
    )
    return tex_id, width, height


def draw_text_texture(tex_id: int, x: float, y: float, width: float, height: float) -> None:
    """Выводит готовую текстуру текста в координатах (x, y) с заданным размером."""
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
    GL.glColor3f(1.0, 1.0, 1.0)

    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord2f(0.0, 0.0); GL.glVertex2f(x, y)
    GL.glTexCoord2f(1.0, 0.0); GL.glVertex2f(x + width, y)
    GL.glTexCoord2f(1.0, 1.0); GL.glVertex2f(x + width, y + height)
    GL.glTexCoord2f(0.0, 1.0); GL.glVertex2f(x, y + height)
    GL.glEnd()

    GL.glDisable(GL.GL_TEXTURE_2D)

import numpy as np
from OpenGL import GL
from PIL import Image, ImageDraw, ImageFont

from .styles import TEXT_COLOR_RGBA


def create_text_texture(
    text: str,
    font_size: int,
    color: tuple[int, int, int, int] = TEXT_COLOR_RGBA,
) -> tuple[int, int, int]:
    """Рендерит текст в текстуру OpenGL под конкретный font_size."""
    safe_size = max(4, font_size)
    try:
        font = ImageFont.truetype("arial.ttf", safe_size)
    except OSError:
        font = ImageFont.load_default()

    left, top, right, bottom = font.getbbox(text)
    width = max(1, right - left + 4)
    height = max(1, bottom - top + 4)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((-left + 2, -top + 2), text, font=font, fill=color)

    pixels = np.array(image, dtype=np.uint8)

    tex_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,
        0,
        GL.GL_RGBA,
        width,
        height,
        0,
        GL.GL_RGBA,
        GL.GL_UNSIGNED_BYTE,
        pixels,
    )
    return tex_id, width, height


def delete_text_texture(tex_id: int) -> None:
    """Удаляет текстуру из видеопамяти."""
    if tex_id:
        GL.glDeleteTextures([tex_id])


def draw_text_texture(tex_id: int, x: float, y: float, width: float, height: float) -> None:
    """Выводит готовую текстуру текста в координатах (x, y) 1 к 1."""
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

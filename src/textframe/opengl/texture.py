from OpenGL import GL

from textframe.core.interfaces import ITexture


class OpenGLTexture(ITexture):
    def __init__(self, width: int, height: int, rgba_bytes: bytes):
        self.tex_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA,
            width, height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, rgba_bytes,
        )
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def draw(self, x: float, y: float, width: float, height: float) -> None:
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex_id)
        GL.glColor4f(1.0, 1.0, 1.0, 1.0)

        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0.0, 0.0); GL.glVertex2f(x, y)
        GL.glTexCoord2f(1.0, 0.0); GL.glVertex2f(x + width, y)
        GL.glTexCoord2f(1.0, 1.0); GL.glVertex2f(x + width, y + height)
        GL.glTexCoord2f(0.0, 1.0); GL.glVertex2f(x, y + height)
        GL.glEnd()

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glDisable(GL.GL_TEXTURE_2D)

    def destroy(self) -> None:
        if self.tex_id:
            GL.glDeleteTextures(1, [self.tex_id])
            self.tex_id = 0

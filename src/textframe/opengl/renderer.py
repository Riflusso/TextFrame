import sdl3
from OpenGL import GL

from textframe.core.interfaces import IRenderer, ITexture

from .texture import OpenGLTexture


class OpenGLRenderer(IRenderer):
    def __init__(self):
        self.gl_context = None

    def prepare_window_hints(self) -> None:
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 1)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DOUBLEBUFFER, 1)

    def get_window_flags(self) -> int:
        return sdl3.SDL_WINDOW_OPENGL

    def init_context(self, window) -> None:
        self.gl_context = sdl3.SDL_GL_CreateContext(window)
        if not self.gl_context:
            raise RuntimeError(f"SDL_GL_CreateContext failed: {sdl3.SDL_GetError().decode()}")

        sdl3.SDL_GL_MakeCurrent(window, self.gl_context)
        sdl3.SDL_GL_SetSwapInterval(1)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    def begin_frame(self, width: int, height: int, bg_color: tuple[float, float, float]) -> None:
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, height, 0, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        GL.glClearColor(*bg_color, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def fill_rect(
        self, x: float, y: float, width: float, height: float, color: tuple[float, float, float]
    ) -> None:
        GL.glColor3f(*color)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(x, y)
        GL.glVertex2f(x + width, y)
        GL.glVertex2f(x + width, y + height)
        GL.glVertex2f(x, y + height)
        GL.glEnd()

    def create_texture(self, width: int, height: int, rgba_bytes: bytes) -> ITexture:
        return OpenGLTexture(width, height, rgba_bytes)

    def end_frame(self, window) -> None:
        sdl3.SDL_GL_SwapWindow(window)

    def shutdown(self) -> None:
        if self.gl_context:
            sdl3.SDL_GL_DestroyContext(self.gl_context)
            self.gl_context = None

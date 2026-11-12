import ctypes

import sdl3
from OpenGL import GL

from .text import create_text_texture, draw_text_texture


def init_window(title: bytes, width: int, height: int):
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init failed: {sdl3.SDL_GetError().decode()}")

    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 1)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DOUBLEBUFFER, 1)

    window = sdl3.SDL_CreateWindow(
        title, width, height, sdl3.SDL_WINDOW_OPENGL | sdl3.SDL_WINDOW_RESIZABLE
    )
    gl_context = sdl3.SDL_GL_CreateContext(window)
    sdl3.SDL_GL_MakeCurrent(window, gl_context)
    sdl3.SDL_GL_SetSwapInterval(1)

    # Включаем прозрачность (альфа-канал) для текстуры текста
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    return window, gl_context


def setup_ortho(width: int, height: int) -> None:
    GL.glViewport(0, 0, width, height)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(0, width, height, 0, -1, 1)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()


def handle_events() -> bool:
    event = sdl3.SDL_Event()
    while sdl3.SDL_PollEvent(ctypes.byref(event)):
        if event.type == sdl3.SDL_EVENT_QUIT:
            return False
        if event.type == sdl3.SDL_EVENT_KEY_DOWN:
            if event.key.scancode == sdl3.SDL_SCANCODE_ESCAPE:
                return False
    return True


def render(width: int, height: int, tex_id: int, x: float, y: float, text_w: float, text_h: float) -> None:
    setup_ortho(width, height)

    GL.glClearColor(0.12, 0.13, 0.16, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    draw_text_texture(tex_id, x, y, text_w, text_h)


def cleanup(window, gl_context, tex_id: int) -> None:
    GL.glDeleteTextures([tex_id])
    sdl3.SDL_GL_DestroyContext(gl_context)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()


def main() -> None:
    width, height = 900, 600
    window, gl_context = init_window(b"TextFrame - OpenGL", width, height)

    flags = sdl3.SDL_GetWindowFlags(window)
    if flags & sdl3.SDL_WINDOW_OPENGL:
        text = "Привет, OpenGL!"
    elif flags & sdl3.SDL_WINDOW_VULKAN:
        text = "Привет, Vulkan!"
    else:
        text = "Привет!"

    tex_id, base_w, base_h = create_text_texture(text, font_size=32)

    start_x = 100.0
    start_y = 120.0
    scale = 1.0

    w_ptr = ctypes.c_int(width)
    h_ptr = ctypes.c_int(height)

    running = True
    while running:
        running = handle_events()

        sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(w_ptr), ctypes.byref(h_ptr))
        render(w_ptr.value, h_ptr.value, tex_id, start_x, start_y, base_w * scale, base_h * scale)

        sdl3.SDL_GL_SwapWindow(window)

    cleanup(window, gl_context, tex_id)


if __name__ == "__main__":
    main()

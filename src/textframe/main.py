import ctypes

import sdl3
from OpenGL import GL


def init_window(title: bytes, width: int, height: int):
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init failed: {sdl3.SDL_GetError().decode()}")

    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 1)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DOUBLEBUFFER, 1)

    window = sdl3.SDL_CreateWindow(
        title,
        width,
        height,
        sdl3.SDL_WINDOW_OPENGL | sdl3.SDL_WINDOW_RESIZABLE,
    )
    if not window:
        sdl3.SDL_Quit()
        raise RuntimeError(f"SDL_CreateWindow failed: {sdl3.SDL_GetError().decode()}")

    gl_context = sdl3.SDL_GL_CreateContext(window)
    if not gl_context:
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
        raise RuntimeError(f"SDL_GL_CreateContext failed: {sdl3.SDL_GetError().decode()}")

    sdl3.SDL_GL_MakeCurrent(window, gl_context)
    sdl3.SDL_GL_SetSwapInterval(1)

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


def render(width: int, height: int) -> None:
    setup_ortho(width, height)

    GL.glClearColor(0.12, 0.13, 0.16, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)


def cleanup(window, gl_context) -> None:
    sdl3.SDL_GL_DestroyContext(gl_context)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()


def main() -> None:
    width, height = 800, 600
    window, gl_context = init_window(b"TextFrame - OpenGL", width, height)

    w_ptr = ctypes.c_int(width)
    h_ptr = ctypes.c_int(height)

    running = True
    while running:
        running = handle_events()

        sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(w_ptr), ctypes.byref(h_ptr))
        render(w_ptr.value, h_ptr.value)

        sdl3.SDL_GL_SwapWindow(window)

    cleanup(window, gl_context)


if __name__ == "__main__":
    main()

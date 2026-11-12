import ctypes

import sdl3
from OpenGL import GL

from .styles import BG_COLOR, FRAME_COLOR, TEXT_COLOR_RGBA
from .text import create_text_texture, delete_text_texture, draw_text_texture


def init_window(title: bytes, width: int, height: int):
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init failed: {sdl3.SDL_GetError().decode()}")

    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 1)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DOUBLEBUFFER, 1)

    window = sdl3.SDL_CreateWindow(
        title, width, height, sdl3.SDL_WINDOW_OPENGL | sdl3.SDL_WINDOW_RESIZABLE
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


def handle_events(scale: float) -> tuple[bool, float]:
    """Обработка клавиш: Esc — выход, > (.) — масштаб x2, < (,) — масштаб /2."""
    event = sdl3.SDL_Event()
    while sdl3.SDL_PollEvent(ctypes.byref(event)):
        if event.type == sdl3.SDL_EVENT_QUIT:
            return False, scale

        if event.type == sdl3.SDL_EVENT_KEY_DOWN:
            scancode = event.key.scancode

            if scancode == sdl3.SDL_SCANCODE_ESCAPE:
                return False, scale

            if scancode == sdl3.SDL_SCANCODE_PERIOD:
                if scale < 16.0:
                    scale *= 2.0

            elif scancode == sdl3.SDL_SCANCODE_COMMA:
                if scale > 0.25:
                    scale /= 2.0

    return True, scale


def draw_solid_rect_border(x: float, y: float, width: float, height: float, thickness: float) -> None:
    """Рисует рамку заданной толщины через 4 прямоугольника."""
    GL.glBegin(GL.GL_QUADS)
    # Верхняя грань
    GL.glVertex2f(x, y)
    GL.glVertex2f(x + width, y)
    GL.glVertex2f(x + width, y + thickness)
    GL.glVertex2f(x, y + thickness)
    # Нижняя грань
    GL.glVertex2f(x, y + height - thickness)
    GL.glVertex2f(x + width, y + height - thickness)
    GL.glVertex2f(x + width, y + height)
    GL.glVertex2f(x, y + height)
    # Левая грань
    GL.glVertex2f(x, y + thickness)
    GL.glVertex2f(x + thickness, y + thickness)
    GL.glVertex2f(x + thickness, y + height - thickness)
    GL.glVertex2f(x, y + height - thickness)
    # Правая грань
    GL.glVertex2f(x + width - thickness, y + thickness)
    GL.glVertex2f(x + width, y + thickness)
    GL.glVertex2f(x + width, y + height - thickness)
    GL.glVertex2f(x + width - thickness, y + height - thickness)
    GL.glEnd()


def draw_double_frame(x: float, y: float, width: float, height: float, gap: float, thickness: float) -> None:
    """Рисует двойную рамку."""
    GL.glColor3f(*FRAME_COLOR)
    draw_solid_rect_border(x, y, width, height, thickness)
    inset = thickness + gap
    draw_solid_rect_border(x + inset, y + inset, width - 2 * inset, height - 2 * inset, thickness)


def render(
    width: int,
    height: int,
    tex_id: int,
    start_x: float,
    start_y: float,
    text_w: int,
    text_h: int,
    scale: float,
) -> None:
    setup_ortho(width, height)

    GL.glClearColor(*BG_COLOR, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    thickness = max(1.0, 2.0 * scale)
    frame_gap = max(2.0, 4.0 * scale)
    inner_pad = max(4.0, 10.0 * scale)

    total_offset = 2 * thickness + frame_gap + inner_pad
    frame_w = text_w + 2 * total_offset
    frame_h = text_h + 2 * total_offset

    draw_double_frame(start_x, start_y, frame_w, frame_h, frame_gap, thickness)
    draw_text_texture(tex_id, start_x + total_offset, start_y + total_offset, float(text_w), float(text_h))


def cleanup(window, gl_context, tex_id: int) -> None:
    delete_text_texture(tex_id)
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

    base_font_size = 32
    start_x = 80.0
    start_y = 80.0
    scale = 1.0

    tex_id, text_w, text_h = create_text_texture(text, int(base_font_size * scale), TEXT_COLOR_RGBA)

    w_ptr = ctypes.c_int(width)
    h_ptr = ctypes.c_int(height)

    running = True
    while running:
        running, new_scale = handle_events(scale)

        if new_scale != scale:
            scale = new_scale
            delete_text_texture(tex_id)
            tex_id, text_w, text_h = create_text_texture(text, int(base_font_size * scale), TEXT_COLOR_RGBA)

        sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(w_ptr), ctypes.byref(h_ptr))
        render(w_ptr.value, h_ptr.value, tex_id, start_x, start_y, text_w, text_h, scale)

        sdl3.SDL_GL_SwapWindow(window)

    cleanup(window, gl_context, tex_id)


if __name__ == "__main__":
    main()

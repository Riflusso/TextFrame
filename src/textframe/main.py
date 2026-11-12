import ctypes

import sdl3

from textframe.core.interfaces import IRenderer, ITexture
from textframe.opengl import create_renderer as create_opengl_renderer
from textframe.styles import BG_COLOR, FRAME_COLOR, TEXT_COLOR_RGBA
from textframe.text import create_text_texture
from textframe.vulkan import create_renderer as create_vulkan_renderer

BACKENDS = {
    "opengl": create_opengl_renderer,
    "vulkan": create_vulkan_renderer,
}


def create_app_window(
    renderer: IRenderer,
    backend_name: str,
    width: int,
    height: int,
    x: int | None = None,
    y: int | None = None,
):
    """Создает окно с нужными флагами рендерера и инициализирует графический контекст."""
    renderer.prepare_window_hints()

    titles = {"opengl": b"TextFrame - OpenGL", "vulkan": b"TextFrame - Vulkan"}
    title = titles.get(backend_name, b"TextFrame")
    flags = renderer.get_window_flags() | sdl3.SDL_WINDOW_RESIZABLE
    window = sdl3.SDL_CreateWindow(title, width, height, flags)
    if not window:
        raise RuntimeError(f"SDL_CreateWindow failed: {sdl3.SDL_GetError().decode()}")

    if x is not None and y is not None:
        sdl3.SDL_SetWindowPosition(window, x, y)

    try:
        renderer.init_context(window)
    except Exception:
        sdl3.SDL_DestroyWindow(window)
        raise

    return window


def get_greeting_text(window) -> str:
    """Возвращает текст в зависимости от активного флага окна."""
    flags = sdl3.SDL_GetWindowFlags(window)
    if flags & sdl3.SDL_WINDOW_OPENGL:
        return "Привет, OpenGL!"
    if flags & sdl3.SDL_WINDOW_VULKAN:
        return "Привет, Vulkan!"
    return "Привет!"


def handle_events(scale: float, current_backend: str) -> tuple[bool, float, str]:
    """Обработка клавиш: Esc — выход, > (.) — масштаб x2, < (,) — масштаб /2, Tab — сменить API."""
    event = sdl3.SDL_Event()
    next_backend = current_backend

    while sdl3.SDL_PollEvent(ctypes.byref(event)):
        if event.type == sdl3.SDL_EVENT_QUIT:
            return False, scale, next_backend

        if event.type == sdl3.SDL_EVENT_KEY_DOWN:
            scancode = event.key.scancode
            if scancode == sdl3.SDL_SCANCODE_ESCAPE:
                return False, scale, next_backend
            if scancode == sdl3.SDL_SCANCODE_PERIOD and scale < 16.0:
                scale *= 2.0
            elif scancode == sdl3.SDL_SCANCODE_COMMA and scale > 0.25:
                scale /= 2.0
            elif scancode == sdl3.SDL_SCANCODE_TAB:
                next_backend = "vulkan" if current_backend == "opengl" else "opengl"

    return True, scale, next_backend


def draw_solid_rect_border(
    renderer: IRenderer,
    x: float,
    y: float,
    width: float,
    height: float,
    thickness: float,
    color: tuple[float, float, float],
) -> None:
    """Рисует рамку через 4 прямоугольника, не зная о конкретном API."""
    renderer.fill_rect(x, y, width, thickness, color)  # Верхняя грань
    renderer.fill_rect(x, y + height - thickness, width, thickness, color)  # Нижняя грань
    renderer.fill_rect(x, y + thickness, thickness, height - 2 * thickness, color)  # Левая грань
    renderer.fill_rect(x + width - thickness, y + thickness, thickness, height - 2 * thickness, color)  # Правая


def draw_double_frame(
    renderer: IRenderer, x: float, y: float, width: float, height: float, gap: float, thickness: float
) -> None:
    draw_solid_rect_border(renderer, x, y, width, height, thickness, FRAME_COLOR)
    inset = thickness + gap
    draw_solid_rect_border(renderer, x + inset, y + inset, width - 2 * inset, height - 2 * inset, thickness, FRAME_COLOR)


def render(
    renderer: IRenderer,
    width: int,
    height: int,
    text_texture: ITexture,
    start_x: float,
    start_y: float,
    text_w: int,
    text_h: int,
    scale: float,
) -> None:
    renderer.begin_frame(width, height, BG_COLOR)

    thickness = max(1.0, 2.0 * scale)
    frame_gap = max(2.0, 4.0 * scale)
    inner_pad = max(4.0, 10.0 * scale)

    total_offset = 2 * thickness + frame_gap + inner_pad
    frame_w = text_w + 2 * total_offset
    frame_h = text_h + 2 * total_offset

    draw_double_frame(renderer, start_x, start_y, frame_w, frame_h, frame_gap, thickness)
    text_texture.draw(start_x + total_offset, start_y + total_offset, float(text_w), float(text_h))


def main() -> None:
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init failed: {sdl3.SDL_GetError().decode()}")

    width, height = 900, 600
    current_backend = "vulkan"
    renderer = BACKENDS[current_backend]()
    window = create_app_window(renderer, current_backend, width, height)

    base_font_size = 32
    start_x = 80.0
    start_y = 80.0
    scale = 1.0

    text = get_greeting_text(window)
    text_texture, text_w, text_h = create_text_texture(
        renderer, text, int(base_font_size * scale), TEXT_COLOR_RGBA
    )

    try:
        w_ptr = ctypes.c_int(width)
        h_ptr = ctypes.c_int(height)

        running = True
        while running:
            running, new_scale, new_backend = handle_events(scale, current_backend)

            # Горячее переключение графического API по нажатию Tab
            if new_backend != current_backend:
                win_x, win_y = ctypes.c_int(), ctypes.c_int()
                win_w, win_h = ctypes.c_int(), ctypes.c_int()
                sdl3.SDL_GetWindowPosition(window, ctypes.byref(win_x), ctypes.byref(win_y))
                sdl3.SDL_GetWindowSize(window, ctypes.byref(win_w), ctypes.byref(win_h))

                text_texture.destroy()
                renderer.shutdown()
                sdl3.SDL_DestroyWindow(window)

                current_backend = new_backend
                scale = new_scale
                renderer = BACKENDS[current_backend]()
                window = create_app_window(
                    renderer, current_backend, win_w.value, win_h.value, win_x.value, win_y.value
                )

                text = get_greeting_text(window)
                text_texture, text_w, text_h = create_text_texture(
                    renderer, text, int(base_font_size * scale), TEXT_COLOR_RGBA
                )

            # Обновление текстуры при изменении масштаба
            elif new_scale != scale:
                scale = new_scale
                text_texture.destroy()
                text_texture, text_w, text_h = create_text_texture(
                    renderer, text, int(base_font_size * scale), TEXT_COLOR_RGBA
                )

            sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(w_ptr), ctypes.byref(h_ptr))
            render(renderer, w_ptr.value, h_ptr.value, text_texture, start_x, start_y, text_w, text_h, scale)
            renderer.end_frame(window)
    finally:
        text_texture.destroy()
        renderer.shutdown()
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()


if __name__ == "__main__":
    main()

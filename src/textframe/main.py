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

WINDOW_TITLES = {
    "opengl": b"TextFrame - OpenGL",
    "vulkan": b"TextFrame - Vulkan",
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

    title = WINDOW_TITLES.get(backend_name, b"TextFrame")
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


def rebuild_text_texture(
    renderer: IRenderer,
    window,
    base_font_size: int,
    scale: float,
    old_texture: ITexture | None = None,
) -> tuple[ITexture, int, int]:
    """Удаляет старую текстуру текста (если есть) и создает новую с актуальным API и масштабом."""
    if old_texture is not None:
        old_texture.destroy()
    text = get_greeting_text(window)
    return create_text_texture(renderer, text, int(base_font_size * scale), TEXT_COLOR_RGBA)


def destroy_window_resources(
    window,
    renderer: IRenderer | None,
    text_texture: ITexture | None = None,
) -> None:
    """Освобождает текстуру, графический контекст и окно SDL3."""
    if text_texture is not None:
        text_texture.destroy()
    if renderer is not None:
        renderer.shutdown()
    if window is not None:
        sdl3.SDL_DestroyWindow(window)


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
    inner_height = height - 2 * thickness
    renderer.fill_rect(x, y, width, thickness, color)  # Верхняя грань
    renderer.fill_rect(x, y + height - thickness, width, thickness, color)  # Нижняя грань
    renderer.fill_rect(x, y + thickness, thickness, inner_height, color)  # Левая грань
    renderer.fill_rect(x + width - thickness, y + thickness, thickness, inner_height, color)  # Правая грань


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
    base_font_size = 32
    start_x, start_y = 80.0, 80.0
    scale = 1.0

    current_backend = "opengl"
    renderer: IRenderer | None = None
    window = None
    text_texture: ITexture | None = None

    try:
        renderer = BACKENDS[current_backend]()
        window = create_app_window(renderer, current_backend, width, height)
        text_texture, text_w, text_h = rebuild_text_texture(renderer, window, base_font_size, scale)

        w_ptr = ctypes.c_int(width)
        h_ptr = ctypes.c_int(height)

        running = True
        while running:
            running, new_scale, new_backend = handle_events(scale, current_backend)

            if new_backend != current_backend:
                win_x, win_y = ctypes.c_int(), ctypes.c_int()
                win_w, win_h = ctypes.c_int(), ctypes.c_int()
                sdl3.SDL_GetWindowPosition(window, ctypes.byref(win_x), ctypes.byref(win_y))
                sdl3.SDL_GetWindowSize(window, ctypes.byref(win_w), ctypes.byref(win_h))

                destroy_window_resources(window, renderer, text_texture)
                window, renderer, text_texture = None, None, None

                current_backend = new_backend
                scale = new_scale
                renderer = BACKENDS[current_backend]()
                window = create_app_window(
                    renderer, current_backend, win_w.value, win_h.value, win_x.value, win_y.value
                )
                text_texture, text_w, text_h = rebuild_text_texture(renderer, window, base_font_size, scale)

            elif new_scale != scale:
                scale = new_scale
                text_texture, text_w, text_h = rebuild_text_texture(
                    renderer, window, base_font_size, scale, text_texture
                )

            sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(w_ptr), ctypes.byref(h_ptr))
            render(renderer, w_ptr.value, h_ptr.value, text_texture, start_x, start_y, text_w, text_h, scale)
            renderer.end_frame(window)
    finally:
        destroy_window_resources(window, renderer, text_texture)
        sdl3.SDL_Quit()


if __name__ == "__main__":
    main()

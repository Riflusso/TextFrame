import ctypes
import importlib

import sdl3

from textframe.core.interfaces import IRenderer, ITexture
from textframe.styles import BG_COLOR, FRAME_COLOR, TEXT_COLOR_RGBA
from textframe.text import create_text_texture


def load_backend(name: str) -> IRenderer:
    """Подгружает 'textframe.opengl' или 'textframe.vulkan'."""
    module = importlib.import_module(f"textframe.{name}")
    return module.create_renderer()


def init_window(renderer: IRenderer, title: bytes, width: int, height: int):
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init failed: {sdl3.SDL_GetError().decode()}")

    renderer.prepare_window_hints()

    flags = renderer.get_window_flags() | sdl3.SDL_WINDOW_RESIZABLE
    window = sdl3.SDL_CreateWindow(title, width, height, flags)
    if not window:
        sdl3.SDL_Quit()
        raise RuntimeError(f"SDL_CreateWindow failed: {sdl3.SDL_GetError().decode()}")

    try:
        renderer.init_context(window)
    except Exception:
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
        raise

    return window


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
            if scancode == sdl3.SDL_SCANCODE_PERIOD and scale < 16.0:
                scale *= 2.0
            elif scancode == sdl3.SDL_SCANCODE_COMMA and scale > 0.25:
                scale /= 2.0

    return True, scale


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
    # Единственное место выбора графического API ("opengl" или "vulkan")
    renderer = load_backend("opengl")

    width, height = 900, 600
    window = init_window(renderer, b"TextFrame", width, height)

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

    text_texture, text_w, text_h = create_text_texture(
        renderer, text, int(base_font_size * scale), TEXT_COLOR_RGBA
    )

    w_ptr = ctypes.c_int(width)
    h_ptr = ctypes.c_int(height)

    running = True
    while running:
        running, new_scale = handle_events(scale)

        if new_scale != scale:
            scale = new_scale
            text_texture.destroy()
            text_texture, text_w, text_h = create_text_texture(
                renderer, text, int(base_font_size * scale), TEXT_COLOR_RGBA
            )

        sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(w_ptr), ctypes.byref(h_ptr))
        render(renderer, w_ptr.value, h_ptr.value, text_texture, start_x, start_y, text_w, text_h, scale)
        renderer.end_frame(window)

    text_texture.destroy()
    renderer.shutdown()
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()


if __name__ == "__main__":
    main()

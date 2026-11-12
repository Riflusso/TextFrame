import ctypes

import sdl3

from textframe.core.interfaces import IRenderer, ITexture

from .texture import VulkanTexture


class VulkanRenderer(IRenderer):
    def __init__(self):
        self.sdl_renderer = None

    def prepare_window_hints(self) -> None:
        pass

    def get_window_flags(self) -> int:
        return sdl3.SDL_WINDOW_VULKAN

    def init_context(self, window) -> None:
        # Принудительно запускаем 2D-рендерер SDL3 поверх Vulkan
        self.sdl_renderer = sdl3.SDL_CreateRenderer(window, b"vulkan")
        if not self.sdl_renderer:
            raise RuntimeError(f"SDL_CreateRenderer (vulkan) failed: {sdl3.SDL_GetError().decode()}")

        sdl3.SDL_SetRenderVSync(self.sdl_renderer, 1)
        sdl3.SDL_SetRenderDrawBlendMode(self.sdl_renderer, sdl3.SDL_BLENDMODE_BLEND)

    def begin_frame(self, width: int, height: int, bg_color: tuple[float, float, float]) -> None:
        r = int(bg_color[0] * 255)
        g = int(bg_color[1] * 255)
        b = int(bg_color[2] * 255)
        sdl3.SDL_SetRenderDrawColor(self.sdl_renderer, r, g, b, 255)
        sdl3.SDL_RenderClear(self.sdl_renderer)

    def fill_rect(
        self, x: float, y: float, width: float, height: float, color: tuple[float, float, float]
    ) -> None:
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
        sdl3.SDL_SetRenderDrawColor(self.sdl_renderer, r, g, b, 255)

        rect = sdl3.SDL_FRect(x, y, width, height)
        sdl3.SDL_RenderFillRect(self.sdl_renderer, ctypes.byref(rect))

    def create_texture(self, width: int, height: int, rgba_bytes: bytes) -> ITexture:
        return VulkanTexture(self.sdl_renderer, width, height, rgba_bytes)

    def end_frame(self, window) -> None:
        sdl3.SDL_RenderPresent(self.sdl_renderer)

    def shutdown(self) -> None:
        if self.sdl_renderer:
            sdl3.SDL_DestroyRenderer(self.sdl_renderer)
            self.sdl_renderer = None

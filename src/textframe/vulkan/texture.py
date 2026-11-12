import ctypes

import sdl3

from textframe.core.interfaces import ITexture


class VulkanTexture(ITexture):
    def __init__(self, sdl_renderer, width: int, height: int, rgba_bytes: bytes):
        self.sdl_renderer = sdl_renderer
        self.texture = sdl3.SDL_CreateTexture(
            sdl_renderer,
            sdl3.SDL_PIXELFORMAT_RGBA32,
            sdl3.SDL_TEXTUREACCESS_STATIC,
            width,
            height,
        )
        if not self.texture:
            raise RuntimeError(f"SDL_CreateTexture failed: {sdl3.SDL_GetError().decode()}")

        sdl3.SDL_SetTextureBlendMode(self.texture, sdl3.SDL_BLENDMODE_BLEND)

        # Копируем сырые RGBA-байты в текстуру
        pixel_buf = ctypes.create_string_buffer(rgba_bytes, len(rgba_bytes))
        sdl3.SDL_UpdateTexture(self.texture, None, pixel_buf, width * 4)

    def draw(self, x: float, y: float, width: float, height: float) -> None:
        dst = sdl3.SDL_FRect(x, y, width, height)
        sdl3.SDL_RenderTexture(self.sdl_renderer, self.texture, None, ctypes.byref(dst))

    def destroy(self) -> None:
        if self.texture:
            sdl3.SDL_DestroyTexture(self.texture)
            self.texture = None

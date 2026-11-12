from abc import ABC, abstractmethod


class ITexture(ABC):
    @abstractmethod
    def draw(self, x: float, y: float, width: float, height: float) -> None:
        pass

    @abstractmethod
    def destroy(self) -> None:
        pass


class IRenderer(ABC):
    @abstractmethod
    def prepare_window_hints(self) -> None:
        """Настраивает атрибуты SDL3 перед созданием окна (например, версию GL)."""
        pass

    @abstractmethod
    def get_window_flags(self) -> int:
        """Возвращает флаг окна (SDL_WINDOW_OPENGL или SDL_WINDOW_VULKAN)."""
        pass

    @abstractmethod
    def init_context(self, window) -> None:
        """Создает графический контекст и настраивает blending/vsync."""
        pass

    @abstractmethod
    def begin_frame(self, width: int, height: int, bg_color: tuple[float, float, float]) -> None:
        """Настраивает viewport/проекцию и очищает экран."""
        pass

    @abstractmethod
    def fill_rect(
        self, x: float, y: float, width: float, height: float, color: tuple[float, float, float]
    ) -> None:
        """Рисует закрашенный прямоугольник (используется для граней рамки)."""
        pass

    @abstractmethod
    def create_texture(self, width: int, height: int, rgba_bytes: bytes) -> ITexture:
        """Загружает сырые RGBA-байты в видеопамять."""
        pass

    @abstractmethod
    def end_frame(self, window) -> None:
        """Выводит кадр на экран (SwapBuffers / Present)."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Освобождает графический контекст."""
        pass

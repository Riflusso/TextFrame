def hex_to_rgb_float(hex_color: str) -> tuple[float, float, float]:
    """Переводит HEX (#RRGGBB) в кортеж (r, g, b) со значениями 0.0..1.0 для OpenGL."""
    h = hex_color.lstrip("#")
    return (
        int(h[0:2], 16) / 255.0,
        int(h[2:4], 16) / 255.0,
        int(h[4:6], 16) / 255.0,
    )


def hex_to_rgba_int(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Переводит HEX (#RRGGBB) в кортеж (r, g, b, a) со значениями 0..255 для Pillow."""
    h = hex_color.lstrip("#")
    return (
        int(h[0:2], 16),
        int(h[2:4], 16),
        int(h[4:6], 16),
        alpha,
    )


# Палитра Catppuccin Mocha (основные цвета)
CATPPUCCIN_MOCHA = {
    "base": "#1e1e2e",       # Основной фон
    "mantle": "#181825",     # Темный фон
    "crust": "#11111b",      # Самый темный фон
    "surface0": "#313244",   # Поверхности / элементы
    "text": "#cdd6f4",       # Основной текст
    "subtext0": "#a6adc8",   # Второстепенный текст
    "lavender": "#b4befe",   # Лавандовый акцент
    "blue": "#89b4fa",       # Синий акцент
    "mauve": "#cba6f7",      # Фиолетовый акцент (используем для рамки)
    "pink": "#f5c2e7",       # Розовый акцент
    "peach": "#fab387",      # Персиковый акцент
    "green": "#a6e3a1",      # Зеленый акцент
}

# Готовые цвета для рендера
BG_COLOR = hex_to_rgb_float(CATPPUCCIN_MOCHA["base"])
FRAME_COLOR = hex_to_rgb_float(CATPPUCCIN_MOCHA["mauve"])
TEXT_COLOR_RGBA = hex_to_rgba_int(CATPPUCCIN_MOCHA["text"])

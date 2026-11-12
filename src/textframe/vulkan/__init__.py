from .renderer import VulkanRenderer


def create_renderer() -> VulkanRenderer:
    return VulkanRenderer()

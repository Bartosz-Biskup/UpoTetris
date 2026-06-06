from abc import abstractmethod, ABC
from pygame import Surface
import time
import pygame
from typing import Literal, Optional, Callable, Any
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
from colors import Color


BASE_DIR = Path(__file__).parent.parent

DEFAULT_FONT_PATH = BASE_DIR / "assets" / "Adumu.ttf"
DEFAULT_FONT_SIZE = 18

Anchor = Literal[
    "center",
    "top_left", "top_center", "top_right",
    "middle_left", "middle_right",
    "bottom_left", "bottom_center", "bottom_right"
]


def _load_font(size: int, path: str | None) -> pygame.font.Font:
    try:
        return pygame.font.Font(path or DEFAULT_FONT_PATH, size)
    except FileNotFoundError:
        return pygame.font.SysFont("monospace", size)


class UiElement(ABC):
    @abstractmethod
    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        ...

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        ...


class Layout:
    def __init__(self):
        self.elements = []

    def add_element(self, element: UiElement, position: tuple[int, int], anchor: Anchor):
        self.elements.append({
            "element": element,
            "position": position,
            "anchor": anchor
        })

    def render(self, surface: Surface):
        for item in self.elements:
            element = item["element"]
            x, y = item["position"]
            anchor = item["anchor"]
            w, h = element.get_size()

            offsets = {
                "center":        (w // 2,  h // 2),
                "top_left":      (0,       0),
                "top_center":    (w // 2,  0),
                "top_right":     (w,       0),
                "middle_left":   (0,       h // 2),
                "middle_right":  (w,       h // 2),
                "bottom_left":   (0,       h),
                "bottom_center": (w // 2,  h),
                "bottom_right":  (w,       h),
            }

            ox, oy = offsets[anchor]
            element.draw(surface, (x - ox, y - oy))

    def clear(self) -> None:
        self.elements = []


class Label(UiElement):
    def __init__(self, text: str, color=(230, 230, 230), font_size=DEFAULT_FONT_SIZE, font_path=DEFAULT_FONT_PATH):
        self.text = text
        self._font = _load_font(font_size, font_path)
        self._color = color
        self.set_text(text)

    @lru_cache(maxsize=1)
    def _get_surface(self, text: str, color: tuple[int, int, int]) -> Surface:
        return self._font.render(text, True, color)

    def set_text(self, text: str):
        self.text = text

    def get_size(self):
        return self._get_surface(self.text, self._color).get_size()

    def draw(self, surface, pos):
        surface.blit(self._get_surface(self.text, self._color), pos)


class BlinkingLabel(Label):
    def __init__(
        self,
        text: str,
        color: tuple[int, int, int] = (230, 230, 230),
        blink_color: tuple[int, int, int] = (0, 255, 127),
        blink_duration_ms: int = 300,
        font_size: int = DEFAULT_FONT_SIZE,
        font_path: str = DEFAULT_FONT_PATH,
    ) -> None:
        super().__init__(text, color, font_size, font_path)
        self._default_color = color
        self._blink_color = blink_color
        self._blink_duration_ms = blink_duration_ms
        self._blink_timer: int | None = None

    def blink(self) -> None:
        self._blink_timer = pygame.time.get_ticks()
        self._color = self._blink_color

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        if self._blink_timer is not None:
            elapsed = pygame.time.get_ticks() - self._blink_timer
            if elapsed >= self._blink_duration_ms:
                self._blink_timer = None
                self._color = self._default_color

        super().draw(surface, pos)


class TimeLabel(UiElement):
    def __init__(self, countdown: int | None = None, color=(230, 230, 230), font_size=DEFAULT_FONT_SIZE,
                 font_path=DEFAULT_FONT_PATH):
        self._font = _load_font(font_size, font_path)
        self._color = color
        self.countdown = countdown
        self._start_time = time.time()

    def reset(self):
        self._start_time = time.time()

    @property
    def finished(self):
        return self.countdown is not None and self._elapsed() >= self.countdown

    @property
    def time_elapsed(self) -> float:
        return self._elapsed()

    def _elapsed(self):
        return time.time() - self._start_time

    def _text(self):
        t = int(min(self._elapsed(), self.countdown) if self.countdown else self._elapsed())
        s = self.countdown - t if self.countdown else t
        return f"{s // 60:02d}:{s % 60:02d}"

    def get_size(self):
        return self._font.size(self._text())

    def draw(self, surface, pos):
        surface.blit(self._font.render(self._text(), True, self._color), pos)


@dataclass(frozen=True)
class FrameStyle:
    fill: Optional[tuple] = None
    border_color: Optional[tuple] = None
    border_thickness: int = 2
    border_radius: int = 0


class Frame(UiElement):
    def __init__(self, size: tuple[int, int], style: FrameStyle = None):
        self._size = size
        self.style = style or FrameStyle()
        self._layout = Layout()

    def add_widget(self, element: UiElement, position: tuple[int, int], anchor: Anchor):
        self._layout.add_element(element, position, anchor)

    def get_size(self) -> tuple[int, int]:
        return self._size

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        x, y = pos
        w, h = self._size
        rect = pygame.Rect(x, y, w, h)

        if self.style.fill:
            pygame.draw.rect(surface, self.style.fill, rect, border_radius=self.style.border_radius)

        old_clip = surface.get_clip()
        surface.set_clip(rect)
        self._layout.render(surface)          # Layout already knows how to draw everything
        surface.set_clip(old_clip)

        if self.style.border_color:
            pygame.draw.rect(surface,
                             self.style.border_color,
                             rect,
                             width=self.style.border_thickness,
                             border_radius=self.style.border_radius)

    def clear_layout(self) -> None:
        self._layout.clear()


class Rect(UiElement):
    def __init__(self, size: tuple[int, int], color: tuple):
        self._size = size
        self.color = color

    def get_size(self) -> tuple[int, int]:
        return self._size

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        x, y = pos
        w, h = self._size
        pygame.draw.rect(surface, self.color, pygame.Rect(x, y, w, h))


class Image(UiElement):
    def __init__(self, path: Path, scale: float = 1.0) -> None:
        surface = pygame.image.load(path).convert_alpha()
        w, h = surface.get_size()
        self._surface = pygame.transform.scale(surface, (max(1, int(w * scale)), max(1, int(h * scale))))

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        surface.blit(self._surface, pos)

    def get_size(self) -> tuple[int, int]:
        return self._surface.get_size()


class Button(UiElement):
    def __init__(self,
                 text: str,
                 function: Callable[[], Any],
                 text_color: Color,
                 button_size: tuple[int, int] = (70, 30),
                 border_color: Color = (255, 255, 255),
                 border_color_hover: Color = (127, 127, 127),
                 border_color_pressed: Color = (0, 127, 127)) -> None:
        super().__init__()

        self.function = function
        self._text_color = text_color
        self._button_size = button_size
        self._border_color = border_color
        self._border_color_hover = border_color_hover
        self._border_color_pressed = border_color_pressed

        self._current_state: Literal['none', 'press', 'hover'] = 'none'

        self._label: Label | None = None
        self._text = text

        frame_style: FrameStyle = FrameStyle(fill=None,
                                             border_color=self._border_color,
                                             border_thickness=3,
                                             border_radius=5)
        self._frame: Frame = Frame(self._button_size, frame_style)
        self._add_label_to_frame()

    def _add_label_to_frame(self) -> None:
        self._frame.add_widget(self._label,
                               (self._button_size[0] // 2, self._button_size[1] // 2),
                               'center')

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._label = Label(value, self._text_color)
        self._frame.clear_layout()
        self._add_label_to_frame()
        self.text = value

    def get_size(self) -> tuple[int, int]:
        return self._button_size

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        self._tick()
        self._frame.draw(surface, pos)

    def _tick(self) -> None:
        ...




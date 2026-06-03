from dataclasses import dataclass
from ui_elements import UiElement, Image
import pygame
from pygame import Surface
from ui_elements import UiElement


@dataclass
class BlinkConfig:
    on_ms: int = 500
    off_ms: int = 250


class Menu(UiElement):
    def __init__(
        self,
        items: list[Image],
        cursor_size: tuple[int, int] = (12, 40),
        cursor_color: tuple[int, int, int] = (255, 255, 255),
        cursor_blink: BlinkConfig | None = None,
        item_gap: int = -30,
        cursor_gap: int = 16,
        cursor_offset_y: int = 0
    ) -> None:
        self._items = items
        self._cursor_gap = cursor_gap
        self._item_gap = item_gap
        self._cursor_offset_y = cursor_offset_y

        item_h = items[0].get_size()[1] if items else cursor_size[1]

        self._cursor = Caret(
            size=cursor_size,
            shift_amount=item_h + item_gap,
            item_count=len(items),
            color=cursor_color,
            blink=cursor_blink or BlinkConfig(),
        )

    def tick(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._cursor.shift(-1)
                elif event.key == pygame.K_DOWN:
                    self._cursor.shift(1)

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        x, y = pos
        cursor_w, cursor_h = self._cursor.get_size()
        item_h = self._items[0].get_size()[1] if self._items else 0
        cursor_y = y + (item_h - cursor_h) // 2
        self._cursor.draw(surface, (x + 10, cursor_y + self._cursor_offset_y))

        item_x = x + cursor_w + self._cursor_gap
        current_y = y
        for item in self._items:
            item.draw(surface, (item_x, current_y))
            current_y += item.get_size()[1] + self._item_gap

    def get_size(self) -> tuple[int, int]:
        cursor_w, _ = self._cursor.get_size()
        item_w = max((item.get_size()[0] for item in self._items), default=0)
        total_h = sum(item.get_size()[1] for item in self._items)
        total_h += self._item_gap * (len(self._items) - 1)
        return cursor_w + self._cursor_gap + item_w, total_h

    @property
    def selected_index(self) -> int:
        return self._cursor.index


class Caret(UiElement):
    def __init__(
        self,
        size: tuple[int, int],
        shift_amount: int,
        item_count: int,
        color: tuple[int, int, int] = (255, 255, 255),
        blink: BlinkConfig | None = None,
    ) -> None:
        self._width, self._height = size
        self._shift_amount = shift_amount
        self._item_count = item_count
        self._color = color
        self._blink = blink or BlinkConfig()

        self._index: int = 0
        self._blink_timer: int = pygame.time.get_ticks()
        self._visible: bool = True

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        if not self._is_visible_now():
            return
        x, y = pos
        pygame.draw.rect(
            surface,
            self._color,
            (x, y + (self._index + 1) * self._shift_amount, self._width, self._height),
        )

    def get_size(self) -> tuple[int, int]:
        total_height = self._height + (self._item_count - 1) * self._shift_amount
        return self._width, total_height

    def shift(self, delta: int) -> None:
        """
        Move the cursor by delta steps. Positive = down, negative = up.
        Clamps silently at both ends.
        """
        self._index = max(0, min(self._item_count - 1, self._index + delta))
        self._reset_blink()

    @property
    def index(self) -> int:
        return self._index

    def _is_visible_now(self) -> bool:
        now = pygame.time.get_ticks()
        elapsed = now - self._blink_timer
        duration = self._blink.on_ms if self._visible else self._blink.off_ms
        if elapsed >= duration:
            self._visible = not self._visible
            self._blink_timer = now
        return self._visible

    def _reset_blink(self) -> None:
        self._visible = True
        self._blink_timer = pygame.time.get_ticks()

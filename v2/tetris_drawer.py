from dataclasses import dataclass
from tetris_game import TetrisGrid
import pygame
from pygame import Surface
from colors import Color
from tetris_game import TetrisGame
from ui_elements import UiElement


@dataclass(frozen=True)
class TetrisDrawerSettings:
    cell_size_px: int
    cell_offset: int
    hide_first: int
    grid_bg_color: Color
    empty_cell_color: Color


DEFAULT_SETTINGS: TetrisDrawerSettings = TetrisDrawerSettings(cell_size_px=25,
                                                              cell_offset=3,
                                                              hide_first=0,
                                                              grid_bg_color=(0, 0, 0),
                                                              empty_cell_color=(100, 100, 100))


class TetrisDrawer(UiElement):
    def __init__(self,
                 tetris_game: TetrisGame,
                 settings: TetrisDrawerSettings) -> None:
        self.tetris_game = tetris_game
        self.settings = settings

    def get_size(self) -> tuple[int, int]:
        grid: TetrisGrid = self.tetris_game.snapshot.grid

        visible_rows = grid.size_y - self.settings.hide_first
        visible_cols = grid.size_x

        width = visible_cols * self.settings.cell_size_px + (visible_cols - 1) * self.settings.cell_offset
        height = visible_rows * self.settings.cell_size_px + (visible_rows - 1) * self.settings.cell_offset

        return width, height

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        grid: TetrisGrid = self.tetris_game.snapshot.grid
        for y in range(self.settings.hide_first, grid.size_y):
            for x in range(grid.size_x):
                cell_pos = self._calculate_cell_position(x, y, pos)
                color = grid.get_cell((x, y))
                self._draw_cell(surface, cell_pos, color)

        for row_idx, row in enumerate(self.tetris_game.current_piece.current_shape):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue
                x = self.tetris_game.current_piece.pos[0] + col_idx
                y = self.tetris_game.current_piece.pos[1] + row_idx
                if y >= self.settings.hide_first:
                    cell_pos = self._calculate_cell_position(x, y, pos)
                    self._draw_cell(surface, cell_pos, self.tetris_game.current_piece.color)

    def _draw_cell(self, surface: Surface, pos: tuple[int, int], color: tuple[int, int, int] | None) -> None:
        draw_color = color if color else self.settings.empty_cell_color
        pygame.draw.rect(surface, draw_color,
                         (*pos, self.settings.cell_size_px, self.settings.cell_size_px))

    def _calculate_cell_position(self, x: int, y: int, origin: tuple[int, int]) -> tuple[int, int]:
        x_pos = origin[0] + x * (self.settings.cell_size_px + self.settings.cell_offset)
        y_pos = origin[1] + (y - self.settings.hide_first) * (self.settings.cell_size_px + self.settings.cell_offset)
        return x_pos, y_pos

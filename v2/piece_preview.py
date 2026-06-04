import pygame
from ui_elements import UiElement, Frame, FrameStyle
from pygame import Surface
from typing import Optional
from pieces import Piece
from dataclasses import dataclass
from tetris_game import TetrisGame


@dataclass
class PiecePreviewStyle:
    cell_size: int
    cell_offset: int
    frame_style: FrameStyle = FrameStyle()


DEFAULT_PIECE_PREVIEW_STYLE = PiecePreviewStyle(cell_size=30,
                                                cell_offset=3,
                                                frame_style=FrameStyle(fill=None,
                                                                       border_color=(255, 255, 255),
                                                                    border_radius=5))


class PiecePreview(UiElement):
    def __init__(self,
                 size: tuple[int, int],
                 tetris_game: TetrisGame,
                 style: PiecePreviewStyle = DEFAULT_PIECE_PREVIEW_STYLE):
        self._size = size
        self._tetris_game = tetris_game
        self.style = style
        self._piece: Optional[Piece] = None
        self._frame = Frame(size, style.frame_style)

    def get_size(self) -> tuple[int, int]:
        return self._size

    def draw(self, surface: Surface, pos: tuple[int, int]) -> None:
        self._frame.draw(surface, pos)

        self._piece = self._tetris_game.snapshot.next_piece

        shape = self._piece.current_shape
        step = self.style.cell_size + self.style.cell_offset

        shape_cols = len(shape[0])
        shape_rows = len(shape)

        fw, fh = self._size
        ox = pos[0] + (fw - shape_cols * step) // 2
        oy = pos[1] + (fh - shape_rows * step) // 2

        for row_i, row in enumerate(shape):
            for col_i, cell_val in enumerate(row):
                if cell_val:
                    pygame.draw.rect(
                        surface,
                        self._piece.color,
                        pygame.Rect(ox + col_i * step, oy + row_i * step, self.style.cell_size, self.style.cell_size)
                    )
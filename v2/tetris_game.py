from dataclasses import dataclass
import pieces
from pieces import Piece
from grid import TetrisGrid
import colors
from colors import Color
from typing import Literal


GameStatuses = Literal["Not started", "Running", "Lost"]


@dataclass(frozen=True)
class TetrisGameSettings:
    grid_size: tuple[int, int]
    available_colors: list[Color]
    available_pieces: list[pieces.PieceDefinition]
    tick_every: int = 60
    # death_line: int


class TetrisGame:
    def __init__(self,
                 settings: TetrisGameSettings) -> None:
        self.settings = settings

        self.grid: TetrisGrid = TetrisGrid(self.settings.grid_size)
        self.game_status: GameStatuses = "Not started"

        self.piece_factory: pieces.PieceFactory = pieces.PieceFactory(self.settings.available_pieces,
                                                                      self.settings.available_colors,
                                                                      self.settings.grid_size[0])
        self.current_piece: Piece = self.piece_factory.spawn()
        self.next_piece: Piece = self.piece_factory.spawn()

    def _is_valid(self, piece: Piece) -> bool:
        for row_idx, row in enumerate(piece.current_shape):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                x = piece.pos[0] + col_idx
                y = piece.pos[1] + row_idx

                if y < 0:
                    if x < 0 or x >= self.grid.size_x:
                        return False
                    continue

                if not self.grid.valid_cell((x, y)):
                    return False

                if self.grid.get_cell((x, y)) is not None:
                    return False

        return True

    def _lock(self) -> None:
        for row_idx, row in enumerate(self.current_piece.current_shape):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                x = self.current_piece.pos[0] + col_idx
                y = self.current_piece.pos[1] + row_idx

                self.grid.set_cell((x, y), self.current_piece.color)

    def _clear_lines(self) -> int:
        cleared = 0
        row = self.grid.size_y - 1
        while row >= 0:
            if all(self.grid.get_cell((x, row)) is not None for x in range(self.grid.size_x)):
                self.grid.clear_row(row)
                cleared += 1
            else:
                row -= 1

        return cleared

    def _advance(self) -> None:
        self.current_piece, self.next_piece = self.next_piece, self.piece_factory.spawn()
        if not self._is_valid(self.current_piece):
            self.game_status = 'Lost'

    def tick(self) -> int:
        if self.game_status == 'Lost':
            return 0

        candidate: Piece = self.current_piece.move_down()
        if self._is_valid(candidate):
            self.current_piece = candidate

        number_cleared: int = 0
        if not self._is_valid(self.current_piece.move_down()):
            self._lock()
            number_cleared = self._clear_lines()
            self._advance()

        return number_cleared

    def move_left(self) -> None:
        if self.game_status != 'Running':
            return
        candidate = self.current_piece.move_left()
        if self._is_valid(candidate):
            self.current_piece = candidate

    def move_right(self) -> None:
        if self.game_status != 'Running':
            return
        candidate = self.current_piece.move_right()
        if self._is_valid(candidate):
            self.current_piece = candidate

    def rotate(self) -> None:
        if self.game_status != 'Running':
            return
        candidate = self.current_piece.next_rotation()
        if self._is_valid(candidate):
            self.current_piece = candidate

    def hard_drop(self) -> None:
        candidate: Piece = self.current_piece.move_down()
        while self._is_valid(candidate):
            self.current_piece = candidate
            candidate: Piece = self.current_piece.move_down()

    def start(self) -> None:
        if self.game_status != 'Not started':
            raise ValueError('The game has already started')
        self.game_status = 'Running'


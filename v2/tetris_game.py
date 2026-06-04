from dataclasses import dataclass
import pieces
from pieces import Piece
from grid import TetrisGrid
from colors import Color
from typing import Literal


GameStatuses = Literal["Not started", "Running", "Lost"]


@dataclass(frozen=True)
class TetrisGameSettings:
    grid_size: tuple[int, int]
    available_colors: list[Color]
    available_pieces: list[pieces.PieceDefinition]
    tick_every: int = 60


@dataclass(frozen=True)
class GameState:
    current_piece: Piece
    next_piece: Piece
    grid: TetrisGrid
    lines_cleared: int
    pieces_dropped: int
    game_status: GameStatuses


class TetrisGame:
    def __init__(self,
                 settings: TetrisGameSettings) -> None:
        self._settings = settings

        self._grid: TetrisGrid = TetrisGrid(self._settings.grid_size)
        self._game_status: GameStatuses = "Not started"

        self._piece_factory: pieces.PieceFactory = pieces.PieceFactory(self._settings.available_pieces,
                                                                       self._settings.available_colors,
                                                                       self._settings.grid_size[0])
        self.current_piece: Piece = self._piece_factory.spawn()
        self.next_piece: Piece = self._piece_factory.spawn()

        self._total_lines_cleared: int = 0
        self._total_pieces_dropped: int = 0

        self._game_snapshot: GameState = self._get_game_snapshot()

    def _get_game_snapshot(self) -> GameState:
        """
        Generated every tick to avoid generating every time an external function asks for it
        """

        return GameState(self.current_piece,
                         self.next_piece,
                         self._grid,
                         self._total_lines_cleared,
                         self._total_pieces_dropped,
                         self._game_status)

    @property
    def snapshot(self) -> GameState:
        return self._game_snapshot

    def _is_valid(self, piece: Piece) -> bool:
        for row_idx, row in enumerate(piece.current_shape):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                x = piece.pos[0] + col_idx
                y = piece.pos[1] + row_idx

                if y < 0:
                    if x < 0 or x >= self._grid.size_x:
                        return False
                    continue

                if not self._grid.valid_cell((x, y)):
                    return False

                if self._grid.get_cell((x, y)) is not None:
                    return False

        return True

    def _lock(self) -> None:
        for row_idx, row in enumerate(self.current_piece.current_shape):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                x = self.current_piece.pos[0] + col_idx
                y = self.current_piece.pos[1] + row_idx

                self._grid.set_cell((x, y), self.current_piece.color)

    def _clear_lines(self) -> int:
        cleared = 0
        row = self._grid.size_y - 1
        while row >= 0:
            if all(self._grid.get_cell((x, row)) is not None for x in range(self._grid.size_x)):
                self._grid.clear_row(row)
                cleared += 1
            else:
                row -= 1

        return cleared

    def _advance(self) -> None:
        self.current_piece, self.next_piece = self.next_piece, self._piece_factory.spawn()
        if not self._is_valid(self.current_piece):
            self._game_status = 'Lost'
            return

        self._total_pieces_dropped += 1

    def tick(self) -> None:
        if self._game_status == 'Lost':
            return

        candidate: Piece = self.current_piece.move_down()
        if self._is_valid(candidate):
            self.current_piece = candidate

        number_cleared: int = 0
        if not self._is_valid(self.current_piece.move_down()):
            self._lock()
            number_cleared = self._clear_lines()
            self._advance()

        self._total_lines_cleared += number_cleared
        self._game_snapshot = self._get_game_snapshot()

    def move_left(self) -> None:
        if self._game_status != 'Running':
            return
        candidate = self.current_piece.move_left()
        if self._is_valid(candidate):
            self.current_piece = candidate

    def move_right(self) -> None:
        if self._game_status != 'Running':
            return
        candidate = self.current_piece.move_right()
        if self._is_valid(candidate):
            self.current_piece = candidate

    def rotate(self) -> None:
        if self._game_status != 'Running':
            return
        candidate = self.current_piece.next_rotation()
        if self._is_valid(candidate):
            self.current_piece = candidate

    def hard_drop(self) -> None:
        candidate: Piece = self.current_piece.move_down()
        while self._is_valid(candidate):
            self.current_piece = candidate
            candidate: Piece = self.current_piece.move_down()
        self.tick()

    def start(self) -> None:
        if self._game_status != 'Not started':
            raise ValueError('The game has already started')
        self._game_status = 'Running'

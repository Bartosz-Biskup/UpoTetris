from pieces import Piece
from grid import TetrisGrid
from colors import Color
from pieces import PieceDefinition, PieceFactory
from dataclasses import dataclass


class TetrisExtension:
    """
    TetrisExtension can be passed and is called directly by TetrisGameEngine, that way we can directly influence some
    of engine's behaviours.
    """
    def is_valid(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece) -> bool:
        return True

    def lock(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece) -> bool:
        return True

    def clear_lines(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece,
                 cleared: int) -> None:
        ...

    def advance(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece) -> None:
        ...

    def tick(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece) -> None:
        ...

    def move_left(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece,
                 candidate: Piece) -> None:
        ...

    def move_right(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece,
                 candidate: Piece) -> None:
        ...

    def rotate(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece,
                 candidate: Piece) -> None:
        ...

    def hard_drop(self,
                 grid: TetrisGrid,
                 game_on: bool,
                 current_piece: Piece,
                 next_piece: Piece,
                 candidate: Piece) -> None:
        ...


class TetrisGameEngine:
    def __init__(self,
                 grid_size: tuple[int, int],
                 piece_factory: PieceFactory,
                 level_extensions: list[TetrisExtension]) -> None:
        self.grid: TetrisGrid = TetrisGrid(grid_size)
        self.level_extensions = level_extensions
        self.game_on: bool = True

        self._piece_factory = piece_factory
        self.current_piece: Piece = self._piece_factory.spawn()
        self.next_piece: Piece = self._piece_factory.spawn()

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

        for extension in self.level_extensions:
            if not extension.is_valid(self.grid, self.game_on, self.current_piece, self.next_piece):
                return False

        return True

    def _lock(self) -> None:
        for extension in self.level_extensions:
            if not extension.lock(self.grid, self.game_on, self.current_piece, self.next_piece):
                return None

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

        for extension in self.level_extensions:
            extension.clear_lines(self.grid, self.game_on, self.current_piece, self.next_piece, cleared)
        return cleared

    def _advance(self) -> None:
        self.current_piece, self.next_piece = self.next_piece, self._piece_factory.spawn()

        for extension in self.level_extensions:
            extension.advance(self.grid, self.game_on, self.current_piece, self.next_piece)

        if not self._is_valid(self.current_piece):
            self.game_on = False
            return

    def tick(self) -> None:
        if not self.game_on:
            return

        candidate: Piece = self.current_piece.move_down()
        if self._is_valid(candidate):
            self.current_piece = candidate

        if not self._is_valid(self.current_piece.move_down()):
            self._lock()
            self._clear_lines()
            self._advance()

        for extension in self.level_extensions:
            extension.tick(self.grid, self.game_on, self.current_piece, self.next_piece)

    def move_left(self) -> None:
        if not self.game_on:
            return
        candidate = self.current_piece.move_left()
        if self._is_valid(candidate):
            self.current_piece = candidate

        for extension in self.level_extensions:
            extension.move_left(self.grid, self.game_on, self.current_piece, self.next_piece, candidate)

    def move_right(self) -> None:
        if not self.game_on:
            return
        candidate = self.current_piece.move_right()
        if self._is_valid(candidate):
            self.current_piece = candidate

        for extension in self.level_extensions:
            extension.move_right(self.grid, self.game_on, self.current_piece, self.next_piece, candidate)

    def rotate(self) -> None:
        if not self.game_on:
            return
        candidate = self.current_piece.next_rotation()
        if self._is_valid(candidate):
            self.current_piece = candidate

        for extension in self.level_extensions:
            extension.rotate(self.grid, self.game_on, self.current_piece, self.next_piece, candidate)

    def hard_drop(self) -> None:
        if not self.game_on:
            return
        candidate: Piece = self.current_piece.move_down()
        while self._is_valid(candidate):
            self.current_piece = candidate
            candidate: Piece = self.current_piece.move_down()
        self.tick()

        for extension in self.level_extensions:
            extension.hard_drop(self.grid, self.game_on, self.current_piece, self.next_piece, candidate)


class ScoreKeeper(TetrisExtension):
    """
    Stores score as float internally to get more precision in score calculations.
    """
    def __init__(self,
                 score_added_per_lock: float = 2,
                 score_added_per_tick: float = 0.5,
                 score_added_per_hard_drop: float = 4,
                 score_added_per_cleared_line: float = 200) -> None:
        self._score: float = 0

        self.score_added_per_lock = score_added_per_lock
        self.score_added_per_tick = score_added_per_tick
        self.score_added_per_hard_drop = score_added_per_hard_drop
        self.score_added_per_cleared_line = score_added_per_cleared_line

        self._lines_cleared_last_tick: int = 0

    @property
    def score(self) -> int:
        return int(self._score)

    def lock(self,
             grid: TetrisGrid,
             game_on: bool,
             current_piece: Piece,
             next_piece: Piece) -> bool:
        self._score += self.score_added_per_lock
        return True

    def tick(self,
             grid: TetrisGrid,
             game_on: bool,
             current_piece: Piece,
             next_piece: Piece) -> None:
        self._score += self.score_added_per_tick

    def hard_drop(self,
             grid: TetrisGrid,
             game_on: bool,
             current_piece: Piece,
             next_piece: Piece,
             candidate: Piece) -> None:
        self._score += self.score_added_per_hard_drop

    def clear_lines(self,
                  grid: TetrisGrid,
                  game_on: bool,
                  current_piece: Piece,
                  next_piece: Piece,
                  cleared: int) -> None:
        self._score += self.score_added_per_cleared_line * cleared
        self._lines_cleared_last_tick = cleared

    def get_lines_cleared_last_tick(self) -> int:
        return self._lines_cleared_last_tick


@dataclass(frozen=True)
class TetrisGameSettings:
    grid_size: tuple[int, int]
    available_pieces: list[PieceDefinition]
    available_colors: list[Color]
    game_speed: int
    extensions: list[TetrisExtension]


class TetrisGame:
    def __init__(self, settings: TetrisGameSettings) -> None:
        self.grid_size = settings.grid_size
        self.available_pieces = settings.available_pieces
        self.available_colors = settings.available_colors
        self.game_speed = settings.game_speed

        self._score_keeper: ScoreKeeper = ScoreKeeper()
        self._extensions = settings.extensions
        self._extensions.append(self._score_keeper)

        self._tetris_game: TetrisGameEngine = TetrisGameEngine(self.grid_size,
                                                               PieceFactory(self.available_pieces,
                                                                            self.available_colors,
                                                                            self.grid_size[0]),
                                                               self._extensions)

        self._tick_count: int = 0

    def tick(self) -> None:
        self._tick_count += 1

        if self._tick_count % self.game_speed == 0:
            self._tetris_game.tick()

    def move_left(self) -> None:
        self._tetris_game.move_left()

    def move_right(self) -> None:
        self._tetris_game.move_right()

    def hard_drop(self) -> None:
        self._tetris_game.hard_drop()

    def rotate(self) -> None:
        self._tetris_game.rotate()

    def get_score(self) -> int:
        return self._score_keeper.score

    def get_grid(self) -> TetrisGrid:
        return self._tetris_game.grid

    def get_game_on(self) -> bool:
        return self._tetris_game.game_on

    def get_current_piece(self) -> Piece:
        return self._tetris_game.current_piece

    def get_next_piece(self) -> Piece:
        return self._tetris_game.next_piece

    def get_lines_cleared_last_tick(self) -> int:
        return self._score_keeper.get_lines_cleared_last_tick()

from dataclasses import dataclass
from colors import Color
from tetris_pieces import Piece, PieceDefinition, PieceFactory
from tetris_game_engine import TetrisExtension, TetrisGameEngine
from tetris_grid import TetrisGrid


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
        self._score += self.score_added_per_cleared_line * self._clear_lines_combo_function(cleared)
        self._lines_cleared_last_tick = cleared

    def _clear_lines_combo_function(self, cleared_lines: int) -> int:
        return int(1.5 ** (cleared_lines - 1))

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

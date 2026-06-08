from tetris_pieces import Piece
from tetris_grid import TetrisGrid
from tetris_pieces import PieceFactory


def is_valid_position(grid: TetrisGrid, piece: Piece) -> bool:
    for row_idx, row in enumerate(piece.current_shape):
        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            x = piece.pos[0] + col_idx
            y = piece.pos[1] + row_idx

            if y < 0:
                if x < 0 or x >= grid.size_x:
                    return False
                continue

            if not grid.valid_cell((x, y)):
                return False

            if grid.get_cell((x, y)) is not None:
                return False

    return True


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
        piece_valid: bool = is_valid_position(self.grid, piece)

        for extension in self.level_extensions:
            if not extension.is_valid(self.grid, self.game_on, self.current_piece, self.next_piece):
                return False

        return piece_valid

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



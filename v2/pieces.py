import dataclasses
from random import choice
from colors import Color


@dataclasses.dataclass(frozen=True)
class PieceDefinition:
    name: str
    rotation_states: tuple[list[list[int]], ...]


@dataclasses.dataclass(frozen=True)
class Piece:
    definition: PieceDefinition
    pos: tuple[int, int]
    color: Color
    rotation_state: int

    @property
    def current_shape(self) -> list[list[int]]:
        return self.definition.rotation_states[self.rotation_state]

    def move_left(self) -> 'Piece':
        return Piece(self.definition, (self.pos[0] - 1, self.pos[1]), self.color, self.rotation_state)

    def move_right(self) -> 'Piece':
        return Piece(self.definition, (self.pos[0] + 1, self.pos[1]), self.color, self.rotation_state)

    def move_down(self) -> 'Piece':
        return Piece(self.definition, (self.pos[0], self.pos[1] + 1), self.color, self.rotation_state)

    def next_rotation(self) -> 'Piece':
        new_rotation_state: int = (self.rotation_state + 1) % len(self.definition.rotation_states)
        return Piece(self.definition, (self.pos[0], self.pos[1]), self.color, new_rotation_state)


pieces: list[PieceDefinition] = [
    PieceDefinition('i-block', (
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]],
    )),

    PieceDefinition('o-block', (
        [[1, 1],
         [1, 1]],
    )),

    PieceDefinition('t-block', (
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],

        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],

        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],

        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]],
    )),

    PieceDefinition('s-block', (
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],

        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]],
    )),

    PieceDefinition('z-block', (
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],

        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]],
    )),

    PieceDefinition('l-block', (
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],

        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],

        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],

        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]],
    )),

    PieceDefinition('j-block', (
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],

        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],

        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],

        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]],
    )),
]


class PieceFactory:
    def __init__(self,
                 allowed_pieces: list[PieceDefinition],
                 allowed_colors: list[Color],
                 grid_column_size: int) -> None:
        self.allowed_pieces = allowed_pieces
        self.allowed_colors = allowed_colors
        self.cols = grid_column_size

    def _spawn_position(self, piece: PieceDefinition) -> tuple[int, int]:
        piece_width = len(piece.rotation_states[0][0])
        return self.cols // 2 - piece_width // 2, 0

    def spawn(self) -> Piece:
        random_piece: PieceDefinition = choice(self.allowed_pieces)
        return Piece(random_piece,
                     self._spawn_position(random_piece),
                     choice(self.allowed_colors),
                     rotation_state=0)

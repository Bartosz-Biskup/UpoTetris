from colors import all_colors, Color
from pieces import Piece, pieces,PieceDefinition
from dataclasses import dataclass
from tetris_game import TetrisExtension, TetrisGameSettings


DEFAULT_GRID_SIZE: tuple[int, int] = (14, 20)


levels: dict[str, TetrisGameSettings] = {
    'EASY': TetrisGameSettings(grid_size=DEFAULT_GRID_SIZE,
                               available_pieces=pieces[:2],
                               available_colors=all_colors,
                               game_speed=60,
                               extensions=[]),
    'MEDIUM': TetrisGameSettings(grid_size=DEFAULT_GRID_SIZE,
                               available_pieces=pieces[:4],
                               available_colors=all_colors,
                               game_speed=30,
                               extensions=[]),
    'HARD': TetrisGameSettings(grid_size=DEFAULT_GRID_SIZE,
                               available_pieces=pieces,
                               available_colors=all_colors,
                               game_speed=15,
                               extensions=[]),
}
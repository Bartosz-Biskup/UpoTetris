from colors import all_colors
from tetris_pieces import pieces
from tetris_game_engine import TetrisExtension
from v2.tetris_game import TetrisGameSettings

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
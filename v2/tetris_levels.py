from colors import all_colors, Color
from pieces import pieces
from tetris_game import TetrisGameSettings


DEFAULT_GRID_SIZE: tuple[int, int] = (14, 20)


levels: dict[str, TetrisGameSettings] = {
    'EASY': TetrisGameSettings(DEFAULT_GRID_SIZE,
                               all_colors,
                               pieces[:2],
                               30),
    'MEDIUM': TetrisGameSettings(DEFAULT_GRID_SIZE,
                                 all_colors,
                                 pieces[:4],
                                 30),
    'HARD': TetrisGameSettings(DEFAULT_GRID_SIZE,
                               all_colors,
                               pieces,
                               15)
}
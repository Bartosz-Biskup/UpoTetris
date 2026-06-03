from colors import all_colors, Color
from pieces import pieces
from tetris_game import TetrisGameSettings, TetrisGame
from v2.tetris_drawer import TetrisDrawer, DEFAULT_SETTINGS, TetrisDrawerSettings

levels: dict[str, TetrisGameSettings] = {
    'EASY': TetrisGameSettings((10, 17),
                               all_colors,
                               pieces[:2],
                               30),
    'MEDIUM': TetrisGameSettings((10, 17),
                                 all_colors,
                                 pieces[:4],
                                 30),
    'HARD': TetrisGameSettings((10, 17),
                               all_colors,
                               pieces,
                               15)
}
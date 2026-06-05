import pygame
from tetris_game import TetrisGame
from v2.tetris_drawer import TetrisDrawer, DEFAULT_SETTINGS
from tetris_levels import levels, TetrisGameSettings
from ui_elements import UiElement


class TetrisController(UiElement):
    def __init__(self, level: str) -> None:
        tetris_level_settings: TetrisGameSettings | None = levels.get(level)
        if tetris_level_settings is None:
            raise ValueError('Invalid tetris level')

        self.tetris_game = TetrisGame(tetris_level_settings)
        self._tetris_drawer = TetrisDrawer(self.tetris_game, DEFAULT_SETTINGS)

    def handle_events(self, events: list[pygame.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.tetris_game.move_left()
                elif event.key == pygame.K_d:
                    self.tetris_game.move_right()
                elif event.key == pygame.K_w:
                    self.tetris_game.rotate()
                elif event.key == pygame.K_SPACE:
                    self.tetris_game.hard_drop()

    def tick(self) -> None:
        self.tetris_game.tick()

    def draw(self, surface: pygame.Surface, pos: tuple[int, int]) -> None:
        self._tetris_drawer.draw(surface, pos)

    def get_size(self) -> tuple[int, int]:
        return self._tetris_drawer.get_size()

    @property
    def is_lost(self) -> bool:
        return not self.tetris_game.get_game_on()

    @property
    def score(self) -> int:
        return self.tetris_game.get_score()

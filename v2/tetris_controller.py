import pygame
from tetris_game import TetrisGame
from v2.tetris_drawer import TetrisDrawer, DEFAULT_SETTINGS
from tetris_levels import levels
from ui_elements import UiElement
from random import randint


class ScoreKeeper:
    def __init__(self, game: TetrisGame) -> None:
        self.score: float = 0

        self._game = game
        self._lines_cleared: int = 0

    def tick(self) -> None:
        total_lines_cleared: int = self._game.snapshot.lines_cleared
        self._lines_cleared, lines = total_lines_cleared, total_lines_cleared - self._lines_cleared

        self.score += round(100 * lines * (1 + (lines - 1) * 0.5))
        self.score += randint(0, 100) / 100

    def get_score(self) -> int:
        return int(self.score)

    def reset(self) -> None:
        self.score = 0


class TetrisController(UiElement):
    def __init__(self, level: str) -> None:
        self.tetris_game = TetrisGame(levels.get(level))
        self.tetris_drawer = TetrisDrawer(self.tetris_game, DEFAULT_SETTINGS)
        self._tick: int = 0

        self.score_keeper: ScoreKeeper = ScoreKeeper(self.tetris_game)

    def start(self) -> None:
        self.tetris_game.start()

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
        self._tick += 1
        if self._tick % self.tetris_game.settings.tick_every != 0:
            return
        self.tetris_game.tick()
        self.score_keeper.tick()

    def draw(self, surface: pygame.Surface, pos: tuple[int, int]) -> None:
        self.tetris_drawer.draw(surface, pos)

    def get_size(self) -> tuple[int, int]:
        x, y = self.tetris_game.settings.grid_size
        cell_size = self.tetris_drawer.settings.cell_size_px
        offset: int = self.tetris_drawer.settings.cell_offset
        return x * (cell_size + offset), (y - self.tetris_drawer.settings.hide_first) * (cell_size + offset)

    @property
    def is_lost(self) -> bool:
        return self.tetris_game.game_status == 'Lost'
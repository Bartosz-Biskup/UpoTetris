import pygame
from tetris_game import TetrisGame, GameState
from v2.tetris_drawer import TetrisDrawer, DEFAULT_SETTINGS
from tetris_levels import levels, TetrisGameSettings
from ui_elements import UiElement
from random import randint


class ScoreKeeper:
    def __init__(self, game: TetrisGame) -> None:
        self._prev_score, self.score = 0, 0
        self._game = game
        self._lines_cleared: int = 0

    def tick(self) -> None:
        total_lines_cleared: int = self._game.snapshot.lines_cleared
        self._lines_cleared, lines = total_lines_cleared, total_lines_cleared - self._lines_cleared

        self.score += round(100 * lines * (1 + (lines - 1) * 0.5))
        self.score += randint(0, 100) / 100

    def get_score(self) -> int:
        return int(self.score)

    def get_score_change(self) -> int:
        """
        returns score change since last call
        """
        difference: int = self.score - self._prev_score
        self._prev_score = self.score
        return difference

    def reset(self) -> None:
        self.score = 0


class TetrisController(UiElement):
    def __init__(self, level: str) -> None:
        tetris_level_settings: TetrisGameSettings | None = levels.get(level)
        if tetris_level_settings is None:
            raise ValueError('Invalid tetris level')

        self.tetris_game = TetrisGame(tetris_level_settings)
        self._tetris_drawer = TetrisDrawer(self.tetris_game, DEFAULT_SETTINGS)
        self._score_keeper: ScoreKeeper = ScoreKeeper(self.tetris_game)

        self._tick_count: int = 0

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
        self._tick_count += 1
        if self._tick_count % self.tetris_game._settings.tick_every != 0:
            return

        self.tetris_game.tick()
        self._score_keeper.tick()

    def draw(self, surface: pygame.Surface, pos: tuple[int, int]) -> None:
        self._tetris_drawer.draw(surface, pos)

    def get_size(self) -> tuple[int, int]:
        return self._tetris_drawer.get_size()

    @property
    def is_lost(self) -> bool:
        return self.tetris_game.snapshot.game_status == 'Lost'

    @property
    def score(self) -> int:
        return self._score_keeper.get_score()

    @property
    def tetris_snapshot(self) -> GameState:
        return self.tetris_game.snapshot

    @property
    def score_change(self) -> int:
        return self._score_keeper.get_score_change()
import pygame
import tetris_game
from colors import all_colors
from tetris_game import TetrisGame, TetrisGameSettings
from v2.tetris_drawer import TetrisDrawer, DEFAULT_SETTINGS, TetrisDrawerSettings
from pieces import pieces


tetris_settings = TetrisGameSettings((10, 17),
                                     all_colors,
                                     pieces[:2])

drawer_settings: TetrisDrawerSettings = TetrisDrawerSettings(cell_size_px=28,
                                                              cell_offset=2,
                                                              hide_first=2,
                                                              grid_bg_color=(0, 0, 0),
                                                              empty_cell_color=(81, 68, 94))


def tetris_game_pygame(screen: pygame.Surface,
                       game: TetrisGame,
                       game_clock: pygame.Clock,
                       tick_every: int) -> None:
    game_drawer: TetrisDrawer = TetrisDrawer(game, drawer_settings)

    game.start()
    running: bool = True
    current_tick: int = 0
    while game._game_status != 'Lost' and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    key = 'a'
                    game.move_left()
                elif event.key == pygame.K_d:
                    key = 'd'
                    game.move_right()
                elif event.key == pygame.K_w:
                    key = 'w'
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    key = 'space'
                    game.hard_drop()

        current_tick = (current_tick + 1) % 60

        screen.fill((0, 0, 0))
        game_drawer.draw(screen, (10, 10))
        if current_tick % tick_every == 0:
            game.tick()

        pygame.display.update()
        clock.tick(180)




if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((720, 480))
    clock = pygame.time.Clock()

    tetris_game_pygame(screen, TetrisGame(tetris_settings), clock, 60)
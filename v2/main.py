from abc import abstractmethod, ABC
import pygame
from tetris_controller import TetrisController
from ui_elements import Label, TimeLabel, Layout, Image, Page, PageContainer, Button
from piece_preview import PiecePreview
from cursorMenu import Menu
from assets import DEFAULT_ASSETS_PATH
import sys
from audio_players import SoundEffectPlayer, SoundtrackPlayer, Soundtrack
from ui_elements import BlinkingLabel
from user_data_manager import ScoreManager, JsonManager, SoundtrackManager


SCREEN_DIMENSIONS: tuple[int, int] = (720, 480)
screen_w, screen_h = SCREEN_DIMENSIONS

USER_FILE: str = 'user_data.json'
JSON_FILE_MANAGER: JsonManager = JsonManager(USER_FILE)
SCORE_MANAGER: ScoreManager = ScoreManager(JSON_FILE_MANAGER)
SOUNDTRACK_MANAGER: SoundtrackManager = SoundtrackManager(JSON_FILE_MANAGER, SCORE_MANAGER)


class UiScreen(ABC):
    @abstractmethod
    def on_enter(self) -> None:
        ...

    @abstractmethod
    def on_exit(self) -> None:
        ...

    @abstractmethod
    def tick(self, events: list[pygame.Event]) -> None:
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        ...

    @abstractmethod
    def next_screen(self) -> 'UiScreen | None':
        ...


class GameOverScreen(UiScreen):
    def __init__(self,
                 score: int,
                 time: float,
                 level: str) -> None:
        self._score = score
        self._time = time
        self._level = level

        self._layout: Layout = Layout()
        self._menu: Menu | None = None
        self._next: UiScreen | None = None

    def on_enter(self) -> None:
        minutes = int(self._time // 60)
        seconds = int(self._time % 60)

        score_label = Label(text=f"SCORE: {self._score}", font_size=32)
        time_label  = Label(text=f"TIME: {minutes:02}:{seconds:02}", font_size=32)

        self._menu = Menu(items=[
            Image(DEFAULT_ASSETS_PATH / "play_again_button.png"),
            Image(DEFAULT_ASSETS_PATH / "main_menu_button.png"),
        ], cursor_offset_y=-30)

        self._layout = Layout()
        self._layout.add_element(score_label,   (screen_w // 3, 120), "center")
        self._layout.add_element(time_label,    (screen_w // 3 * 2, 120),  "center")
        self._layout.add_element(self._menu,    (screen_w // 2, screen_h // 2 + 20),  "center")

    def on_exit(self) -> None: ...

    def tick(self, events: list[pygame.Event]) -> None:
        if self._menu is None:
            return

        self._menu.tick(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                match self._menu.selected_index:
                    case 0:
                        self._next = TetrisGameScreen(level=self._level)
                    case 1:
                        self._next = MainMenuScreen()

    def draw(self, surface: pygame.Surface) -> None:
        if self._menu is None:
            return
        self._layout.render(surface)

    def next_screen(self) -> 'UiScreen | None':
        return self._next


class MainMenuScreen(UiScreen):
    def __init__(self) -> None:
        self._layout: Layout = Layout()
        self._menu: Menu | None = None
        self._logo_img: Image = Image(DEFAULT_ASSETS_PATH / "logo.png", scale=1)

        self._next: UiScreen | None = None

    def on_enter(self) -> None:
        items = [
            Image(DEFAULT_ASSETS_PATH / "play_button.png"),
            Image(DEFAULT_ASSETS_PATH / "market_button.png"),
            Image(DEFAULT_ASSETS_PATH / "red_quit_button.png"),
        ]

        self._menu = Menu(items=items, cursor_offset_y=-8)
        self._layout = Layout()
        self._layout.add_element(self._menu, (screen_w // 2 + 30, 320), "center")
        self._layout.add_element(self._logo_img, (screen_w // 2 + 10, 110), "center")

    def on_exit(self) -> None:
        ...

    def tick(self, events: list[pygame.Event]) -> None:
        if self._menu is None:
            return

        self._menu.tick(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                match self._menu.selected_index:
                    case 0:
                        self._next = ChooseLevelScreen()
                    case 1:
                        self._next = MarketScreen()
                    case 2:
                        sys.exit()

    def draw(self, surface: pygame.Surface) -> None:
        if self._menu is None:
            return

        self._layout.render(surface)

    def next_screen(self) -> 'UiScreen | None':
        return self._next


class TetrisGameScreen(UiScreen):
    def __init__(self, level: str) -> None:
        self.level = level
        self.controller = TetrisController(level)

        self._layout: Layout = Layout()
        self._score_label: BlinkingLabel | None = None
        self._time_label: TimeLabel | None = None
        self._piece_preview: PiecePreview | None = None

        self._sx_player: SoundEffectPlayer = SoundEffectPlayer()
        self._soundtrack_player: SoundtrackPlayer = SoundtrackPlayer(SOUNDTRACK_MANAGER)

    @staticmethod
    def _format_score(score: int) -> str:
        return str(score).zfill(2)

    def on_enter(self) -> None:
        self._soundtrack_player.play_default()

        self._score_label: BlinkingLabel = BlinkingLabel(text='00', font_size=20)
        self._piece_preview: PiecePreview = PiecePreview((200, 150), self.controller.tetris_game)
        self._time_label: TimeLabel = TimeLabel(font_size=20)

        self._layout.add_element(self.controller, (10, screen_h // 2), 'middle_left')
        self._layout.add_element(self._score_label, (415, 180), 'bottom_left')
        self._layout.add_element(self._piece_preview, (515, 265), "center")
        self._layout.add_element(self._time_label, (560, 180), 'bottom_left')

    def on_exit(self) -> None:
        self._sx_player.play_ack()
        SCORE_MANAGER.add_score(self.controller.score)
        self._soundtrack_player.stop()

    def tick(self, events: list[pygame.Event]) -> None:
        if self.controller.is_lost:
            return

        self.controller.handle_events(events)
        self.controller.tick()

        # if False:
        #     self._score_label.blink()
        #     self._sx_player.play_faah()

        self._score_label.set_text(self._format_score(self.controller.score))

    def draw(self, surface: pygame.Surface) -> None:
        self._layout.render(surface)

    def next_screen(self) -> 'UiScreen | None':
        if self.controller.is_lost:
            return GameOverScreen(self.controller.score,
                                  self._time_label.time_elapsed,
                                  self.level)


class ChooseLevelScreen(UiScreen):
    def __init__(self) -> None:
        self._layout: Layout = Layout()
        self._menu: Menu | None = None
        self._next: UiScreen | None = None

    def on_enter(self) -> None:
        title = Label(text="CHOOSE LEVEL:", font_size=32)

        self._menu = Menu(items=[
            Image(DEFAULT_ASSETS_PATH / "play_easy.png"),
            Image(DEFAULT_ASSETS_PATH / "play_normal.png"),
            Image(DEFAULT_ASSETS_PATH / "play_hard.png"),
        ], cursor_offset_y=-8)

        self._layout = Layout()
        self._layout.add_element(title,       (screen_w // 2, 120), "center")
        self._layout.add_element(self._menu,  (screen_w // 2, 320),       "center")

    def on_exit(self) -> None: ...

    def tick(self, events: list[pygame.Event]) -> None:
        if self._menu is None:
            return

        self._menu.tick(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                match self._menu.selected_index:
                    case 0:
                        self._next = TetrisGameScreen(level="EASY")
                    case 1:
                        self._next = TetrisGameScreen(level="MEDIUM")
                    case 2:
                        self._next = TetrisGameScreen(level="HARD")

    def draw(self, surface: pygame.Surface) -> None:
        if self._menu is None:
            return
        self._layout.render(surface)

    def next_screen(self) -> 'UiScreen | None':
        return self._next


class MarketScreen(UiScreen):
    ITEMS_PER_PAGE = 4

    START_X = 0
    START_Y = 20
    ITEM_H = 100

    def __init__(self):
        self._songs: list[Soundtrack] = []
        self._equipped_name: str | None = None

        self._container = PageContainer(size=(screen_w, screen_h))
        self._coins_label = Label("", (255, 255, 0))

        self._exit_btn = Button("EXIT", self._exit, (255, 80, 80))

        self._next = None

    def on_enter(self):
        self._reload_data()
        self._build_ui()

    def on_exit(self):
        pass

    def _reload_data(self):
        self._songs = SOUNDTRACK_MANAGER.get_all_soundtracks()
        self._equipped_name = SOUNDTRACK_MANAGER.get_default_soundtrack().name
        self._coins_label.set_text(f"Coins: {SCORE_MANAGER.get_score()}")

    def _build_ui(self):
        self._container.pages.clear()

        page = self._container.create_page()
        index = 0

        for song in self._songs:
            if index >= self.ITEMS_PER_PAGE:
                page = self._container.create_page()
                index = 0

            self._add_song(page, song, index)
            index += 1

    def _add_song(self, page, song, index):
        base_y = self.START_Y + index * self.ITEM_H
        page.add_widget(Label(song.name), (150, base_y + 20), "center")
        page.add_widget(Label(song.author, (150, 150, 150)), (150, base_y + 45), "center")
        page.add_widget(Label(str(song.price), (255, 255, 0)), (150, base_y + 70), "center")
        page.add_widget(self._make_buy_button(song), (355, base_y + 25), "center")
        page.add_widget(self._make_equip_button(song), (355, base_y + 65), "center")

    def _make_buy_button(self, song: Soundtrack) -> Button:
        if song.owned:
            return Button("BOUGHT", lambda: None, (255, 80, 80))

        def buy():
            if SCORE_MANAGER.get_score() < song.price:
                return

            SOUNDTRACK_MANAGER.buy_soundtrack(song.name)

            self._reload_data()
            self._build_ui()

        return Button("BUY", buy, (0, 255, 0))

    def _make_equip_button(self, song: Soundtrack) -> Button:
        if song.name == self._equipped_name:
            return Button("EQUIPPED", lambda: None, (0, 255, 0))

        def equip():
            if not song.owned:
                return

            SOUNDTRACK_MANAGER.set_default_soundtrack(song.name)

            self._reload_data()
            self._build_ui()

        return Button("EQUIP", equip, (200, 200, 200))

    def _exit(self):
        self._next = MainMenuScreen()

    def tick(self, events):
        ...

    def draw(self, surface):
        surface.fill((20, 20, 20))

        self._container.draw(surface, (150, 0))

        self._exit_btn.draw(surface, (20, 20))
        self._coins_label.draw(surface, (screen_w - 150, 10))

    def next_screen(self):
        return self._next

def mainloop(screen: pygame.Surface) -> None:
    clock = pygame.time.Clock()

    current_screen: UiScreen = MainMenuScreen()
    current_screen.on_enter()

    running: bool = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        next_screen = current_screen.next_screen()
        if next_screen is not None:
            current_screen.on_exit()
            current_screen = next_screen
            current_screen.on_enter()

        current_screen.tick(events)

        screen.fill((0, 0, 0))
        current_screen.draw(screen)
        pygame.display.update()

        clock.tick(120)

    current_screen.on_exit()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    mainloop(screen)
from pathlib import Path
from typing import Optional
from pygame import mixer, error
from user_data_manager import SoundtrackManager, Soundtrack


DEFAULT_MIXER_VOLUME: float = 0.4
DEFAULT_SOUND_EFFECTS_PATH: Path = Path(__file__).parent.parent / "sound_effects"
DEFAULT_SOUNDTRACK_PATH: Path = Path(__file__).parent.parent / "soundtracks"

ACK_SX_PATH: Path = DEFAULT_SOUND_EFFECTS_PATH / "ack.mp3"
FAAH_SX_PATH: Path = DEFAULT_SOUND_EFFECTS_PATH / "Faah sound effect.mp3"


class BaseAudioPlayer:
    def __init__(self,
                 volume: float = DEFAULT_MIXER_VOLUME) -> None:
        if not mixer.get_init():
            mixer.init()

        self._volume = volume

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        if not 0 <= value <= 1:
            raise ValueError('Invalid volume.')

        self._volume = value

    @staticmethod
    def _load(path: Path) -> Optional[mixer.Sound]:
        if not path.exists():
            return None

        try:
            return mixer.Sound(path)
        except error:
            return None

    def _play(self, sound: mixer.Sound, loops: int = 0) -> None:
        sound.set_volume(self.volume)
        sound.play(loops=loops)


class SoundEffectPlayer(BaseAudioPlayer):
    def __init__(self) -> None:
        super().__init__()

        self._ack: Optional[mixer.Sound] = self._load(ACK_SX_PATH)
        self._faah: Optional[mixer.Sound] = self._load(FAAH_SX_PATH)

    def play_faah(self) -> None:
        if self._faah is not None:
            self._play(self._faah)

    def play_ack(self) -> None:
        if self._ack is not None:
            self._play(self._ack)


class SoundtrackPlayer(BaseAudioPlayer):
    def __init__(self,
                 soundtrack_manager: SoundtrackManager) -> None:
        super().__init__()
        self._soundtrack_mg = soundtrack_manager
        self._current: Optional[mixer.Sound] = None

    def _get_soundtrack_path(self, name: str) -> Path:
        all_soundtracks: list[Soundtrack] = self._soundtrack_mg.get_all_soundtracks()
        match: Optional[Soundtrack] = next((s for s in all_soundtracks if s.name == name), None)

        if match is None:
            raise ValueError('Soundtrack not found.')

        return Path(match.path)

    def play_default(self) -> None:
        default_soundtrack: str = self._soundtrack_mg.get_default_soundtrack().name
        self.play(default_soundtrack)

    def play(self, soundtrack_name: str) -> None:
        soundtrack_path: Path = DEFAULT_SOUNDTRACK_PATH / self._get_soundtrack_path(soundtrack_name)
        sound: Optional[mixer.Sound] = self._load(soundtrack_path)

        if sound is None:
            raise ValueError('Path not found')

        self.stop()
        self._play(sound, loops=-1)
        self._current = sound

    def stop(self) -> None:
        if self._current is not None:
            self._current.stop()
            self._current = None





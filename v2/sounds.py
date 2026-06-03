from pygame import mixer
from pathlib import Path
from typing import Optional


DEFAULT_SOUND_EFFECTS_PATH: Path = Path(__file__).parent.parent / "sound_effects"
DEFAULT_SOUNDTRACK_PATH: Path = Path(__file__).parent.parent / "soundtracks"

ACK_SX_PATH: Path = DEFAULT_SOUND_EFFECTS_PATH / "ack.mp3"
FAAH_SX_PATH: Path = DEFAULT_SOUND_EFFECTS_PATH / "Faah sound effect.mp3"

DEFAULT_MIXER_VOLUME: float = 0.3


class SoundEffectPlayer:
    def __init__(self, volume: float = DEFAULT_MIXER_VOLUME) -> None:
        if not mixer.get_init():
            mixer.init()

        self._ack: Optional[mixer.Sound] = self._load(ACK_SX_PATH)
        self._faah: Optional[mixer.Sound] = self._load(FAAH_SX_PATH)

        self.volume = volume

    def play_ack(self) -> None:
        self._play(self._ack)

    def play_faah(self) -> None:
        self._play(self._faah)

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Volume must be between 0.0 and 1.0, got {value}")
        self._volume = value
        for sound in (self._ack, self._faah):
            if sound is not None:
                sound.set_volume(value)

    @staticmethod
    def _load(path: Path) -> Optional[mixer.Sound]:
        if not path.exists():
            print(f"[SoundEffectPlayer] Warning: sound file not found: {path}")
            return None
        return mixer.Sound(path)

    @staticmethod
    def _play(sound: Optional[mixer.Sound]) -> None:
        if sound is not None:
            sound.play()



import json
import os
from dataclasses import dataclass, asdict


class JsonManager:
    def __init__(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Game data file not found: '{filepath}'")
        self._filepath = filepath

    def load(self) -> dict:
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get(self, key: str):
        return self.load()[key]

    def set(self, key: str, value) -> None:
        data = self.load()
        data[key] = value
        self.save(data)


@dataclass
class Soundtrack:
    name: str
    author: str
    path: str
    price: int
    owned: bool
    rarity: str

    @classmethod
    def from_dict(cls, data: dict) -> "Soundtrack":
        return cls(
            name=data["name"],
            author=data["author"],
            path=data["path"],
            price=data["price"],
            owned=data["owned"],
            rarity=data["rarity"],
        )


class ScoreManager:
    _SCORE_KEY = "score"
    _MAX_SCORE_KEY = "max-score"

    def __init__(self, json_manager: JsonManager):
        self._db = json_manager

    def get_score(self) -> int:
        return self._db.get(self._SCORE_KEY)

    def get_max_score(self) -> int:
        return self._db.get(self._MAX_SCORE_KEY)

    def add_score(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError(f"add_score expects a positive amount, got {amount}.")

        data = self._db.load()
        data[self._SCORE_KEY] += amount
        self._set_max_score(data)
        self._db.save(data)
        return data[self._SCORE_KEY]

    def remove_score(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError(f"remove_score expects a positive amount, got {amount}.")

        data = self._db.load()
        data[self._SCORE_KEY] = max(0, data[self._SCORE_KEY] - amount)
        self._db.save(data)
        return data[self._SCORE_KEY]

    def _set_max_score(self, data: dict) -> None:
        if data[self._SCORE_KEY] > data[self._MAX_SCORE_KEY]:
            data[self._MAX_SCORE_KEY] = data[self._SCORE_KEY]


class SoundtrackManager:
    _SONGS_KEY = "songs"
    _DEFAULT_KEY = "default-soundtrack"

    def __init__(self, json_manager: JsonManager, score_manager: ScoreManager):
        self._db = json_manager
        self._score = score_manager

    def get_all_soundtracks(self) -> list[Soundtrack]:
        return [Soundtrack.from_dict(s) for s in self._db.get(self._SONGS_KEY)]

    def get_default_soundtrack(self) -> Soundtrack:
        return self._find_by_name(self._db.get(self._DEFAULT_KEY))

    def set_default_soundtrack(self, name: str) -> None:
        song = self._find_by_name(name)
        if not song.owned:
            raise ValueError(f"Cannot set '{name}' as default — player does not own it.")
        self._db.set(self._DEFAULT_KEY, name)

    def buy_soundtrack(self, name: str) -> Soundtrack:
        song = self._find_by_name(name)

        if song.owned:
            raise ValueError(f"'{name}' is already owned.")

        balance = self._score.get_score()
        if balance < song.price:
            raise ValueError(f"Not enough score to buy '{name}'. Need {song.price}, have {balance}.")

        data = self._db.load()
        for entry in data[self._SONGS_KEY]:
            if entry["name"] == name:
                entry["owned"] = True
                break

        self._db.save(data)
        self._score.remove_score(song.price)
        return Soundtrack.from_dict({**asdict(song), "owned": True})

    def _find_by_name(self, name: str) -> Soundtrack:
        for entry in self._db.get(self._SONGS_KEY):
            if entry["name"] == name:
                return Soundtrack.from_dict(entry)
        raise ValueError(f"No song found with name '{name}'.")
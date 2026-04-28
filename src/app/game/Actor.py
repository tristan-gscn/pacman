from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.game.GameEngine import GameEngine


class Actor:
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0
    ) -> None:
        self.x = x
        self.y = y
        self._game_engine: GameEngine | None = None

    def set_game_engine(self, game_engine: GameEngine | None) -> None:
        self._game_engine = game_engine

    def move(self, dx: float, dy: float) -> None:
        if self._game_engine is None:
            self.x += dx
            self.y += dy
            return
        self._game_engine.move_actor(self, dx, dy)

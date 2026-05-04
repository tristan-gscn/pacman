from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.game.GameEngine import GameEngine


class Actor:
    """Base class for all moving entities in the game (Player and NPCs)."""

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0
    ) -> None:
        """Initialize an actor with coordinates.

        Args:
            x (float): Initial x-coordinate. Defaults to 0.0.
            y (float): Initial y-coordinate. Defaults to 0.0.
        """
        self.x = x
        self.y = y
        self._game_engine: GameEngine | None = None

    def set_game_engine(self, game_engine: GameEngine | None) -> None:
        """Associate the actor with a game engine instance.

        Args:
            game_engine (GameEngine | None): The game engine to attach.
        """
        self._game_engine = game_engine

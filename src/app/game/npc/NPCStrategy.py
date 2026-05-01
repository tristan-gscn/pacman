from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.game.Player import Player


class NPCStrategy(ABC):
    """Abstract base class for NPC movement strategies."""
    path: list[tuple[int, int]] = []

    @abstractmethod
    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        """Determine the target coordinate for the NPC.

        Args:
            grid (list[list[int]]): The current maze grid.
            player (Player): The player instance for reference.

        Returns:
            tuple[int, int]: The target (row, col) coordinate.
        """
        pass

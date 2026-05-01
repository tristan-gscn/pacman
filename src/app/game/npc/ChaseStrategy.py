from __future__ import annotations
from typing import TYPE_CHECKING
from .NPCStrategy import NPCStrategy

if TYPE_CHECKING:
    from src.app.game.Player import Player


class ChaseStrategy(NPCStrategy):
    """Strategy for NPCs to directly chase the player."""

    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        """Target the player's current position.

        Args:
            grid (list[list[int]]): The maze grid.
            player (Player): The player instance.

        Returns:
            tuple[int, int]: The player's (row, col) coordinate.
        """
        return (int(round(player.y)), int(round(player.x)))

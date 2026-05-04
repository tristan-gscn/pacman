from __future__ import annotations
from typing import TYPE_CHECKING
from .NPCStrategy import NPCStrategy
from src.app.game.npc.FleeStrategy import FleeStrategy

if TYPE_CHECKING:
    from src.app.game.Player import Player
    from src.app.game.npc.NPC import NPC


class ScatterStrategy(NPCStrategy):
    """Strategy where NPCs chase the player but scatter when too close."""

    def __init__(self, flee_radius: int = 4) -> None:
        """Initialize the scatter strategy.

        Args:
            flee_radius (int): The distance at which the NPC starts scattering.
                Defaults to 4.
        """
        self.flee = False
        self.flee_target: tuple[int, int] | None = None
        self.flee_radius = flee_radius
        self.npc_pos: tuple[int, int] = (0, 0)
        self.npc: NPC | None = None

    def set_npc(self, npc: NPC) -> None:
        """Set the NPC instance using this strategy.

        Args:
            npc (NPC): The NPC instance.
        """
        self.npc = npc

    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        """Determine target based on distance to player.

        Chases the player unless they are within flee_radius, in which case
        it chooses a flee target.

        Args:
            grid (list[list[int]]): The maze grid.
            player (Player): The player instance.

        Returns:
            tuple[int, int]: The target (row, col) coordinate.
        """
        if self.npc is not None:
            self.npc_pos = (int(round(self.npc.y)), int(round(self.npc.x)))

        player_pos = (int(round(player.y)), int(round(player.x)))
        distance = abs(self.npc_pos[0] - player_pos[0]) + abs(
            self.npc_pos[1] - player_pos[1])

        if self.flee:
            if self.flee_target is None:
                self.flee_target = FleeStrategy.get_flee_target(
                    grid, player_pos, self.npc_pos)
            if self.npc_pos == self.flee_target:
                self.flee = False
                self.flee_target = None
            else:
                return self.flee_target

        if distance <= self.flee_radius:
            self.flee = True
            self.flee_target = FleeStrategy.get_flee_target(
                grid, player_pos, self.npc_pos)
            return self.flee_target

        return player_pos

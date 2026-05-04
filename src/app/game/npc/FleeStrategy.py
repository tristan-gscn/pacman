from __future__ import annotations
from typing import TYPE_CHECKING
from .NPCStrategy import NPCStrategy
from src.app.game.MazeUtils import MazeUtils
import random

if TYPE_CHECKING:
    from src.app.game.Player import Player
    from src.app.game.npc.NPC import NPC


class FleeStrategy(NPCStrategy):
    """Strategy for NPCs to flee from the player."""

    def __init__(self) -> None:
        """Initialize the flee strategy."""
        self.flee_target: tuple[int, int] | None = None
        self.npc_pos: tuple[int, int] = (0, 0)
        self.npc: NPC | None = None

    def set_npc(self, npc: NPC) -> None:
        """Set the NPC instance using this strategy.

        Args:
            npc (NPC): The NPC instance.
        """
        self.npc = npc

    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        """Determine a target cell far away from the player.

        Args:
            grid (list[list[int]]): The maze grid.
            player (Player): The player instance.

        Returns:
            tuple[int, int]: The target (row, col) coordinate to flee to.
        """
        if self.npc is not None:
            self.npc_pos = (int(round(self.npc.y)), int(round(self.npc.x)))

        if self.flee_target is None or self.npc_pos == self.flee_target:
            self.flee_target = self.get_flee_target(
                grid,
                (int(round(player.y)), int(round(player.x))),
                self.npc_pos
            )
        return self.flee_target

    @staticmethod
    def get_flee_target(
        grid: list[list[int]],
        player_pos: tuple[int, int],
        npc_pos: tuple[int, int]
    ) -> tuple[int, int]:
        """Calculate the best cell to flee to.

        Finds the reachable cell that is furthest from the player.

        Args:
            grid (list[list[int]]): The maze grid.
            player_pos (tuple[int, int]): Current player (row, col).
            npc_pos (tuple[int, int]): Current NPC (row, col).

        Returns:
            tuple[int, int]: The chosen flee target (row, col).
        """
        height = len(grid)
        width = len(grid[0]) if height else 0

        def in_bounds(coordinates: tuple[int, int]) -> bool:
            """Check if coordinates are within the maze grid.

            Args:
                coordinates (tuple[int, int]): (row, col) tuple to check.

            Returns:
                bool: True if coordinates are within bounds.
            """
            row, col = coordinates
            return 0 <= row < height and 0 <= col < width

        if not in_bounds(player_pos) or not in_bounds(npc_pos):
            return player_pos

        def get_neighbors(position: tuple[int, int]) -> list[tuple[int, int]]:
            """Get accessible neighboring cells respecting maze walls.

            Args:
                position (tuple[int, int]): Current (row, col) position.

            Returns:
                list[tuple[int, int]]: List of accessible neighbor coordinates.
            """
            row, col = position
            walls = MazeUtils.unpack_cell(grid[row][col])
            neighbors: list[tuple[int, int]] = []
            if not walls["N"] and row > 0:
                neighbors.append((row - 1, col))
            if not walls["S"] and row < height - 1:
                neighbors.append((row + 1, col))
            if not walls["W"] and col > 0:
                neighbors.append((row, col - 1))
            if not walls["E"] and col < width - 1:
                neighbors.append((row, col + 1))
            return neighbors

        player_dist: dict[tuple[int, int], int] = {player_pos: 0}
        queue: list[tuple[int, int]] = [player_pos]
        while queue:
            current = queue.pop(0)
            current_dist = player_dist[current]
            for neighbor in get_neighbors(current):
                if neighbor in player_dist:
                    continue
                player_dist[neighbor] = current_dist + 1
                queue.append(neighbor)

        max_distance = -1
        best_cells: list[tuple[int, int]] = []
        visited: set[tuple[int, int]] = {npc_pos}
        queue = [npc_pos]
        while queue:
            current = queue.pop(0)
            distance = player_dist.get(current)
            if distance is not None:
                if distance > max_distance:
                    max_distance = distance
                    best_cells = [current]
                elif distance == max_distance:
                    best_cells.append(current)

            for neighbor in get_neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                queue.append(neighbor)

        if not best_cells:
            return player_pos
        return random.choice(best_cells)

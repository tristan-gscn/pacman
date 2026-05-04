from __future__ import annotations
from typing import TYPE_CHECKING
from .NPCStrategy import NPCStrategy
from src.app.game.MazeUtils import MazeUtils

if TYPE_CHECKING:
    from src.app.game.Player import Player


class AmbushStrategy(NPCStrategy):
    """Strategy for NPCs to ambush the player by targeting a cell ahead."""

    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        """Target a cell in front of the player based on their direction.

        Args:
            grid (list[list[int]]): The maze grid.
            player (Player): The player instance.

        Returns:
            tuple[int, int]: The target (row, col) coordinate.
        """
        row = int(round(player.y))
        col = int(round(player.x))
        height = len(grid)
        width = len(grid[0]) if height else 0

        def in_bounds(r: int, c: int) -> bool:
            """Check if coordinates are within the maze grid.

            Args:
                r (int): Row index.
                c (int): Column index.

            Returns:
                bool: True if coordinates are within bounds.
            """
            return 0 <= r < height and 0 <= c < width

        if not in_bounds(row, col):
            return (row, col)

        walls = MazeUtils.unpack_cell(grid[row][col])

        if player.direction == "right" and not walls["E"]:
            target = (row, col + 1)
            if in_bounds(*target):
                return target
        elif player.direction == "left" and not walls["W"]:
            target = (row, col - 1)
            if in_bounds(*target):
                return target
        elif player.direction == "up" and not walls["N"]:
            target = (row - 1, col)
            if in_bounds(*target):
                return target
        elif player.direction == "down" and not walls["S"]:
            target = (row + 1, col)
            if in_bounds(*target):
                return target

        return (row, col)

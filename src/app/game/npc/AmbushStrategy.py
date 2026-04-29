from .NPCStrategy import NPCStrategy
from src.app.game.MazeUtils import MazeUtils
from src.app.game.Player import Player


class AmbushStrategy(NPCStrategy):
    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        row = int(round(player.y))
        col = int(round(player.x))
        height = len(grid)
        width = len(grid[0]) if height else 0

        def in_bounds(r: int, c: int) -> bool:
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

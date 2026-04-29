from .NPCStrategy import NPCStrategy
from src.app.game.Player import Player


class AmbushStrategy(NPCStrategy):
    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:

        if player.direction == "right":
            cell: int = grid[int(round(player.y)), int(round(player.x)) + 1]
            if not (cell & 15 and cell & 8):
                return (int(round(player.y)), int(round(player.x)) + 1)
        elif player.direction == "left":
            cell: int = grid[int(round(player.y)), int(round(player.x)) - 1]
            if not (cell & 15 and cell & 2):
                return (int(round(player.y)), int(round(player.x)) - 1)
        elif player.direction == "up":
            cell: int = grid[int(round(player.y)) - 1, int(round(player.x))]
            if not (cell & 15 and cell & 4):
                return (int(round(player.y)), int(round(player.x)) + 1)
        elif player.direction == "down":
            cell: int = grid[int(round(player.y)) + 1, int(round(player.x))]
            if not (cell & 15 and cell & 1):
                return (int(round(player.y)), int(round(player.x)) + 1)
        else:
            return (int(round(player.y)), int(round(player.x)))

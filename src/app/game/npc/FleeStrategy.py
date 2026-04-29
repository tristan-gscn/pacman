from .NPCStrategy import NPCStrategy
from src.app.game.Player import Player
from src.app.game.MazeUtils import MazeUtils
from src.app.game.npc.NPC import NPC
import random


class FleeStrategy(NPCStrategy):

    def __init__(self):
        self.flee_target: tuple[int, int] | None = None
        self.npc_pos: tuple[int, int] = (0, 0)

    def set_npc(self, npc: NPC):
        self.npc_pos: tuple[int, int] = (npc.x, npc.y)

    def act(self, grid: list[list[int]], player: Player) -> None:
        if not self.flee_target:
            self.flee_target = self.get_flee_target(grid, (int(round(player.x)), int(round(player.y))))
        if self.npc_pos == self.flee_target:
            self.flee_target = None
            return self.npc_pos
        return self.flee_target

    @staticmethod
    def get_flee_target(grid: list[list[int]], player_pos: tuple[int, int]):
        radius = max(10, len(grid) // 2 + len(grid[0]) // 2)

        def propagate(past: int, radius: int, coordinates: tuple[int, int],
                      direction: str | None):
            if past == radius:
                return coordinates
            if direction is not None:
                if not MazeUtils.unpack_cell(
                        grid[coordinates[1]][coordinates[0]])[direction]:
                    return None
            return [
                propagate(past + 1, radius,
                          (coordinates[0] + 1, coordinates[1]), "E"),
                propagate(past + 1, radius,
                          (coordinates[0] - 1, coordinates[1]), "W"),
                propagate(past + 1, radius,
                          (coordinates[0], coordinates[1] - 1), "N"),
                propagate(past + 1, radius,
                          (coordinates[0], coordinates[1] + 1), "S"),
            ]

        propagation_res = propagate(0, radius, player_pos, None)

        def flatten(nested_list):
            flat_list = []
            for item in nested_list:
                if isinstance(item, list):
                    flat_list.extend(flatten(item))
                elif item is not None:
                    flat_list.append(item)
            return flat_list

        return random.choice(flatten(propagation_res))

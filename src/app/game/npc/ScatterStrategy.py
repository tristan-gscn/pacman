from .NPCStrategy import NPCStrategy
from src.app.game.Player import Player


class ScatterStrategy(NPCStrategy):
    flee: bool = False
    flee_target: tuple[int, int]

    def act(self, grid: list[list[int]], player: Player) -> None:
        if len(self.path) < 4:
            pass

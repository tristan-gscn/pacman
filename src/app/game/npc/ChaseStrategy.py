from .NPCStrategy import NPCStrategy
from src.app.game import Player


class ChaseStrategy(NPCStrategy):
    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        return (int(round(player.y)), int(round(player.x)))

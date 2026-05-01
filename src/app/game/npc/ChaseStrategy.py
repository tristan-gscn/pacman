from __future__ import annotations
from typing import TYPE_CHECKING
from .NPCStrategy import NPCStrategy

if TYPE_CHECKING:
    from src.app.game.Player import Player


class ChaseStrategy(NPCStrategy):
    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        return (int(round(player.y)), int(round(player.x)))

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.game.Player import Player


class NPCStrategy(ABC):
    path: list[tuple[int, int]] = []

    @abstractmethod
    def act(self, grid: list[list[int]], player: Player) -> tuple[int, int]:
        pass

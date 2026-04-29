from ..Actor import Actor
from .NPCStrategy import NPCStrategy
from src.models import NPCSprites


class NPC(Actor):
    def __init__(
        self,
        strategy: NPCStrategy,
        sprites: NPCSprites,
        color: int
    ):
        super().__init__()
        self.strategy = strategy
        self.sprites = sprites
        self.color = color
        self.path: list[tuple[int, int]] = []
        self.direction: str = "right"
        self.strategy.path = self.path

        from .FleeStrategy import FleeStrategy
        from .ScatterStrategy import ScatterStrategy
        if isinstance(self.strategy, (FleeStrategy, ScatterStrategy)):
            self.strategy.set_npc(self)

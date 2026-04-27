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

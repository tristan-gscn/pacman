from app.game.Actor import Actor
from app.game.npc import NPCStrategy
from models import NPCSprites


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

from ..Actor import Actor
from .NPCStrategy import NPCStrategy
from src.models import NPCSprites


class NPC(Actor):
    """Non-Player Character (Ghost) in the game.

    Controlled by a strategy and moves towards a target.
    """

    def __init__(
        self,
        strategy: NPCStrategy,
        sprites: NPCSprites,
        color: int,
        start_x: float = 0.0,
        start_y: float = 0.0
    ):
        """Initialize an NPC.

        Args:
            strategy (NPCStrategy): The movement strategy for the NPC.
            sprites (NPCSprites): Sprite set for the NPC.
            color (int): Color representing the NPC.
            start_x (float): Initial x-coordinate and respawn point.
            start_y (float): Initial y-coordinate and respawn point.
        """
        super().__init__(x=start_x, y=start_y)
        self.strategy = strategy
        self.base_strategy = strategy
        self.sprites = sprites
        self.color = color
        self.path: list[tuple[int, int]] = []
        self.direction: str = "right"
        self.start_x = start_x
        self.start_y = start_y
        self.is_fleeing = False
        self.respawn_time = 0.0
        self.flee_timer = 0.0
        self.set_strategy(strategy)

    def set_strategy(self, strategy: NPCStrategy) -> None:
        """Set a new movement strategy for the NPC.

        Args:
            strategy (NPCStrategy): The new strategy to apply.
        """
        self.strategy = strategy
        self.strategy.path = self.path

        from .FleeStrategy import FleeStrategy
        from .ScatterStrategy import ScatterStrategy
        if isinstance(self.strategy, (FleeStrategy, ScatterStrategy)):
            self.strategy.set_npc(self)

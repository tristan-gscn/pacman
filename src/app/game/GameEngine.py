from src.app.game.Player import Player
from src.app.game.npc import NPC, ChaseStrategy, AmbushStrategy, \
    FleeStrategy, ScatterStrategy
from src.models import NPCSprites, Color

npc_sprites = NPCSprites(
    fear="npc/fear.png",
    mov_left="npc/mov_left.png",
    mov_right="npc/mov_right.png",
    mov_top="npc/mov_up.png",
    mov_bottom="npc/mov_down.png"
)


class GameEngine:
    def __init__(self) -> None:
        self.npcs: dict[str, NPC] = {
            "Blinky": NPC(
                strategy=ChaseStrategy(),
                sprites=npc_sprites,
                color=Color.RED
            ),
            "Pinky": NPC(
                strategy=AmbushStrategy(),
                sprites=npc_sprites,
                color=Color.MAGENTA
            ),
            "Inky": NPC(
                strategy=FleeStrategy(),
                sprites=npc_sprites,
                color=Color.CYAN
            ),
            "Clyde": NPC(
                strategy=ScatterStrategy(),
                sprites=npc_sprites,
                color=Color.GOLD
            )
        }
        self.npcs["Blinky"].x = 5
        self.npcs["Blinky"].y = 5
        self.npcs["Pinky"].x = 2
        self.npcs["Pinky"].y = 2
        self.npcs["Inky"].x = 3
        self.npcs["Inky"].y = 6
        self.npcs["Clyde"].x = 4
        self.npcs["Clyde"].y = 11
        self.player = Player()

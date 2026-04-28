from src.app.game.Actor import Actor
from src.app.game.Player import Player
from src.app.game.npc import NPC, ChaseStrategy, AmbushStrategy, \
    FleeStrategy, ScatterStrategy
from src.models import NPCSprites, Color

npc_sprites = NPCSprites(
    fear="npc/fear.png",
    mov_left="npc/mov_left.png",
    mov_right="npc/mov_right.png",
    mov_up="npc/mov_up.png",
    mov_down="npc/mov_down.png"
)


class GameEngine:
    def __init__(self) -> None:
        self.move_speed = 3.0
        self._key_to_direction: dict[int, str] = {
            65361: "left",
            97: "left",
            65363: "right",
            100: "right",
            65362: "up",
            119: "up",
            65364: "down",
            115: "down",
        }
        self._direction_vectors: dict[str, tuple[float, float]] = {
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
            "up": (0.0, -1.0),
            "down": (0.0, 1.0),
        }
        self._pressed_directions: list[str] = []
        self._active_direction: str = "left"
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
        self._attach_engine()

    def _attach_engine(self) -> None:
        self.player.set_game_engine(self)
        for npc in self.npcs.values():
            npc.set_game_engine(self)

    def set_player_direction(self, direction: str) -> None:
        self.player.direction = direction

    def move_player(self, dx: float, dy: float) -> None:
        self.player.move(dx, dy)

    def move_actor(self, actor: Actor, dx: float, dy: float) -> None:
        actor.x += dx
        actor.y += dy

    def on_key_press(self, keycode: int) -> None:
        direction = self._key_to_direction.get(keycode)
        if direction is None:
            return
        if direction in self._pressed_directions:
            self._pressed_directions.remove(direction)
        self._pressed_directions.append(direction)
        self._active_direction = direction
        self.set_player_direction(direction)

    def on_key_release(self, keycode: int) -> None:
        direction = self._key_to_direction.get(keycode)
        if direction is None:
            return
        if direction in self._pressed_directions:
            self._pressed_directions.remove(direction)
        if self._active_direction == direction:
            if self._pressed_directions:
                self._active_direction = self._pressed_directions[-1]
            self.set_player_direction(self._active_direction)

    def update(self, delta_seconds: float) -> None:
        self.set_player_direction(self._active_direction)
        dx, dy = self._direction_vectors[self._active_direction]
        self.move_player(
            dx * self.move_speed * delta_seconds,
            dy * self.move_speed * delta_seconds
        )

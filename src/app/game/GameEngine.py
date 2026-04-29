import random

from src.app.game.Actor import Actor
from src.app.game.Player import Player
from src.app.game.PacGum import PacGum
from src.app.game.npc import NPC, ChaseStrategy, AmbushStrategy, \
    FleeStrategy, ScatterStrategy
from src.models import NPCSprites, Color
from src.app.game.MazeUtils import MazeUtils
from src.app.game.FindPath import FindPath

npc_sprites = NPCSprites(fear="npc/fear.png",
                         mov_left="npc/mov_left.png",
                         mov_right="npc/mov_right.png",
                         mov_up="npc/mov_up.png",
                         mov_down="npc/mov_down.png")


class GameEngine:

    def __init__(self, maze: list[list[int]], path_finder: FindPath) -> None:
        self.move_speed = 40 / 320
        self.ghost_speed_factor = 0.7
        self.global_flee = True
        self.pacgum_spawn_chance = 1.0
        self._maze: list[list[int]] = maze
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
        self.path_finder: FindPath = path_finder
        self.npcs: dict[str,
                        NPC] = {
                            "Blinky":
                            NPC(strategy=ChaseStrategy(),
                                sprites=npc_sprites,
                                color=Color.RED),
                            "Pinky":
                            NPC(strategy=AmbushStrategy(),
                                sprites=npc_sprites,
                                color=Color.MAGENTA),
                            "Inky":
                            NPC(strategy=AmbushStrategy(),
                                sprites=npc_sprites,
                                color=Color.CYAN),
                            "Clyde":
                            NPC(strategy=ScatterStrategy(),
                                sprites=npc_sprites,
                                color=Color.GOLD)
                        }
        self.npcs["Blinky"].x = 14
        self.npcs["Blinky"].y = 0
        self.npcs["Pinky"].x = 14
        self.npcs["Pinky"].y = 14
        self.npcs["Inky"].x = 0
        self.npcs["Inky"].y = 14
        self.npcs["Clyde"].x = 10
        self.npcs["Clyde"].y = 10
        self.player = Player()
        self.pacgums: list[PacGum] = []
        self._attach_engine()
        self.set_global_flee(self.global_flee)
        self._generate_pacgums()

    def set_global_flee(self, enabled: bool) -> None:
        self.global_flee = enabled
        for npc in self.npcs.values():
            if enabled:
                npc.set_strategy(FleeStrategy())
            else:
                npc.set_strategy(npc.base_strategy)
            npc.path = []

    def _attach_engine(self) -> None:
        self.player.set_game_engine(self)
        for npc in self.npcs.values():
            npc.set_game_engine(self)

    def _generate_pacgums(self) -> None:
        self.pacgums.clear()
        occupied: set[tuple[int, int]] = set()
        occupied.add((int(round(self.player.x)), int(round(self.player.y))))
        for npc in self.npcs.values():
            occupied.add((int(round(npc.x)), int(round(npc.y))))

        for y, row in enumerate(self._maze):
            for x, cell in enumerate(row):
                if (x, y) in occupied:
                    continue
                if cell == 15:
                    continue
                if random.random() > self.pacgum_spawn_chance:
                    continue
                self.pacgums.append(PacGum(x=float(x), y=float(y)))

    def set_player_direction(self, direction: str) -> None:
        self.player.direction = direction

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

    def update(self) -> None:
        if self._active_direction in ["left", "right"]:
            self.player.y = float(round(self.player.y))
        elif self._active_direction in ["up", "down"]:
            self.player.x = float(round(self.player.x))

        current_cx = round(self.player.x)
        current_cy = round(self.player.y)
        walls: dict[str, bool] = self.check_walls(current_cx, current_cy)

        tolerance = 0.05
        is_aligned_x = abs(self.player.x - current_cx) < tolerance
        is_aligned_y = abs(self.player.y - current_cy) < tolerance

        can_move = True

        if self._active_direction in ["left", "right"] and is_aligned_x:
            self.player.x = float(current_cx)
            if not self.check_movements(walls, self._active_direction):
                can_move = False

        elif self._active_direction in ["up", "down"] and is_aligned_y:
            self.player.y = float(current_cy)
            if not self.check_movements(walls, self._active_direction):
                can_move = False

        if can_move:
            self.set_player_direction(self._active_direction)
            dx, dy = self._direction_vectors[self._active_direction]
            self.move_actor(self.player, dx * self.move_speed,
                            dy * self.move_speed)

        player_cell = (int(round(self.player.x)), int(round(self.player.y)))
        if self.pacgums:
            self.pacgums = [
                pacgum for pacgum in self.pacgums
                if (int(round(pacgum.x)), int(round(pacgum.y))) != player_cell
            ]

    def update_ghosts(self) -> None:
        for ghost in self.npcs.values():
            current_cx = round(ghost.x)
            current_cy = round(ghost.y)

            tolerance = 0.05
            is_aligned_x = abs(ghost.x - current_cx) < tolerance
            is_aligned_y = abs(ghost.y - current_cy) < tolerance

            if is_aligned_x:
                ghost.x = float(current_cx)
            if is_aligned_y:
                ghost.y = float(current_cy)

            if is_aligned_x and is_aligned_y:
                self.gosts_path(ghost)

            can_move = True
            if ghost.direction in ["left", "right"] and is_aligned_x:
                walls = self.check_walls(current_cx, current_cy)
                if not self.check_movements(walls, ghost.direction):
                    can_move = False
            elif ghost.direction in ["up", "down"] and is_aligned_y:
                walls = self.check_walls(current_cx, current_cy)
                if not self.check_movements(walls, ghost.direction):
                    can_move = False

            if can_move:
                dx, dy = self._direction_vectors[ghost.direction]
                speed = self.move_speed * self.ghost_speed_factor
                self.move_actor(ghost, dx * speed, dy * speed)

    def check_walls(self, x: float, y: float) -> dict[str, bool]:
        return MazeUtils.unpack_cell(self._maze[int(y)][int(x)])

    def check_movements(self, walls: dict[str, bool], direction: str) -> bool:
        if direction == "left" and walls["W"]:
            return False
        if direction == "right" and walls["E"]:
            return False
        if direction == "up" and walls["N"]:
            return False
        if direction == "down" and walls["S"]:
            return False
        return True

    def gosts_path(self, ghost: NPC) -> None:
        ghost.path = self.path_finder.a_star_algorithm(
            (int(round(ghost.y)), int(round(ghost.x))),
            ghost.strategy.act(self._maze, self.player))
        self.gosts_direction(ghost)

    def gosts_direction(self, ghost: NPC) -> None:
        dest_x: int
        dest_y: int
        if ghost.path and len(ghost.path) > 1:
            dest_y, dest_x = ghost.path[1]
            if dest_x > ghost.x:
                ghost.direction = "right"
            elif dest_x < ghost.x:
                ghost.direction = "left"
            elif dest_y < ghost.y:
                ghost.direction = "up"
            elif dest_y > ghost.y:
                ghost.direction = "down"

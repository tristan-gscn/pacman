from mazegenerator.mazegenerator import (
    MazeGenerator, )

from src.app.game.Actor import Actor
from src.app.game.Player import Player
from src.app.game.PacGum import PacGum
from src.app.game.SuperPacGum import SuperPacGum
from src.app.game.npc import NPC, ChaseStrategy, AmbushStrategy, \
    FleeStrategy, ScatterStrategy
from src.models import NPCSprites, Color
from src.models.GameStates import GameStates
from src.app.game.MazeUtils import MazeUtils
from src.app.game.FindPath import FindPath

npc_sprites = NPCSprites(fear="npc/fear.png",
                         mov_left="npc/mov_left.png",
                         mov_right="npc/mov_right.png",
                         mov_up="npc/mov_up.png",
                         mov_down="npc/mov_down.png")


class GameEngine:

    def __init__(self, mazegen: MazeGenerator, path_finder: FindPath,
                 game_states: GameStates) -> None:
        self.move_speed = 40 / 320
        self.ghost_speed_factor = 0.7
        self.global_flee = False
        self.game_states: GameStates = game_states
        self._mazegen: MazeGenerator = mazegen
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
            "death": (0.0, 0.0)
        }
        self._pressed_directions: list[str] = []
        self._active_direction: str = "left"
        self.path_finder: FindPath = path_finder
        self.npcs: dict[str, NPC] = {
            "Blinky":
            NPC(strategy=ChaseStrategy(), sprites=npc_sprites,
                color=Color.RED,
                start_x=float(len(self._mazegen.maze[0]) - 1),
                start_y=0.0),
            "Pinky":
            NPC(strategy=AmbushStrategy(),
                sprites=npc_sprites,
                color=Color.MAGENTA,
                start_x=0.0,
                start_y=0.0),
            "Inky":
            NPC(strategy=AmbushStrategy(),
                sprites=npc_sprites,
                color=Color.CYAN,
                start_x=0.0,
                start_y=float(len(self._mazegen.maze) - 1)),
            "Clyde":
            NPC(strategy=ScatterStrategy(),
                sprites=npc_sprites,
                color=Color.GOLD,
                start_x=float(len(self._mazegen.maze[0]) - 1),
                start_y=float(len(self._mazegen.maze) - 1))
        }
        self.player = Player()
        self.rebirth()
        self.pacgums: list[PacGum] = []
        self.super_pacgums: list[SuperPacGum] = []
        self.flee_timer: float = 0.0
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
        self.super_pacgums.clear()
        occupied: set[tuple[int, int]] = set()
        occupied.add((int(round(self.player.x)), int(round(self.player.y))))
        for npc in self.npcs.values():
            occupied.add((int(round(npc.x)), int(round(npc.y))))

        # Define corners for super pacgums
        corners = [
            (0, 0),
            (len(self._mazegen.maze[0]) - 1, 0),
            (0, len(self._mazegen.maze) - 1),
            (len(self._mazegen.maze[0]) - 1, len(self._mazegen.maze) - 1)
        ]
        for cx, cy in corners:
            self.super_pacgums.append(SuperPacGum(x=float(cx), y=float(cy)))
            occupied.add((cx, cy))

        for y, row in enumerate(self._mazegen.maze):
            for x, cell in enumerate(row):
                if (x, y) in occupied:
                    continue
                if cell == 15:
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
            if self.player.direction != "death":
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

        self.eating_pacgum()
        player_cell = (int(round(self.player.x)), int(round(self.player.y)))
        if self.pacgums:
            self.pacgums = [
                pacgum for pacgum in self.pacgums
                if (int(round(pacgum.x)), int(round(pacgum.y))) != player_cell
            ]
        if self.super_pacgums:
            self.super_pacgums = [
                spg for spg in self.super_pacgums
                if (int(round(spg.x)), int(round(spg.y))) != player_cell
            ]

        if self.global_flee:
            import time
            if time.monotonic() > self.flee_timer:
                for npc in self.npcs.values():
                    npc.is_fleeing = False
                    npc.set_strategy(npc.base_strategy)
                    npc.path = []

    def update_ghosts(self) -> None:
        import time
        current_time = time.monotonic()
        for ghost in self.npcs.values():
            if current_time < ghost.respawn_time:
                continue

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
        self.collisions()

    def check_walls(self, x: float, y: float) -> dict[str, bool]:
        return MazeUtils.unpack_cell(self._mazegen.maze[int(y)][int(x)])

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
            ghost.strategy.act(self._mazegen.maze, self.player))
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

    def collisions(self) -> None:
        import time
        if self.player.direction != "death":
            px: float = self.player.x
            py: float = self.player.y
            for ghost in self.npcs.values():
                if time.monotonic() < ghost.respawn_time:
                    continue
                if ((ghost.x - px)**2 + (ghost.y - py)**2) <= 0.64:
                    if ghost.is_fleeing:
                        # Eat ghost
                        ghost.x = ghost.start_x
                        ghost.y = ghost.start_y
                        ghost.is_fleeing = False
                        ghost.set_strategy(ghost.base_strategy)
                        ghost.respawn_time = time.monotonic() + 2.0
                        self.game_states.score += \
                            self.game_states.points_per_ghost
                        ghost.path = []
                    else:
                        self.player.direction = "death"
                        self.game_states.current_lives -= 1
                    return

    def eating_pacgum(self) -> None:
        px, py = int(round(self.player.x)), int(round(self.player.y))

        # Check normal pacgums
        eaten_pacgums = [
            p for p in self.pacgums
            if int(round(p.x)) == px and int(round(p.y)) == py
        ]
        if eaten_pacgums:
            self.game_states.score += \
                len(eaten_pacgums) * self.game_states.points_per_pacgum

        # Check super pacgums
        eaten_super = [
            spg for spg in self.super_pacgums
            if int(round(spg.x)) == px and int(round(spg.y)) == py
        ]
        if eaten_super:
            self.game_states.score += \
                len(eaten_super) * self.game_states.points_per_super_pacgum
            import time
            self.flee_timer = time.monotonic() + 10.0
            for npc in self.npcs.values():
                if time.monotonic() >= npc.respawn_time:
                    npc.is_fleeing = True
                    npc.set_strategy(FleeStrategy())
                    npc.path = []

    def rebirth(self) -> None:
        self.path_finder.maze = self._mazegen.maze
        self.player.direction = "right"
        self.player.x = (len(self._mazegen.maze[0]) // 2
                         - (len(self._mazegen.maze[0]) % 2 == 0))
        self.player.y = (len(self._mazegen.maze) // 2
                         - (len(self._mazegen.maze) % 2 == 0))
        for ghost in self.npcs.values():
            ghost.x = ghost.start_x
            ghost.y = ghost.start_y
            ghost.is_fleeing = False
            ghost.respawn_time = 0.0
            ghost.set_strategy(ghost.base_strategy)

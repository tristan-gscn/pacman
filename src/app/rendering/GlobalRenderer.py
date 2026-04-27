from mlx import Mlx
from src.app.game.GameEngine import GameEngine
from .GameRenderer import GameRenderer
from .SpriteRenderer import SpriteRenderer
import time


class GlobalRenderer:
    """Renderer managing the MLX graphics context and window."""

    mlx: Mlx
    mlx_ptr: int
    win_ptr: int

    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    CELL_SIZE: int = 40
    FRAME_DELAY_SECONDS: float = 0.1

    def __init__(
        self,
        maze: list[list[int]],
        game_engine: GameEngine,
        window_width: int | None = None,
        window_height: int | None = None
    ) -> None:
        """Create the window and start the MLX render loop.

        Args:
            maze (list[list[int]]): Maze grid to render.
            game_engine (GameEngine): Game state with actors and sprites.
            window_width (int | None): Optional override for window width.
            window_height (int | None): Optional override for window height.
        """
        try:
            self.mlx = Mlx()
        except OSError as e:
            raise RuntimeError(
                f"Failed to initialize MLX library. libmlx.so not found: {e}"
            ) from e

        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("Failed to initialize MLX context")

        win_width = window_width or self.WINDOW_WIDTH
        win_height = window_height or self.WINDOW_HEIGHT
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr,
            win_width,
            win_height,
            "Pacman"
        )
        if not self.win_ptr:
            if hasattr(self.mlx, 'mlx_release'):
                self.mlx.mlx_release(self.mlx_ptr)
            raise RuntimeError("Failed to create MLX window")

        self.maze = maze
        self.game_engine = game_engine
        self.game_renderer = GameRenderer(
            self.mlx,
            self.mlx_ptr,
            self.win_ptr,
            win_width=win_width,
            win_height=win_height,
            cell_size=self.CELL_SIZE
        )
        self.sprite_renderer = SpriteRenderer(
            self.mlx,
            self.mlx_ptr,
            self.win_ptr,
            cell_size=self.CELL_SIZE
        )
        self.game_renderer.render_maze(self.maze)

        self.player_frames = self.sprite_renderer.load_sprite_frames(
            self.game_engine.player.sprites.mov_right
        )
        self.npc_frames: dict[str, list[int]] = {}
        for name, npc in self.game_engine.npcs.items():
            self.npc_frames[name] = self.sprite_renderer.load_sprite_frames(
                npc.sprites.mov_right,
                recolor=npc.color
            )

        self.frame_index = 0
        self.last_frame_time = time.monotonic()

        # Register the function that will be called continuously
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render_next_frame, None)

        # Start the blocking loop
        self.mlx.mlx_loop(self.mlx_ptr)

    def render_next_frame(self, _) -> None:
        """Render a single frame and advance animation timing.

        Args:
            _ (object): Unused MLX callback parameter.
        """

        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.game_renderer.render_maze(self.maze)
        now = time.monotonic()
        if now - self.last_frame_time >= self.FRAME_DELAY_SECONDS:
            self.frame_index += 1
            self.last_frame_time = now

        for name, npc in self.game_engine.npcs.items():
            self.sprite_renderer.render_sprite_frame(
                npc.x,
                npc.y,
                self.npc_frames.get(name, []),
                self.frame_index,
                self.game_renderer.offset_x,
                self.game_renderer.offset_y
            )

        self.sprite_renderer.render_sprite_frame(
            self.game_engine.player.x,
            self.game_engine.player.y,
            self.player_frames,
            self.frame_index,
            self.game_renderer.offset_x,
            self.game_renderer.offset_y
        )

        time.sleep(0.05)

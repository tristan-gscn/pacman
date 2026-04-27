from mlx import Mlx
from .GameRenderer import GameRenderer
import time

class GlobalRenderer:
    """Renderer managing the MLX graphics context and window."""

    mlx: Mlx
    mlx_ptr: int
    win_ptr: int

    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    CELL_SIZE: int = 40

    def __init__(
        self,
        maze: list[list[int]],
        window_width: int | None = None,
        window_height: int | None = None
    ) -> None:
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

        game_renderer = GameRenderer(
            self.mlx,
            self.mlx_ptr,
            self.win_ptr,
            win_width=win_width,
            win_height=win_height,
            cell_size=self.CELL_SIZE
        )
        game_renderer.render_maze(maze)

        # Register the function that will be called continuously
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render_next_frame, None)

        # Start the blocking loop
        self.mlx.mlx_loop(self.mlx_ptr)

    def render_next_frame(self, _) -> None:
        """Called continuously by MLX to update the screen."""

        # self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        # TODO: DRAW SOMETHING HERE

        time.sleep(0.05)

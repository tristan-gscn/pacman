from functools import partial
from mlx import Mlx
from src.app.rendering.MazeRenderer import MazeRenderer
from mazegenerator.mazegenerator import MazeGenerator
import time

class GlobalRenderer:
    """Renderer managing the MLX graphics context and window."""

    mlx: Mlx
    mlx_ptr: int
    win_ptr: int

    def __init__(self) -> None:
        try:
            self.mlx = Mlx()
        except OSError as e:
            raise RuntimeError(
                f"Failed to initialize MLX library. libmlx.so not found: {e}"
            ) from e

        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("Failed to initialize MLX context")

        mazegen = MazeGenerator()
        mazegen.generate()

        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr,
            len(mazegen.maze[0]) * 40 + 100,
            len(mazegen.maze) * 40 + 100,
            "Pacman"
        )
        if not self.win_ptr:
            if hasattr(self.mlx, 'mlx_release'):
                self.mlx.mlx_release(self.mlx_ptr)
            raise RuntimeError("Failed to create MLX window")

        pixel_put = partial(self.mlx.mlx_pixel_put, self.mlx_ptr, self.win_ptr)
        MazeRenderer().render_maze(mazegen.maze, pixel_put)

        # Register the function that will be called continuously
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render_next_frame, None)

        # Start the blocking loop
        self.mlx.mlx_loop(self.mlx_ptr)

    def render_next_frame(self, _) -> None:
        """Called continuously by MLX to update the screen."""

        # self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        # TODO: DRAW SOMETHING HERE

        time.sleep(0.05)

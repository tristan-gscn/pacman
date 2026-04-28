from functools import partial
from mlx import Mlx  # type: ignore[import-untyped]
from .MazeRenderer import MazeRenderer


class GameRenderer:
    """Renderer responsible for drawing game entities (maze, etc.)."""

    def __init__(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int,
        cell_size: int
    ) -> None:
        """Initialize the renderer with MLX context and sizing.

        Args:
            mlx (Mlx): MLX wrapper instance.
            mlx_ptr (int): Pointer to MLX context.
            win_ptr (int): Pointer to the MLX window.
            win_width (int): Window width in pixels.
            win_height (int): Window height in pixels.
            cell_size (int): Size of a maze cell in pixels.
        """
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.win_width = win_width
        self.win_height = win_height
        self.cell_size = cell_size
        self.offset_x = 0
        self.offset_y = 0

    def render_maze(self, maze: list[list[int]]) -> None:
        """Render the maze and compute screen offsets.

        Args:
            maze (list[list[int]]): Maze grid where each cell is a wall
            bitmask.
        """
        maze_width = len(maze[0]) * self.cell_size
        maze_height = len(maze) * self.cell_size
        self.offset_x = max((self.win_width - maze_width) // 2, 0)
        self.offset_y = max((self.win_height - maze_height) // 2, 0)

        pixel_put = partial(self.mlx.mlx_pixel_put, self.mlx_ptr, self.win_ptr)
        MazeRenderer().render_maze(
            maze,
            pixel_put,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            cell_size=self.cell_size
        )

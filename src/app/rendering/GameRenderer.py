from functools import partial
from mlx import Mlx
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
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.win_width = win_width
        self.win_height = win_height
        self.cell_size = cell_size

    def render_maze(self, maze: list[list[int]]) -> None:
        maze_width = len(maze[0]) * self.cell_size
        maze_height = len(maze) * self.cell_size
        offset_x = max((self.win_width - maze_width) // 2, 0)
        offset_y = max((self.win_height - maze_height) // 2, 0)

        pixel_put = partial(self.mlx.mlx_pixel_put, self.mlx_ptr, self.win_ptr)
        MazeRenderer().render_maze(
            maze,
            pixel_put,
            offset_x=offset_x,
            offset_y=offset_y,
            cell_size=self.cell_size
        )

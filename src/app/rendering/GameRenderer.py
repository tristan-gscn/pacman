from functools import partial
from mlx import Mlx  # type: ignore[import-untyped]
from src.models import Color
from src.app.game.PacGum import PacGum
from src.app.game.SuperPacGum import SuperPacGum
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
        self._maze_renderer = MazeRenderer()

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
        self._maze_renderer.render_maze(
            maze,
            pixel_put,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            cell_size=self.cell_size
        )

    def render_pacgums(self, pacgums: list[PacGum]) -> None:
        for pacgum in pacgums:
            self.draw_pacgum_at(int(round(pacgum.x)), int(round(pacgum.y)))

    def render_super_pacgums(self, super_pacgums: list[SuperPacGum], visible: bool) -> None:
        if not visible:
            return
        for spg in super_pacgums:
            self.draw_super_pacgum_at(int(round(spg.x)), int(round(spg.y)))

    def redraw_cell(
        self,
        maze: list[list[int]],
        cell_x: int,
        cell_y: int,
        has_pacgum: bool,
        has_super_pacgum: bool = False,
        super_visible: bool = True
    ) -> None:
        self.draw_cell_background(maze, cell_x, cell_y)
        if has_pacgum:
            self.draw_pacgum_at(cell_x, cell_y)
        if has_super_pacgum and super_visible:
            self.draw_super_pacgum_at(cell_x, cell_y)

    def draw_cell_background(
        self,
        maze: list[list[int]],
        cell_x: int,
        cell_y: int
    ) -> None:
        cell = maze[cell_y][cell_x]
        pixel_put = partial(self.mlx.mlx_pixel_put, self.mlx_ptr, self.win_ptr)
        cell_px = cell_x * self.cell_size + self.offset_x
        cell_py = cell_y * self.cell_size + self.offset_y
        for dy in range(self.cell_size):
            for dx in range(self.cell_size):
                pixel_put(cell_px + dx, cell_py + dy, Color.BLACK)
        self._maze_renderer.render_cell(
            cell_x,
            cell_y,
            cell,
            pixel_put,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            cell_size=self.cell_size
        )

    def draw_pacgum_at(self, cell_x: int, cell_y: int) -> None:
        radius = max(self.cell_size // 12, 1)
        pixel_put = self.mlx.mlx_pixel_put
        half_cell = self.cell_size / 2.0
        center_x = int(round(cell_x * self.cell_size + self.offset_x + half_cell))
        center_y = int(round(cell_y * self.cell_size + self.offset_y + half_cell))

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                pixel_put(
                    self.mlx_ptr,
                    self.win_ptr,
                    center_x + dx,
                    center_y + dy,
                    Color.WHITE
                )

    def draw_super_pacgum_at(self, cell_x: int, cell_y: int) -> None:
        radius = max(self.cell_size // 6, 2)
        pixel_put = self.mlx.mlx_pixel_put
        half_cell = self.cell_size / 2.0
        center_x = int(round(cell_x * self.cell_size + self.offset_x + half_cell))
        center_y = int(round(cell_y * self.cell_size + self.offset_y + half_cell))

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                pixel_put(
                    self.mlx_ptr,
                    self.win_ptr,
                    center_x + dx,
                    center_y + dy,
                    Color.WHITE
                )

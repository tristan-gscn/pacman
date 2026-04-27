from typing import Callable

from src.app.game_engine import MazeUtils
from src.models import Color


class MazeRenderer:
    """Renders a maze grid onto a graphical window.

    This class provides methods to iterate through a maze grid and draw
    each cell's walls using a provided pixel drawing function.
    """

    def render_maze(
        self,
        maze: list[list[int]],
        pixel_put: Callable
    ) -> None:
        """Renders the entire maze.

        Args:
            maze (list[list[int]]): A 2D grid representing the maze where each
                integer holds the bitmask of the cell's walls.
            pixel_put (Callable): A function used to draw a single pixel.
        """
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                self._render_cell(x, y, cell, pixel_put)

    def _render_cell(
        self,
        x: int,
        y: int,
        cell: int,
        pixel_put: Callable
    ) -> None:
        """Renders a single cell of the maze at the specified grid coordinates.

        Args:
            x (int): The x-coordinate (column index) of the cell in the grid.
            y (int): The y-coordinate (row index) of the cell in the grid.
            cell (int): The integer bitmask representing the walls of the cell.
            pixel_put (Callable): A function used to draw a single pixel.
        """

        unpacked_cell = MazeUtils().unpack_cell(cell)
        
        px = x * 40 + 50
        py = y * 40 + 50
        
        if unpacked_cell["N"]:
            for k in range(40):
                pixel_put(
                    px + k,
                    py,
                    Color.WHITE
                )
                
        if unpacked_cell["S"]:
            for k in range(40):
                pixel_put(
                    px + k,
                    py + 39,
                    Color.WHITE
                )
                
        if unpacked_cell["E"]:
            for k in range(40):
                pixel_put(
                    px + 39,
                    py + k,
                    Color.WHITE
                )
                
        if unpacked_cell["W"]:
            for k in range(40):
                pixel_put(
                    px,
                    py + k,
                    Color.WHITE
                )

        # If we're in the 42 pattern, color the background in blue
        if cell == 15:
            for i in range(1, 39):
                for j in range(1, 39):
                    pixel_put(
                        px + i,
                        py + j,
                        Color.BLUE
                    )

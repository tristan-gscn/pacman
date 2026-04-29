from mlx import Mlx  # type: ignore[import-untyped]

from src.app.rendering.gui import BaseScreen
from src.models import Color


class InGameHud(BaseScreen):
    def __init__(self) -> None:
        self.score = 0
        self.level = 42
        self.time_remaining = "42:42"
        self.max_lives = 3
        self.current_lives = 3
        self._maze_offset_x = 0
        self._maze_offset_y = 0
        self._maze_width = 0
        self._maze_height = 0

    def update_layout(
        self,
        maze_offset_x: int,
        maze_offset_y: int,
        maze_width: int,
        maze_height: int
    ) -> bool:
        next_offset_x = max(maze_offset_x, 0)
        next_offset_y = max(maze_offset_y, 0)
        next_width = max(maze_width, 0)
        next_height = max(maze_height, 0)

        changed = (
            next_offset_x != self._maze_offset_x
            or next_offset_y != self._maze_offset_y
            or next_width != self._maze_width
            or next_height != self._maze_height
        )

        self._maze_offset_x = next_offset_x
        self._maze_offset_y = next_offset_y
        self._maze_width = next_width
        self._maze_height = next_height
        return changed

    def set_state(
        self,
        score: int,
        level: int,
        time_remaining: str,
        max_lives: int,
        current_lives: int
    ) -> bool:
        changed = (
            score != self.score
            or level != self.level
            or time_remaining != self.time_remaining
            or max_lives != self.max_lives
            or current_lives != self.current_lives
        )

        self.score = score
        self.level = level
        self.time_remaining = time_remaining
        self.max_lives = max_lives
        self.current_lives = current_lives
        return changed

    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        maze_left = self._maze_offset_x
        maze_top = self._maze_offset_y
        maze_width = self._maze_width
        maze_height = self._maze_height
        if maze_width <= 0 or maze_height <= 0:
            maze_left = 0
            maze_top = 0
            maze_width = win_width
            maze_height = win_height

        maze_right = maze_left + maze_width
        maze_bottom = maze_top + maze_height

        top_y = max(maze_top - 30, 0)
        bottom_y = min(maze_bottom + 12, win_height - 30)

        heart_scale = 3
        heart_width = 8 * heart_scale
        heart_height = 7 * heart_scale
        heart_spacing = 6
        total_width = (
            self.max_lives * heart_width
            + max(self.max_lives - 1, 0) * heart_spacing
        )
        hearts_x = max(maze_right - total_width, 0)
        hearts_y = max(bottom_y - (heart_height - 16), 0)

        level_text = f"LEVEL {self.level}"
        time_text = self.time_remaining
        score_text = f"SCORE: {self.score}"

        level_x = max(maze_left, 0)
        time_x = max(maze_right - (len(time_text) * 10), 0)
        score_x = max(maze_left, 0)

        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            level_x,
            top_y,
            Color.WHITE,
            level_text
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            time_x,
            top_y,
            Color.WHITE,
            time_text
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            score_x,
            bottom_y,
            Color.WHITE,
            score_text
        )

        for idx in range(self.max_lives):
            filled = idx < self.current_lives
            heart_x = hearts_x + idx * (heart_width + heart_spacing)
            self._draw_heart(
                mlx,
                mlx_ptr,
                win_ptr,
                heart_x,
                hearts_y,
                heart_scale,
                filled
            )

    def _draw_heart(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        x: int,
        y: int,
        scale: int,
        filled: bool
    ) -> None:
        if filled:
            pattern = [
                "01100110",
                "11111111",
                "11111111",
                "11111111",
                "01111110",
                "00111100",
                "00011000",
            ]
        else:
            pattern = [
                "01100110",
                "10011001",
                "10000001",
                "10000001",
                "01000010",
                "00100100",
                "00011000",
            ]

        for row_index, row in enumerate(pattern):
            for col_index, value in enumerate(row):
                if value != "1":
                    continue
                px = x + col_index * scale
                py = y + row_index * scale
                for dy in range(scale):
                    for dx in range(scale):
                        mlx.mlx_pixel_put(
                            mlx_ptr,
                            win_ptr,
                            px + dx,
                            py + dy,
                            Color.RED
                        )

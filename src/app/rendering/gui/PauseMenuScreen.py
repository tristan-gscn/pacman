from mlx import Mlx  # type: ignore[import-untyped]

from src.app.rendering.gui import BaseScreen
from src.models import Color


class PauseMenuScreen(BaseScreen):
    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        box_width = 300
        box_height = 170
        box_x = max((win_width - box_width) // 2, 0)
        box_y = max((win_height - box_height) // 2, 0)

        self._draw_filled_rect(
            mlx,
            mlx_ptr,
            win_ptr,
            box_x,
            box_y,
            box_width,
            box_height,
            Color.BLACK
        )
        self._draw_rect_outline(
            mlx,
            mlx_ptr,
            win_ptr,
            box_x,
            box_y,
            box_width,
            box_height,
            Color.WHITE
        )

        title = "PAUSE"
        line1 = "Resume (ENTER)"
        line2 = "Exit (ESC)"

        title_x = max(box_x + (box_width // 2) - (len(title) * 6), box_x + 10)
        title_y = box_y + 30
        line1_x = max(box_x + (box_width // 2) - (len(line1) * 5), box_x + 10)
        line1_y = title_y + 50
        line2_x = max(box_x + (box_width // 2) - (len(line2) * 5), box_x + 10)
        line2_y = line1_y + 30

        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            title_x,
            title_y,
            Color.WHITE,
            title
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            line1_x,
            line1_y,
            Color.WHITE,
            line1
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            line2_x,
            line2_y,
            Color.WHITE,
            line2
        )

    def _draw_filled_rect(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        x: int,
        y: int,
        width: int,
        height: int,
        color: int
    ) -> None:
        pixel_put = mlx.mlx_pixel_put
        for py in range(y, y + height):
            for px in range(x, x + width):
                pixel_put(mlx_ptr, win_ptr, px, py, color)

    def _draw_rect_outline(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        x: int,
        y: int,
        width: int,
        height: int,
        color: int
    ) -> None:
        pixel_put = mlx.mlx_pixel_put
        max_x = x + width - 1
        max_y = y + height - 1
        for px in range(x, x + width):
            pixel_put(mlx_ptr, win_ptr, px, y, color)
            pixel_put(mlx_ptr, win_ptr, px, max_y, color)
        for py in range(y, y + height):
            pixel_put(mlx_ptr, win_ptr, x, py, color)
            pixel_put(mlx_ptr, win_ptr, max_x, py, color)

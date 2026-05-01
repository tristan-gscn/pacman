from mlx import Mlx

from .BaseScreen import BaseScreen
from src.models import Color


class InstructionsScreen(BaseScreen):
    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        """Render the instructions screen with title and return hint.

        Args:
            mlx (Mlx): MLX wrapper instance.
            mlx_ptr (int): Pointer to MLX context.
            win_ptr (int): Pointer to the MLX window.
            win_width (int): Window width in pixels.
            win_height (int): Window height in pixels.
        """
        title = "INSTRUCTIONS"
        hint = "Press ESC to return"

        title_x = max((win_width // 2) - (len(title) * 6), 0)
        title_y = max((win_height // 2) - 40, 0)
        hint_x = max((win_width // 2) - (len(hint) * 5), 0)
        hint_y = min(title_y + 40, win_height - 20)

        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            title_x,
            title_y,
            Color.YELLOW,
            title
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            hint_x,
            hint_y,
            Color.WHITE,
            hint
        )

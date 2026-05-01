from pathlib import Path

from mlx import Mlx

from .BaseScreen import BaseScreen
from src.models import Color


class MenuScreen(BaseScreen):

    def __init__(self, file: str) -> None:
        self._logo_ptr: int | None = None
        self._logo_width = 0
        self._logo_height = 0
        self.highscores_file: str = file
        self.text_lines = [
            "Start (ENTER)", "Highscores (SPACE)", "Instructions (SHIFT)",
            "Exit (ESC)"
        ]

    def render(self, mlx: Mlx, mlx_ptr: int, win_ptr: int, win_width: int,
               win_height: int) -> None:

        self._ensure_logo_loaded(mlx, mlx_ptr)
        if self._logo_ptr is not None:
            logo_x = max((win_width - self._logo_width) // 2, 0)
            centered_y = (win_height - self._logo_height) // 2 - 60
            max_y = max(win_height - self._logo_height, 0)
            logo_y = min(max(centered_y, 0), max_y)
            mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, self._logo_ptr,
                                        logo_x, logo_y)
            text_y = min(logo_y + self._logo_height + 40, win_height - 20)
        else:
            text_y = max((win_height // 2) - 20, 0)

        for line in self.text_lines:
            line_x = max((win_width // 2) - (len(line) * 5), 0)
            mlx.mlx_string_put(mlx_ptr, win_ptr, line_x, text_y, Color.WHITE,
                               line)
            text_y += 34

    def _ensure_logo_loaded(self, mlx: Mlx, mlx_ptr: int) -> None:
        if self._logo_ptr is not None:
            return
        logo_path = Path(
            __file__).resolve().parents[4] / "assets" / "game_logo.png"
        img_ptr, width, height = mlx.mlx_png_file_to_image(
            mlx_ptr, str(logo_path))
        if img_ptr:
            self._logo_ptr = img_ptr
            self._logo_width = width
            self._logo_height = height

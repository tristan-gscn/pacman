import json
import os
from pathlib import Path

from mlx import Mlx  # type: ignore[import-untyped]

from src.app.rendering.gui import BaseScreen
from src.models import Color


class MenuScreen(BaseScreen):

    def __init__(self, file: str) -> None:
        self._logo_ptr: int | None = None
        self._logo_width = 0
        self._logo_height = 0
        self.highscores_file: str = file
        self.text_lines = [
            "Start (ENTER)", "Highscores (SPACE)", "Instructions (SHIFT)",
            "Exit (ESC)", "Scores to beat:"
        ]
        self.text_score: list[str] = []

    def render(self, mlx: Mlx, mlx_ptr: int, win_ptr: int, win_width: int,
               win_height: int) -> None:

        self.get_scores()
        final_text: list[str] = self.text_lines + self.text_score
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

        for line in final_text:
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

    def get_scores(self) -> None:
        self.text_score = []
        if not os.path.exists(self.highscores_file):
            self.text_score.append(
                "No score registered yet. Be the first one!")
            return
        try:
            with open(self.highscores_file, "r") as f:
                scores_dict: dict[str, int] = json.load(f)
                for name, score in scores_dict.items():
                    if not isinstance(name, str) or not isinstance(score, int):
                        raise ValueError("Don't touch the saves datas please!")
                    self.text_score.append(f"{name}: {score}")
        except Exception as e:
            print(e)  # TODO Improving the message displayed

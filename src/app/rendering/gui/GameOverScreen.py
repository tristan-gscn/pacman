from mlx import Mlx

from .BaseScreen import BaseScreen
from src.models import Color


class GameOverScreen(BaseScreen):
    def __init__(self, score: int, name: str):
        self.title = "GAME OVER"
        self.score_text = f"Final Score: {score}"
        self.prompt_title = "Enter your name:"
        self.name = name

    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:

        title_x = max((win_width // 2) - (len(self.title) * 6), 0)
        title_y = max((win_height // 2) - 80, 0)
        score_x = max((win_width // 2) - (len(self.score_text) * 5), 0)
        score_y = title_y + 40
        prompt_title_x = max(
            (win_width // 2) - (len(self.prompt_title) * 5),
            0
        )
        prompt_title_y = score_y + 50
        prompt_hint_x = max((win_width // 2) - (len(self.name) * 4), 0)
        prompt_hint_y = prompt_title_y + 30

        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            title_x,
            title_y,
            Color.RED,
            self.title
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            score_x,
            score_y,
            Color.WHITE,
            self.score_text
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            prompt_title_x,
            prompt_title_y,
            Color.WHITE,
            self.prompt_title
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            prompt_hint_x,
            prompt_hint_y,
            Color.YELLOW,
            self.name
        )

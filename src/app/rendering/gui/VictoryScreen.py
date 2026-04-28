from mlx import Mlx  # type: ignore[import-untyped]

from src.app.rendering.gui import BaseScreen
from src.models import Color


class VictoryScreen(BaseScreen):
    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        title = "VICTORY"
        message = "GG, you won!"
        score_text = "Final Score: 42"
        prompt_title = "Entrez votre nom"
        prompt_hint = "(logic coming soon)"

        title_x = max((win_width // 2) - (len(title) * 6), 0)
        title_y = max((win_height // 2) - 90, 0)
        message_x = max((win_width // 2) - (len(message) * 5), 0)
        message_y = title_y + 40
        score_x = max((win_width // 2) - (len(score_text) * 5), 0)
        score_y = message_y + 40
        prompt_title_x = max((win_width // 2) - (len(prompt_title) * 5), 0)
        prompt_title_y = score_y + 50
        prompt_hint_x = max((win_width // 2) - (len(prompt_hint) * 4), 0)
        prompt_hint_y = prompt_title_y + 30

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
            message_x,
            message_y,
            Color.WHITE,
            message
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            score_x,
            score_y,
            Color.WHITE,
            score_text
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            prompt_title_x,
            prompt_title_y,
            Color.WHITE,
            prompt_title
        )
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            prompt_hint_x,
            prompt_hint_y,
            Color.YELLOW,
            prompt_hint
        )

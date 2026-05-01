from mlx import Mlx  # type: ignore[import-untyped]

from src.app.rendering.gui import BaseScreen
from src.models import Color


class HighscoresScreen(BaseScreen):
    def __init__(self, filename: str):
        self.filename = filename

    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        title = "HIGHSCORES"
        hint = "Press ESC to return"

        title_x = max((win_width // 2) - (len(title) * 6), 0)
        title_y = 50
        hint_x = max((win_width // 2) - (len(hint) * 5), 0)
        hint_y = win_height - 50

        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            title_x,
            title_y,
            Color.YELLOW,
            title
        )

        import os
        import json
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    scores = json.load(f)
                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                
                start_y = title_y + 60
                for i, (name, score) in enumerate(sorted_scores[:10]):
                    text = f"{i+1}. {str(name).upper()}: {score}"
                    x = max((win_width // 2) - (len(text) * 5), 0)
                    y = start_y + i * 30
                    mlx.mlx_string_put(mlx_ptr, win_ptr, x, y, Color.WHITE, text)
            except Exception:
                pass

        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            hint_x,
            hint_y,
            Color.WHITE,
            hint
        )

from mlx import Mlx  # type: ignore[import-untyped]

from src.app.rendering.gui import BaseScreen


class InGameHud(BaseScreen):
    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        return

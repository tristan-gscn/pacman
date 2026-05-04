from mlx import Mlx

from .BaseScreen import BaseScreen
from src.models import Color


class InstructionsScreen(BaseScreen):
    def __init__(
        self,
        points_per_pacgum: int = 5,
        points_per_super_pacgum: int = 4,
        points_per_ghost: int = 5
    ) -> None:
        self._lines: list[tuple[str, int]] = [
            ("MOVEMENT", Color.YELLOW),
            ("WASD / Arrow Keys", Color.WHITE),
            ("", Color.WHITE),
            ("GOAL", Color.YELLOW),
            ("Eat all pacgums to clear the level", Color.WHITE),
            ("Survive 10 levels to win", Color.WHITE),
            ("", Color.WHITE),
            ("SCORING", Color.YELLOW),
            (
                f"Pacgum: {points_per_pacgum} pts"
                f"  |  Super: {points_per_super_pacgum} pts",
                Color.WHITE,
            ),
            (f"Ghost (flee): {points_per_ghost} pts", Color.WHITE),
            ("", Color.WHITE),
            ("PAUSE", Color.YELLOW),
            ("ESC: Pause  |  ENTER: Resume", Color.WHITE),
            ("ESC from pause: Main menu", Color.WHITE),
        ]

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
        total_lines = len(self._lines) + 1
        block_height = total_lines * 25
        start_y = max((win_height - block_height) // 2, 20)

        for _ in range(2):
            for i, (text, color) in enumerate(self._lines):
                char_w = 6 if color == Color.YELLOW else 5
                tx = max((win_width // 2) - (len(text) * char_w), 0)
                ty = start_y + i * 25
                mlx.mlx_string_put(
                    mlx_ptr,
                    win_ptr,
                    tx,
                    ty,
                    color,
                    text
                )

        hint = "Press ESC to return"
        hx = max((win_width // 2) - (len(hint) * 5), 0)
        hy = start_y + block_height
        mlx.mlx_string_put(
            mlx_ptr,
            win_ptr,
            hx,
            hy,
            Color.WHITE,
            hint
        )

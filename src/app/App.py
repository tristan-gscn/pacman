import os

from mazegenerator.mazegenerator import (  # type: ignore[import-untyped]
    MazeGenerator,
)
from src.parsing import ConfigParser
from src.app.game.GameEngine import GameEngine
from src.app.rendering import GlobalRenderer
from src.models import UIMode
from src.app.game.FindPath import FindPath


class App:
    """High-level application entry point for game and rendering management."""

    _KEY_ENTER = 65293
    _KEY_SPACE = 32
    _KEY_SHIFT_LEFT = 65505
    _KEY_SHIFT_RIGHT = 65506
    _KEY_ESCAPE = 65307

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = config_path
        self.game_engine: GameEngine | None = None
        self.renderer: GlobalRenderer | None = None
        self.ui_mode = UIMode.MAIN_MENU

    def run(self) -> None:
        try:
            print(ConfigParser().parse(self.config_path))
        except Exception as e:
            print(f"{type(e).__name__} error occured while parsing: {e}")

        try:
            mazegen = MazeGenerator()
            mazegen.generate()
            path_finder: FindPath = FindPath(mazegen.maze)
            self.game_engine = GameEngine(mazegen.maze, path_finder)
            self.renderer = GlobalRenderer(
                mazegen.maze,
                self.game_engine,
                key_press_callback=self._on_key_press,
                key_release_callback=self._on_key_release,
                update_callback=self._on_update,
                ui_mode_provider=self.get_ui_mode
            )
        except RuntimeError as e:
            print(f"Renderer initialization skipped: {e}")

    def get_ui_mode(self) -> UIMode:
        return self.ui_mode

    def _on_key_press(self, keycode: int) -> None:
        """Handle key press events to update movement direction.

        Args:
            keycode (int): MLX key code for the pressed key.
        """
        if self.ui_mode == UIMode.MAIN_MENU:
            self._handle_main_menu_key(keycode)
            return
        if self.ui_mode in (UIMode.HIGHSCORES, UIMode.INSTRUCTIONS):
            if keycode == self._KEY_ESCAPE:
                self.ui_mode = UIMode.MAIN_MENU
            return
        if self.ui_mode == UIMode.PAUSE_MENU:
            if keycode == self._KEY_ENTER:
                self.ui_mode = UIMode.IN_GAME
            elif keycode == self._KEY_ESCAPE:
                self.ui_mode = UIMode.MAIN_MENU
            return
        if self.ui_mode != UIMode.IN_GAME:
            return
        if keycode == self._KEY_ESCAPE:
            self.ui_mode = UIMode.PAUSE_MENU
            return
        if self.game_engine is not None:
            self.game_engine.on_key_press(keycode)

    def _handle_main_menu_key(self, keycode: int) -> None:
        if keycode == self._KEY_ENTER:
            self.ui_mode = UIMode.IN_GAME
            return
        if keycode == self._KEY_SPACE:
            self.ui_mode = UIMode.HIGHSCORES
            return
        if keycode in (self._KEY_SHIFT_LEFT, self._KEY_SHIFT_RIGHT):
            self.ui_mode = UIMode.INSTRUCTIONS
            return
        if keycode == self._KEY_ESCAPE:
            self._exit_app()

    def _exit_app(self) -> None:
        if self.renderer is not None:
            self.renderer.close()
        os._exit(0)

    def _on_key_release(self, keycode: int) -> None:
        """Handle key release events to stop or switch movement.

        Args:
            keycode (int): MLX key code for the released key.
        """
        if self.ui_mode != UIMode.IN_GAME:
            if self.ui_mode != UIMode.PAUSE_MENU:
                return
        if self.game_engine is not None:
            self.game_engine.on_key_release(keycode)

    def _on_update(self) -> None:
        """Move the player continuously based on current input state.
        """
        if self.game_engine is None:
            return
        if self.ui_mode != UIMode.IN_GAME:
            return
        self.game_engine.update()
        self.game_engine.update_ghosts()
        self.collisions()

    def collisions(self) -> None:
        px: int = self.game_engine.player.x
        py: int = self.game_engine.player.y
        for ghost in self.game_engine.npcs.values():
            if ((ghost.x - px)**2 + (ghost.y - py)**2) <= 30:
                self.renderer._hud.current_lives -= 1



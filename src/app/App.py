import os

from mazegenerator.mazegenerator import (  # type: ignore[import-untyped]
    MazeGenerator, )
from src.parsing import ConfigParser
from src.app.game.GameEngine import GameEngine
from src.app.rendering import GlobalRenderer
from src.models import UIMode
from src.models.Configuration import Configuration
from src.models.GameStates import GameStates
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
        try:
            self.config: Configuration = ConfigParser().parse(self.config_path)
        except Exception as e:
            print(f"{type(e).__name__} error occured while parsing: {e}")
        self.game_states: GameStates = GameStates(
            time_remaining=self.config.level_max_time,
            max_lives=self.config.lives,
            points_per_ghost=self.config.points_per_ghost,
            points_per_pacgum=self.config.points_per_pacgum,
            points_per_super_pacgum=self.config.points_per_super_pacgum
            )
        self.game_engine: GameEngine | None = None
        self.renderer: GlobalRenderer | None = None
        self.ui_mode = UIMode.MAIN_MENU
        self.mazegen = MazeGenerator()

    def run(self) -> None:
        try:
            self.mazegen.generate()
            path_finder: FindPath = FindPath(self.mazegen.maze)
            self.game_engine = GameEngine(self.mazegen.maze, path_finder,
                                          self.game_states)
            self.renderer = GlobalRenderer(
                self.mazegen.maze,
                self.game_engine,
                key_press_callback=self._on_key_press,
                key_release_callback=self._on_key_release,
                update_callback=self._on_update,
                ui_mode_provider=self.get_ui_mode,
                ui_mode_setter=self.set_ui_mode,
                )
        except RuntimeError as e:
            print(f"Renderer initialization skipped: {e}")

    def get_ui_mode(self) -> UIMode:
        return self.ui_mode

    def set_ui_mode(self, ui_mode: UIMode) -> None:
        self.ui_mode = ui_mode

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
        if self.game_engine is not None and \
           self.game_engine.player.direction != "death":
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
        if len(self.game_engine.pacgums) <= 0:
            self.mazegen.generate()
            self.game_engine.rebirth()
            self.game_engine._generate_pacgums()
            self.game_states.time_remaining = self.config.level_max_time  # TODO need to update with config file
            self.game_states.level += 1
        if self.game_engine is None:
            return
        if self.ui_mode != UIMode.IN_GAME:
            return
        if self.game_engine.player.direction != "death":
            self.game_engine.update()
            self.game_engine.update_ghosts()


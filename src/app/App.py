import os
import json
from typing import Any

from mazegenerator.mazegenerator import MazeGenerator
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
    _KEY_BACKSPACE = 65288
    _KEY_UP = 65362
    _KEY_DOWN = 65364
    _KEY_LEFT = 65361
    _KEY_RIGHT = 65363
    _KEY_B = 98
    _KEY_A = 97

    _KONAMI_CODE = [
        _KEY_UP, _KEY_UP, _KEY_DOWN, _KEY_DOWN,
        _KEY_LEFT, _KEY_RIGHT, _KEY_LEFT, _KEY_RIGHT,
        _KEY_B, _KEY_A, _KEY_ENTER,
    ]

    def __init__(self, config_path: str = "config.json") -> None:
        """Initialize the application.

        Args:
            config_path (str): Path to the JSON configuration file.
        """
        self.config_path = config_path
        try:
            self.config: Configuration = ConfigParser().parse(self.config_path)
        except Exception as e:
            print(f"{type(e).__name__} error occured while parsing: {e}")
            os._exit(1)
        self.game_states: GameStates = GameStates(
            score=0,
            level=1,
            time_remaining=self.config.level_max_time,
            max_lives=self.config.lives,
            current_lives=self.config.lives,
            points_per_ghost=self.config.points_per_ghost,
            points_per_pacgum=self.config.points_per_pacgum,
            points_per_super_pacgum=self.config.points_per_super_pacgum)
        self.game_engine: GameEngine | None = None
        self.renderer: GlobalRenderer | None = None
        self.current_input: str = ""
        self.ui_mode = UIMode.MAIN_MENU
        self.mazegen = MazeGenerator(size=(self.config.width,
                                           self.config.height))
        self._konami_buffer: list[int] = []

    def run(self) -> None:
        """Initialize and start the game engine and renderer.

        This method generates the initial maze, sets up the game engine,
        and starts the global renderer with necessary callbacks.
        """
        try:
            self.mazegen.generate()
            path_finder: FindPath = FindPath(self.mazegen.maze)
            self.game_engine = GameEngine(self.mazegen, path_finder,
                                          self.game_states)
            self.renderer = GlobalRenderer(
                self.mazegen,
                self.game_engine,
                self.current_input,
                self.config.highscore_filename,
                key_press_callback=self._on_key_press,
                key_release_callback=self._on_key_release,
                update_callback=self._on_update,
                ui_mode_provider=self.get_ui_mode,
                ui_mode_setter=self.set_ui_mode,
                input_provider=self.get_current_input,
            )
        except RuntimeError as e:
            print(f"Renderer initialization skipped: {e}")

    def get_ui_mode(self) -> UIMode:
        """Get the current UI mode.

        Returns:
            UIMode: The current UI mode of the application.
        """
        return self.ui_mode

    def set_ui_mode(self, ui_mode: UIMode) -> None:
        """Set the current UI mode.

        Args:
            ui_mode (UIMode): The new UI mode to set.
        """
        self.ui_mode = ui_mode

    def get_current_input(self) -> str:
        """Get the current user input string.

        Returns:
            str: The current string input by the user.
        """
        return self.current_input

    def _on_key_press(self, keycode: int) -> None:
        """Handle key press events to update movement direction.

        Args:
            keycode (int): MLX key code for the pressed key.
        """
        if self.ui_mode == UIMode.MAIN_MENU:
            self._handle_main_menu_key(keycode)
            return
        if self.ui_mode in (UIMode.GAME_OVER, UIMode.VICTORY):
            self._handle_lose_victory_key(keycode)
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
            elif (keycode == self._KEY_SPACE
                  and self.game_engine is not None
                  and self.game_engine.cheat_mode):
                self.advance_level()
                if self.ui_mode != UIMode.VICTORY:
                    self.ui_mode = UIMode.IN_GAME
            return
        if self.ui_mode != UIMode.IN_GAME:
            return
        if keycode == self._KEY_ESCAPE:
            self.ui_mode = UIMode.PAUSE_MENU
            return
        self._check_konami_code(keycode)
        if self.game_engine is not None and \
           self.game_engine.player.direction != "death":
            self.game_engine.on_key_press(keycode)

    def _handle_main_menu_key(self, keycode: int) -> None:
        """Handle key presses specifically for the main menu.

        Args:
            keycode (int): MLX key code for the pressed key.
        """
        if keycode == self._KEY_ENTER:
            self.current_input = ""
            self.game_states.score = 0
            self.game_states.level = 1
            self.game_states.time_remaining = self.config.level_max_time
            self.game_states.current_lives = self.config.lives
            if self.game_engine is not None:
                self.mazegen.generate()
                self.game_engine.rebirth()
                self.game_engine._generate_pacgums()
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

    def _handle_lose_victory_key(self, keycode: int) -> None:
        """Handle key presses for game over and victory screens.

        Allows the user to type their name and save high scores.

        Args:
            keycode (int): MLX key code for the pressed key.
        """
        if keycode == self._KEY_ENTER:
            if not self.current_input.strip():
                return
            if "/" in self.config.highscore_filename:
                index: int = self.config.highscore_filename.rfind("/") + 1
                os.makedirs(self.config.highscore_filename[:index],
                            exist_ok=True)
            try:
                scores_dict: dict[str, int] = {}

                if os.path.exists(self.config.highscore_filename):
                    with open(self.config.highscore_filename, "r") as f:
                        loaded_scores: dict[str, Any] = json.load(f)
                        for name, score in loaded_scores.items():
                            if not isinstance(name, str) or not isinstance(
                                    score, int):
                                raise ValueError(
                                    "Don't touch the saves datas please!")
                            scores_dict[name] = score

                new_name = self.current_input.upper().strip()
                new_score = self.game_states.score

                # Load existing scores and sort them to find the 10th score
                existing_scores = sorted(
                    scores_dict.items(),
                    key=lambda x: x[1], reverse=True
                )

                can_save = False
                if len(existing_scores) < 10:
                    can_save = True
                else:
                    tenth_score = existing_scores[9][1]
                    if new_score > tenth_score:
                        can_save = True
                    elif new_name in scores_dict and \
                            new_score > scores_dict[new_name]:
                        can_save = True

                if can_save:
                    if new_name in scores_dict:
                        if new_score > scores_dict[new_name]:
                            scores_dict[new_name] = new_score
                    else:
                        scores_dict[new_name] = new_score

                    # Sort by score descending and take top 10
                    sorted_scores = sorted(scores_dict.items(),
                                           key=lambda x: x[1],
                                           reverse=True)[:10]
                    scores_dict = dict(sorted_scores)
                    with open(self.config.highscore_filename, "w") as f:
                        f.write(json.dumps(scores_dict, indent=2))
            except Exception as e:
                print(e)  # TODO Improving the message displayed
            self.ui_mode = UIMode.MAIN_MENU
            return
        if keycode == self._KEY_BACKSPACE:
            self.current_input = self.current_input[:-1]
            return
        if 32 <= keycode <= 126 and len(self.current_input) < 10:
            self.current_input += chr(keycode).upper()

    def _check_konami_code(self, keycode: int) -> None:
        """Check if the Konami code sequence has been entered.

        Toggles cheat mode when the full sequence is detected.

        Args:
            keycode (int): MLX key code for the pressed key.
        """
        self._konami_buffer.append(keycode)
        if len(self._konami_buffer) > len(self._KONAMI_CODE):
            self._konami_buffer.pop(0)
        if self._konami_buffer == self._KONAMI_CODE:
            if self.game_engine is not None:
                self.game_engine.toggle_cheat_mode()
            self._konami_buffer.clear()

    def advance_level(self) -> None:
        """Advance to the next level."""
        if self.game_engine is None:
            return
        if self.game_states.level >= self.config.levels_to_generate:
            self.ui_mode = UIMode.VICTORY
            return
        self.mazegen.generate()
        self.game_engine.rebirth()
        self.game_engine._generate_pacgums()
        self.game_states.time_remaining = self.config.level_max_time
        self.game_states.level += 1

    def _exit_app(self) -> None:
        """Close the renderer and exit the application."""
        if self.renderer is not None:
            self.renderer.close()
        # Using a proper exit or returning to let the loop end is cleaner
        # but MLX often requires os._exit(0)
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

    def _on_update(self, dt: float = 0.0) -> None:
        """Update game logic on each frame.

        Args:
            dt (float): Delta time since the last update. Defaults to 0.0.
        """
        if self.game_engine is None:
            return
        if len(self.game_engine.pacgums) <= 0 and len(
                self.game_engine.super_pacgums) <= 0:
            if self.game_states.level >= self.config.levels_to_generate:
                self.ui_mode = UIMode.VICTORY
                return
            self.mazegen.generate()
            self.game_engine.rebirth()
            self.game_engine._generate_pacgums()
            self.game_states.time_remaining = self.config.level_max_time
            self.game_states.level += 1
        if self.ui_mode != UIMode.IN_GAME:
            return
        if self.game_engine.player.direction != "death":
            self.game_engine.update()
            self.game_engine.update_ghosts()

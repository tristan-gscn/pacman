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

    def __init__(self, config_path: str = "config.json") -> None:
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

    def run(self) -> None:
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
        return self.ui_mode

    def set_ui_mode(self, ui_mode: UIMode) -> None:
        self.ui_mode = ui_mode

    def get_current_input(self) -> str:
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

    def _exit_app(self) -> None:
        if self.renderer is not None:
            self.renderer.close()
        # Using a proper exit or returning to let the loop end is cleaner
        # but MLX often requires os._exit(0)
        import sys
        sys.exit(0)

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
        """Move the player continuously based on current input state.
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

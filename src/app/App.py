from mazegenerator.mazegenerator import (  # type: ignore[import-untyped]
    MazeGenerator,
)
from src.parsing import ConfigParser
from src.app.game.GameEngine import GameEngine
from src.app.rendering import GlobalRenderer


class App:
    """High-level application entry point for game and rendering management."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = config_path
        self.game_engine: GameEngine | None = None
        self.renderer: GlobalRenderer | None = None

    def run(self) -> None:
        try:
            print(ConfigParser().parse(self.config_path))
        except Exception as e:
            print(f"{type(e).__name__} error occured while parsing: {e}")

        try:
            mazegen = MazeGenerator()
            mazegen.generate()
            self.game_engine = GameEngine()
            self.renderer = GlobalRenderer(
                mazegen.maze,
                self.game_engine,
                key_press_callback=self._on_key_press,
                key_release_callback=self._on_key_release,
                update_callback=self._on_update
            )
        except RuntimeError as e:
            print(f"Renderer initialization skipped: {e}")

    def _on_key_press(self, keycode: int) -> None:
        """Handle key press events to update movement direction.

        Args:
            keycode (int): MLX key code for the pressed key.
        """
        if self.game_engine is not None:
            self.game_engine.on_key_press(keycode)

    def _on_key_release(self, keycode: int) -> None:
        """Handle key release events to stop or switch movement.

        Args:
            keycode (int): MLX key code for the released key.
        """
        if self.game_engine is not None:
            self.game_engine.on_key_release(keycode)

    def _on_update(self, delta_seconds: float) -> None:
        """Move the player continuously based on current input state.

        Args:
            delta_seconds (float): Elapsed time since last update.
        """
        if self.game_engine is None:
            return
        self.game_engine.update(delta_seconds)

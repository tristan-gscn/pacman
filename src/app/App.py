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
        self.move_speed = 3.0
        self._key_to_direction: dict[int, str] = {
            65361: "left",
            97: "left",
            65363: "right",
            100: "right",
            65362: "up",
            119: "up",
            65364: "down",
            115: "down",
        }
        self._direction_vectors: dict[str, tuple[float, float]] = {
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
            "up": (0.0, -1.0),
            "down": (0.0, 1.0),
        }
        self._pressed_directions: list[str] = []
        self._active_direction: str | None = None

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
        direction = self._key_to_direction.get(keycode)
        if direction is None:
            return
        if direction in self._pressed_directions:
            self._pressed_directions.remove(direction)
        self._pressed_directions.append(direction)
        self._active_direction = direction
        if self.game_engine is not None:
            self.game_engine.player.direction = direction

    def _on_key_release(self, keycode: int) -> None:
        """Handle key release events to stop or switch movement.

        Args:
            keycode (int): MLX key code for the released key.
        """
        direction = self._key_to_direction.get(keycode)
        if direction is None:
            return
        if direction in self._pressed_directions:
            self._pressed_directions.remove(direction)
        if self._active_direction == direction:
            self._active_direction = (
                self._pressed_directions[-1]
                if self._pressed_directions
                else None
            )
            if self._active_direction and self.game_engine is not None:
                self.game_engine.player.direction = self._active_direction

    def _on_update(self, delta_seconds: float) -> None:
        """Move the player continuously based on current input state.

        Args:
            delta_seconds (float): Elapsed time since last update.
        """
        if self.game_engine is None or self._active_direction is None:
            return
        if self.game_engine is not None:
            self.game_engine.player.direction = self._active_direction
        dx, dy = self._direction_vectors[self._active_direction]
        self.game_engine.player.x += dx * self.move_speed * delta_seconds
        self.game_engine.player.y += dy * self.move_speed * delta_seconds

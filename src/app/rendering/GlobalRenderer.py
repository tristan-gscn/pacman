from typing import Callable
import math
import time

from mlx import Mlx  # type: ignore[import-untyped]
from src.app.game.GameEngine import GameEngine
from src.models import UIMode
from .GameRenderer import GameRenderer
from .SpriteRenderer import SpriteRenderer
from .gui import (
    MenuScreen,
    InGameHud,
    PauseMenuScreen,
    GameOverScreen,
    VictoryScreen,
    HighscoresScreen,
    InstructionsScreen,
)


class GlobalRenderer:
    """Renderer managing the MLX graphics context and window."""

    mlx: Mlx
    mlx_ptr: int
    win_ptr: int

    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    CELL_SIZE: int = 40
    FRAME_DELAY_SECONDS: float = 0.15

    def __init__(
            self,
            maze: list[list[int]],
            game_engine: GameEngine,
            window_width: int | None = None,
            window_height: int | None = None,
            key_press_callback: Callable[[int], None] | None = None,
            key_release_callback: Callable[[int], None] | None = None,
            update_callback: Callable[[float], None] | None = None,
            ui_mode_provider: Callable[[], UIMode] | None = None
    ) -> None:
        """Create the window and start the MLX render loop.

        Args:
            maze (list[list[int]]): Maze grid to render.
            game_engine (GameEngine): Game state with actors and sprites.
            window_width (int | None): Optional override for window width.
            window_height (int | None): Optional override for window height.
            key_press_callback (Callable[[int], None] | None): Optional handler
                for key press events.
            key_release_callback (Callable[[int], None] | None): Optional
                handler for key release events.
            update_callback (Callable[[float], None] | None): Optional
                per-frame update handler receiving delta seconds.
            ui_mode_provider (Callable[[], UIMode] | None): Optional provider
                to get the current UI state.
        """
        try:
            self.mlx = Mlx()
        except OSError as e:
            raise RuntimeError(
                f"Failed to initialize MLX library. libmlx.so not found: {e}"
            ) from e

        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("Failed to initialize MLX context")

        win_width = window_width or self.WINDOW_WIDTH
        win_height = window_height or self.WINDOW_HEIGHT
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr,
            win_width,
            win_height,
            "Pacman"
        )
        if not self.win_ptr:
            if hasattr(self.mlx, 'mlx_release'):
                self.mlx.mlx_release(self.mlx_ptr)
            raise RuntimeError("Failed to create MLX window")

        self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)

        self.maze = maze
        self.game_engine = game_engine
        self.win_width = win_width
        self.win_height = win_height
        self._key_press_callback = key_press_callback
        self._key_release_callback = key_release_callback
        self._update_callback = update_callback
        self._ui_mode_provider = ui_mode_provider
        self._last_ui_mode: UIMode | None = None
        self._needs_full_redraw = True
        self._hud_dirty = True
        self._prev_actor_positions: dict[str, tuple[float, float]] = {}
        self._prev_pacgum_cells: set[tuple[int, int]] = set()
        self._gui_screens = {
            UIMode.MAIN_MENU: MenuScreen(),
            UIMode.PAUSE_MENU: PauseMenuScreen(),
            UIMode.GAME_OVER: GameOverScreen(),
            UIMode.VICTORY: VictoryScreen(),
            UIMode.HIGHSCORES: HighscoresScreen(),
            UIMode.INSTRUCTIONS: InstructionsScreen(),
        }
        self._hud = InGameHud()
        self.game_renderer = GameRenderer(
            self.mlx,
            self.mlx_ptr,
            self.win_ptr,
            win_width=win_width,
            win_height=win_height,
            cell_size=self.CELL_SIZE
        )
        self.sprite_renderer = SpriteRenderer(
            self.mlx,
            self.mlx_ptr,
            self.win_ptr,
            cell_size=self.CELL_SIZE
        )

        self.player_frames = {
            "left": self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_left
            ),
            "right": self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_right
            ),
            "up": self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_up
            ),
            "down": self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_down
            ),
        }
        self.npc_frames: dict[str, list[int]] = {}
        for name, npc in self.game_engine.npcs.items():
            self.npc_frames[name] = self.sprite_renderer.load_sprite_frames(
                npc.sprites.mov_right,
                recolor=npc.color
            )
        first_npc = next(iter(self.game_engine.npcs.values()), None)
        self.npc_fear_frames = []
        if first_npc is not None:
            self.npc_fear_frames = self.sprite_renderer.load_sprite_frames(
                first_npc.sprites.fear
            )

        self.frame_index = 0
        self.last_frame_time = time.monotonic()
        self.last_update_time = self.last_frame_time

        # Register the function that will be called continuously
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render_next_frame, None)
        if self._key_press_callback is not None:
            self.mlx.mlx_hook(
                self.win_ptr,
                2, 1 << 0,
                self._handle_key_press,
                None
            )
        if self._key_release_callback is not None:
            self.mlx.mlx_hook(
                self.win_ptr,
                3, 1 << 1,
                self._handle_key_release,
                None
            )

        # Start the blocking loop
        self.mlx.mlx_loop(self.mlx_ptr)

    def render_next_frame(self, _: object) -> None:
        """Render a single frame and advance animation timing.

        Args:
            _ (object): Unused MLX callback parameter.
        """
        ui_mode = None
        if self._ui_mode_provider is not None:
            ui_mode = self._ui_mode_provider()

        if ui_mode is not None and ui_mode != UIMode.IN_GAME:
            screen = self._gui_screens.get(ui_mode)

            if ui_mode != self._last_ui_mode:
                if ui_mode == UIMode.PAUSE_MENU:
                    self._needs_full_redraw = True
                    self._render_game_frame(update_state=False)
                else:
                    self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
                if screen is not None:
                    screen.render(
                        self.mlx,
                        self.mlx_ptr,
                        self.win_ptr,
                        self.win_width,
                        self.win_height
                    )
                self._last_ui_mode = ui_mode
            return

        if ui_mode == UIMode.IN_GAME and ui_mode != self._last_ui_mode:
            self._needs_full_redraw = True

        self._last_ui_mode = ui_mode
        self._render_game_frame(update_state=True)

    def _render_game_frame(self, update_state: bool) -> None:
        now = time.monotonic()
        self.last_update_time = now

        if update_state and self._update_callback is not None:
            self._update_callback()

        if self._needs_full_redraw:
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            self.game_renderer.render_maze(self.maze)
            self._update_hud_layout()
            self.game_renderer.render_pacgums(self.game_engine.pacgums)
            self._render_sprites()
            self._render_hud(force=True)
            self._cache_frame_state()
            self._needs_full_redraw = False
            return

        self._update_hud_layout()
        self._render_incremental()
        if update_state and now - self.last_frame_time >= self.FRAME_DELAY_SECONDS:
            self.frame_index += 1
            self.last_frame_time = now

        self._render_sprites()
        self._render_hud(force=False)
        self._cache_frame_state()

    def _update_hud_layout(self) -> None:
        maze_width = 0
        maze_height = 0
        if self.maze:
            maze_width = len(self.maze[0]) * self.CELL_SIZE
            maze_height = len(self.maze) * self.CELL_SIZE
        if self._hud.update_layout(
            self.game_renderer.offset_x,
            self.game_renderer.offset_y,
            maze_width,
            maze_height
        ):
            self._hud_dirty = True

    def _render_hud(self, force: bool) -> None:
        if not force and not self._hud_dirty:
            return
        self._hud.render(
            self.mlx,
            self.mlx_ptr,
            self.win_ptr,
            self.win_width,
            self.win_height
        )
        self._hud_dirty = False

    def _render_incremental(self) -> None:
        current_pacgum_cells = {
            (int(round(pacgum.x)), int(round(pacgum.y)))
            for pacgum in self.game_engine.pacgums
        }
        removed_cells = self._prev_pacgum_cells - current_pacgum_cells
        self._hud.score += len(removed_cells)
        added_cells = current_pacgum_cells - self._prev_pacgum_cells

        cells_to_redraw: set[tuple[int, int]] = set(removed_cells)
        for prev_x, prev_y in self._prev_actor_positions.values():
            for cell in self._covered_cells(prev_x, prev_y):
                cells_to_redraw.add(cell)

        for cell_x, cell_y in cells_to_redraw:
            if not self._is_valid_cell(cell_x, cell_y):
                continue
            has_pacgum = (cell_x, cell_y) in current_pacgum_cells
            self.game_renderer.redraw_cell(self.maze, cell_x, cell_y, has_pacgum)

        for cell_x, cell_y in added_cells - cells_to_redraw:
            if not self._is_valid_cell(cell_x, cell_y):
                continue
            self.game_renderer.draw_pacgum_at(cell_x, cell_y)

    def _render_sprites(self) -> None:
        for name, npc in self.game_engine.npcs.items():
            frames = self.npc_frames.get(name, [])
            if getattr(self.game_engine, "global_flee", False):
                frames = self.npc_fear_frames
            self.sprite_renderer.render_sprite_frame(
                npc.x,
                npc.y,
                frames,
                self.frame_index,
                self.game_renderer.offset_x,
                self.game_renderer.offset_y
            )

        direction = getattr(self.game_engine.player, "direction", "right")
        frames = self.player_frames.get(direction, self.player_frames["right"])
        self.sprite_renderer.render_sprite_frame(
            self.game_engine.player.x,
            self.game_engine.player.y,
            frames,
            self.frame_index,
            self.game_renderer.offset_x,
            self.game_renderer.offset_y
        )

    def _cache_frame_state(self) -> None:
        self._prev_actor_positions = {
            "player": (self.game_engine.player.x, self.game_engine.player.y)
        }
        for name, npc in self.game_engine.npcs.items():
            self._prev_actor_positions[name] = (npc.x, npc.y)
        self._prev_pacgum_cells = {
            (int(round(pacgum.x)), int(round(pacgum.y)))
            for pacgum in self.game_engine.pacgums
        }

    def _covered_cells(self, grid_x: float, grid_y: float) -> set[tuple[int, int]]:
        min_x = int(math.floor(grid_x))
        min_y = int(math.floor(grid_y))
        max_x = int(math.floor(grid_x + 0.9999))
        max_y = int(math.floor(grid_y + 0.9999))
        return {
            (cell_x, cell_y)
            for cell_x in range(min_x, max_x + 1)
            for cell_y in range(min_y, max_y + 1)
        }

    def _is_valid_cell(self, cell_x: int, cell_y: int) -> bool:
        if not self.maze:
            return False
        return 0 <= cell_y < len(self.maze) and 0 <= cell_x < len(self.maze[0])

    def set_player_direction(
            self,
            direction: str
    ) -> None:
        """Set the active player sprite direction.

        Args:
            direction (str): One of "left", "right", "up", or "down".
        """
        if direction in self.player_frames:
            self.game_engine.player.direction = direction

    def _handle_key_press(
            self,
            keycode: int, _: object | None = None
    ) -> None:
        """Handle key press events and forward them to the app callback.

        Args:
            keycode (int): MLX key code for the pressed key.
            _ (object): Unused MLX callback parameter.
        """
        if self._key_press_callback is not None:
            self._key_press_callback(keycode)

    def _handle_key_release(
            self,
            keycode: int, _: object | None = None
    ) -> None:
        """Handle key release events and forward them to the app callback.

        Args:
            keycode (int): MLX key code for the released key.
            _ (object): Unused MLX callback parameter.
        """
        if self._key_release_callback is not None:
            self._key_release_callback(keycode)

    def close(self) -> None:
        """Properly close and release MLX resources."""
        if hasattr(self.mlx, "mlx_loop_end"):
            self.mlx.mlx_loop_end(self.mlx_ptr)
        if hasattr(self.mlx, "mlx_destroy_window"):
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        if hasattr(self.mlx, "mlx_release"):
            self.mlx.mlx_release(self.mlx_ptr)

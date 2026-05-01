from typing import Callable
import math
import time

from mazegenerator.mazegenerator import (
    MazeGenerator,
)
from typing import Any
from mlx import Mlx
from src.app.game.GameEngine import GameEngine
from src.models import UIMode, Color
# from src.models.GameStates import GameStates
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

    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 1000
    CELL_SIZE: int = 40
    FRAME_DELAY_SECONDS: float = 0.15

    def __init__(self,
                 mazegen: MazeGenerator,
                 game_engine: GameEngine,
                 current_input: str,
                 file: str,
                 window_width: int | None = None,
                 window_height: int | None = None,
                 key_press_callback: Callable[[int], None] | None = None,
                 key_release_callback: Callable[[int], None] | None = None,
                 update_callback: Callable[[float], None] | None = None,
                 ui_mode_provider: Callable[[], UIMode] | None = None,
                 ui_mode_setter: Callable[[UIMode], None] | None = None,
                 input_provider: Callable[[], str] | None = None) -> None:
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
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, win_width,
                                               win_height, "Pacman")
        if not self.win_ptr:
            if hasattr(self.mlx, 'mlx_release'):
                self.mlx.mlx_release(self.mlx_ptr)
            raise RuntimeError("Failed to create MLX window")

        self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)

        self.beginning_timestamp: float
        self.mazegen = mazegen
        self.old_maze = mazegen.maze
        self.game_engine = game_engine
        self.current_input: str = "".join([letter for letter in current_input])
        self._level_time = self.game_engine.game_states.time_remaining
        self.win_width = win_width
        self.win_height = win_height
        self._key_press_callback = key_press_callback
        self._key_release_callback = key_release_callback
        self._update_callback = update_callback
        self._ui_mode_provider = ui_mode_provider
        self._ui_mode_setter = ui_mode_setter
        self._input_provider = input_provider
        self._last_ui_mode: UIMode | None = None
        self._needs_full_redraw = True
        self._hud_dirty = True
        self._prev_actor_positions: dict[str, tuple[float, float]] = {}
        self._prev_pacgum_cells: set[tuple[int, int]] = set()
        self._prev_super_pacgum_cells: set[tuple[int, int]] = set()
        self._super_visible = True
        self._gui_screens: dict[UIMode, Any] = {
            UIMode.MAIN_MENU: MenuScreen(file),
            UIMode.PAUSE_MENU: PauseMenuScreen(),
            UIMode.GAME_OVER: GameOverScreen(
                score=game_engine.game_states.score,
                name=current_input),
            UIMode.VICTORY: VictoryScreen(
                score=game_engine.game_states.score,
                name=current_input),
            UIMode.HIGHSCORES: HighscoresScreen(file),
            UIMode.INSTRUCTIONS: InstructionsScreen(),
        }
        self._highscore_file = file
        self._hud = InGameHud(self.game_engine.game_states)
        self.game_renderer = GameRenderer(self.mlx,
                                          self.mlx_ptr,
                                          self.win_ptr,
                                          win_width=win_width,
                                          win_height=win_height,
                                          cell_size=self.CELL_SIZE)
        self.sprite_renderer = SpriteRenderer(self.mlx,
                                              self.mlx_ptr,
                                              self.win_ptr,
                                              cell_size=self.CELL_SIZE)

        self.player_frames = {
            "left":
            self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_left),
            "right":
            self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_right),
            "up":
            self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_up),
            "down":
            self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.mov_down),
            "death":
            self.sprite_renderer.load_sprite_frames(
                self.game_engine.player.sprites.death)
        }
        self.npc_frames: dict[str, list[int]] = {}
        for name, npc in self.game_engine.npcs.items():
            self.npc_frames[name] = self.sprite_renderer.load_sprite_frames(
                npc.sprites.mov_right, recolor=npc.color)
        first_npc = next(iter(self.game_engine.npcs.values()), None)
        self.npc_fear_frames = []
        if first_npc is not None:
            self.npc_fear_frames = self.sprite_renderer.load_sprite_frames(
                first_npc.sprites.fear)

        self.frame_index = 0
        self.last_frame_time = time.monotonic()
        self.last_update_time = self.last_frame_time
        self._last_highscore_refresh = 0.0

        self.is_player_dead = False

        # Register the function that will be called continuously
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render_next_frame, None)
        if self._key_press_callback is not None:
            self.mlx.mlx_hook(self.win_ptr, 2, 1 << 0, self._handle_key_press,
                              None)
        if self._key_release_callback is not None:
            self.mlx.mlx_hook(self.win_ptr, 3, 1 << 1,
                              self._handle_key_release, None)

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
            if screen is None:
                return

            if ui_mode != self._last_ui_mode:
                if ui_mode == UIMode.PAUSE_MENU:
                    self._needs_full_redraw = True
                    self._render_game_frame(update_state=False)
                else:
                    self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
                if screen is not None:
                    screen.render(self.mlx, self.mlx_ptr, self.win_ptr,
                                  self.win_width, self.win_height)
                self._last_ui_mode = ui_mode

            if ui_mode in (UIMode.VICTORY, UIMode.GAME_OVER):
                if self._input_provider is not None:
                    self.current_input = self._input_provider()
                # We already checked screen is not None above
                from .gui import VictoryScreen, GameOverScreen
                if isinstance(screen, (VictoryScreen, GameOverScreen)):
                    screen.name = self.current_input
                self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
                screen.render(self.mlx, self.mlx_ptr, self.win_ptr,
                              self.win_width, self.win_height)

            if ui_mode == UIMode.HIGHSCORES:
                now = time.monotonic()
                if now - self._last_highscore_refresh >= 0.1:
                    self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
                    for _ in range(2):
                        screen.render(self.mlx, self.mlx_ptr, self.win_ptr,
                                      self.win_width, self.win_height)
                    self._last_highscore_refresh = now
            return

        if ui_mode == UIMode.IN_GAME and ui_mode != self._last_ui_mode:
            if self._last_ui_mode == UIMode.MAIN_MENU:
                self.beginning_timestamp = time.monotonic()
            self._needs_full_redraw = True

        self._last_ui_mode = ui_mode
        self._render_game_frame(update_state=True)

    def _render_game_frame(self, update_state: bool) -> None:
        """Render the current game frame and handle incremental updates.

        Args:
            update_state (bool): Whether to advance game state and animation.
        """
        now = time.monotonic()

        if self.mazegen.maze != self.old_maze:
            self._needs_full_redraw = True
            self.old_maze = self.mazegen.maze
            self.beginning_timestamp = time.monotonic()

        self.game_engine.game_states.time_remaining = self._level_time - int(
            now - self.beginning_timestamp
        )
        self.last_update_time = now

        if update_state and self._update_callback is not None:
            dt = now - self.last_update_time
            self._update_callback(dt)

        if self._needs_full_redraw:
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            self.game_renderer.render_maze(self.mazegen.maze)
            self._update_hud_layout()
            self.game_renderer.render_pacgums(self.game_engine.pacgums)
            self.game_renderer.render_super_pacgums(
                self.game_engine.super_pacgums, self._super_visible
            )
            self._render_sprites()
            self._render_hud(force=True)
            self._cache_frame_state()
            self._needs_full_redraw = False
            return

        self._update_hud_layout()
        self._render_incremental()
        if update_state and now - self.last_frame_time >=\
           self.FRAME_DELAY_SECONDS:
            self._super_visible = not self._super_visible
            if self.game_engine.player.direction == "death" and\
               not self.is_player_dead:
                self.frame_index = 0
                self.is_player_dead = True
            if self.game_engine.player.direction == "death" and\
               self.frame_index % 6 == 5:
                time.sleep(0.8)
                self.frame_index = 0
                self.is_player_dead = False
                self.game_engine.rebirth()
            else:
                self.frame_index += 1
            self.last_frame_time = now

        self._render_sprites()
        self._render_hud(force=(int(now * 10 % 10) == 0))
        self._cache_frame_state()

    def _update_hud_layout(self) -> None:
        """Update HUD layout based on current maze dimensions and check game over conditions."""
        maze_width = 0
        maze_height = 0
        if self.mazegen.maze:
            maze_width = len(self.mazegen.maze[0]) * self.CELL_SIZE
            maze_height = len(self.mazegen.maze) * self.CELL_SIZE
        if self._hud.update_layout(self.game_renderer.offset_x,
                                   self.game_renderer.offset_y, maze_width,
                                   maze_height):
            self._hud_dirty = True
        if self._hud.game_states.time_remaining <= 0 or\
           self._hud.game_states.current_lives <= 0:
            if self._ui_mode_setter is not None:
                self._ui_mode_setter(UIMode.GAME_OVER)

    def _render_hud(self, force: bool) -> None:
        """Render the HUD overlay, optionally forcing a redraw.

        Args:
            force (bool): If True, render regardless of dirty state.
        """
        if not force and not self._hud_dirty:
            return
        for rect in self._hud.get_hud_rects(self.win_width, self.win_height):
            x, y, width, height = rect
            self._fill_rect(x, y, width, height, Color.BLACK)
        self._hud.render(self.mlx, self.mlx_ptr, self.win_ptr, self.win_width,
                         self.win_height)
        self._hud_dirty = False

    def _fill_rect(self, x: int, y: int, width: int, height: int,
                   color: int) -> None:
        """Fill a rectangular region with a solid color.

        Args:
            x (int): Left pixel coordinate.
            y (int): Top pixel coordinate.
            width (int): Rectangle width in pixels.
            height (int): Rectangle height in pixels.
            color (int): RGBA color to fill with.
        """
        if width <= 0 or height <= 0:
            return
        pixel_put = self.mlx.mlx_pixel_put
        x_end = x + width
        y_end = y + height
        for py in range(y, y_end):
            for px in range(x, x_end):
                pixel_put(self.mlx_ptr, self.win_ptr, px, py, color)

    def _render_incremental(self) -> None:
        """Perform incremental rendering by redrawing only changed maze cells."""
        current_pacgum_cells = {(int(round(pacgum.x)), int(round(pacgum.y)))
                                for pacgum in self.game_engine.pacgums}
        current_super_cells = {(int(round(spg.x)), int(round(spg.y)))
                               for spg in self.game_engine.super_pacgums}

        removed_cells = (self._prev_pacgum_cells - current_pacgum_cells) | \
                        (self._prev_super_pacgum_cells - current_super_cells)
        if removed_cells:
            self._hud_dirty = True

        cells_to_redraw: set[tuple[int, int]] = set(removed_cells)
        # Always redraw super pacgum cells because of blinking
        cells_to_redraw |= current_super_cells | self._prev_super_pacgum_cells

        for prev_x, prev_y in self._prev_actor_positions.values():
            for cell in self._covered_cells(prev_x, prev_y):
                cells_to_redraw.add(cell)

        for cell_x, cell_y in cells_to_redraw:
            if not self._is_valid_cell(cell_x, cell_y):
                continue
            has_pacgum = (cell_x, cell_y) in current_pacgum_cells
            has_super = (cell_x, cell_y) in current_super_cells
            self.game_renderer.redraw_cell(self.mazegen.maze, cell_x, cell_y,
                                           has_pacgum, has_super,
                                           self._super_visible)

        added_pacgums = current_pacgum_cells - self._prev_pacgum_cells
        for cell_x, cell_y in added_pacgums - cells_to_redraw:
            if not self._is_valid_cell(cell_x, cell_y):
                continue
            self.game_renderer.draw_pacgum_at(cell_x, cell_y)

    def _render_sprites(self) -> None:
        """Render all NPC and player sprites at their current positions."""
        for name, npc in self.game_engine.npcs.items():
            frames = self.npc_frames.get(name, [])
            if npc.is_fleeing:
                frames = self.npc_fear_frames

            # Hide ghost if it's respawning
            if time.monotonic() < npc.respawn_time:
                continue

            self.sprite_renderer.render_sprite_frame(
                npc.x, npc.y, frames, self.frame_index,
                self.game_renderer.offset_x, self.game_renderer.offset_y)

        direction = getattr(self.game_engine.player, "direction", "right")
        frames = self.player_frames.get(direction, self.player_frames["right"])
        self.sprite_renderer.render_sprite_frame(self.game_engine.player.x,
                                                 self.game_engine.player.y,
                                                 frames, self.frame_index,
                                                 self.game_renderer.offset_x,
                                                 self.game_renderer.offset_y)

    def _cache_frame_state(self) -> None:
        """Cache current actor positions and pacgum cells for incremental rendering."""
        self._prev_actor_positions = {
            "player": (self.game_engine.player.x, self.game_engine.player.y)
        }
        for name, npc in self.game_engine.npcs.items():
            self._prev_actor_positions[name] = (npc.x, npc.y)
        self._prev_pacgum_cells = {(int(round(pacgum.x)), int(round(pacgum.y)))
                                   for pacgum in self.game_engine.pacgums}
        self._prev_super_pacgum_cells = \
            {(int(round(spg.x)), int(round(spg.y)))
             for spg in self.game_engine.super_pacgums}

    def _covered_cells(self, grid_x: float,
                       grid_y: float) -> set[tuple[int, int]]:
        """Get the set of maze cells covered by an actor at grid coordinates.

        Args:
            grid_x (float): Actor x position in grid coordinates.
            grid_y (float): Actor y position in grid coordinates.

        Returns:
            set[tuple[int, int]]: Set of (cell_x, cell_y) tuples.
        """
        min_x = int(math.floor(grid_x))
        min_y = int(math.floor(grid_y))
        max_x = int(math.floor(grid_x + 0.9999))
        max_y = int(math.floor(grid_y + 0.9999))
        return {(cell_x, cell_y)
                for cell_x in range(min_x, max_x + 1)
                for cell_y in range(min_y, max_y + 1)}

    def _is_valid_cell(self, cell_x: int, cell_y: int) -> bool:
        """Check if a cell coordinate is within the maze bounds.

        Args:
            cell_x (int): Cell x-coordinate.
            cell_y (int): Cell y-coordinate.

        Returns:
            bool: True if the cell is within bounds.
        """
        if not self.mazegen.maze:
            return False
        return 0 <= cell_y < len(self.mazegen.maze) and \
            0 <= cell_x < len(self.mazegen.maze[0])

    def set_player_direction(self, direction: str) -> None:
        """Set the active player sprite direction.

        Args:
            direction (str): One of "left", "right", "up", or "down".
        """
        if direction in self.player_frames:
            self.game_engine.player.direction = direction

    def _handle_key_press(self, keycode: int, _: object | None = None) -> None:
        """Handle key press events and forward them to the app callback.

        Args:
            keycode (int): MLX key code for the pressed key.
            _ (object): Unused MLX callback parameter.
        """
        if self._key_press_callback is not None:
            self._key_press_callback(keycode)

        # Trigger immediate redraw for GameOver and Victory screens
        ui_mode = None
        if self._ui_mode_provider is not None:
            ui_mode = self._ui_mode_provider()
        if ui_mode in (UIMode.VICTORY, UIMode.GAME_OVER):
            self.render_next_frame(None)

    def _handle_key_release(self,
                            keycode: int,
                            _: object | None = None) -> None:
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

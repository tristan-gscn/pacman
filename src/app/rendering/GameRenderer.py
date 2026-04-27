from functools import partial
from pathlib import Path
from mlx import Mlx
from .MazeRenderer import MazeRenderer


class GameRenderer:
    """Renderer responsible for drawing game entities (maze, etc.)."""

    def __init__(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int,
        cell_size: int
    ) -> None:
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.win_width = win_width
        self.win_height = win_height
        self.cell_size = cell_size
        self.offset_x = 0
        self.offset_y = 0
        self._sprite_cache: dict[tuple[str, int | None], list[int]] = {}

    def render_maze(self, maze: list[list[int]]) -> None:
        maze_width = len(maze[0]) * self.cell_size
        maze_height = len(maze) * self.cell_size
        self.offset_x = max((self.win_width - maze_width) // 2, 0)
        self.offset_y = max((self.win_height - maze_height) // 2, 0)

        pixel_put = partial(self.mlx.mlx_pixel_put, self.mlx_ptr, self.win_ptr)
        MazeRenderer().render_maze(
            maze,
            pixel_put,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            cell_size=self.cell_size
        )

    def render_actor(self, grid_x: int, grid_y: int, color: int) -> None:
        pixel_put = partial(self.mlx.mlx_pixel_put, self.mlx_ptr, self.win_ptr)
        padding = max(self.cell_size // 6, 2)
        start_x = grid_x * self.cell_size + self.offset_x + padding
        start_y = grid_y * self.cell_size + self.offset_y + padding
        end_x = (grid_x + 1) * self.cell_size + self.offset_x - padding
        end_y = (grid_y + 1) * self.cell_size + self.offset_y - padding

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                pixel_put(x, y, color)

    def render_sprite_frame(
        self,
        grid_x: int,
        grid_y: int,
        frames: list[int],
        frame_index: int
    ) -> None:
        if not frames:
            return
        img_ptr = frames[frame_index % len(frames)]
        px = grid_x * self.cell_size + self.offset_x
        py = grid_y * self.cell_size + self.offset_y
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img_ptr, px, py)

    def load_sprite_frames(
        self,
        sprite_path: str,
        recolor: int | None = None
    ) -> list[int]:
        cache_key = (sprite_path, recolor)
        cached = self._sprite_cache.get(cache_key)
        if cached is not None:
            return cached

        full_path = self._resolve_sprite_path(sprite_path)
        img_ptr, width, height = self.mlx.mlx_png_file_to_image(
            self.mlx_ptr,
            str(full_path)
        )
        if not img_ptr:
            raise RuntimeError(f"Failed to load sprite: {full_path}")

        data_view, bpp, size_line, endian = self.mlx.mlx_get_data_addr(img_ptr)
        bytes_per_pixel = bpp // 8
        if bytes_per_pixel < 3:
            raise RuntimeError("Unsupported sprite pixel format")

        frame_size = height
        if frame_size <= 0 or width % frame_size != 0:
            raise RuntimeError("Invalid sprite sheet size")

        frame_count = width // frame_size
        frames: list[int] = []

        for frame_index in range(frame_count):
            frame_img = self.mlx.mlx_new_image(self.mlx_ptr, frame_size, frame_size)
            frame_view, frame_bpp, frame_line, frame_endian = self.mlx.mlx_get_data_addr(
                frame_img
            )
            if frame_bpp != bpp or frame_endian != endian:
                raise RuntimeError("Unexpected frame buffer format")

            if recolor is None:
                self._copy_frame_block(
                    data_view,
                    size_line,
                    frame_view,
                    frame_line,
                    frame_index,
                    frame_size,
                    bytes_per_pixel
                )
            else:
                self._copy_frame_recolor(
                    data_view,
                    size_line,
                    frame_view,
                    frame_line,
                    frame_index,
                    frame_size,
                    bytes_per_pixel,
                    endian,
                    recolor
                )

            frames.append(frame_img)

        self.mlx.mlx_destroy_image(self.mlx_ptr, img_ptr)
        self._sprite_cache[cache_key] = frames
        return frames

    def _resolve_sprite_path(self, sprite_path: str) -> Path:
        base_dir = Path(__file__).resolve().parents[3] / "assets"
        candidate = base_dir / sprite_path
        if candidate.exists():
            return candidate
        if sprite_path.startswith("npc/"):
            fallback = base_dir / "ghost" / sprite_path[len("npc/"):]
            if fallback.exists():
                return fallback
        return candidate

    def _copy_frame_block(
        self,
        src_view: memoryview,
        src_line: int,
        dst_view: memoryview,
        dst_line: int,
        frame_index: int,
        frame_size: int,
        bytes_per_pixel: int
    ) -> None:
        frame_offset = frame_index * frame_size * bytes_per_pixel
        row_bytes = frame_size * bytes_per_pixel
        for y in range(frame_size):
            src_start = y * src_line + frame_offset
            dst_start = y * dst_line
            dst_view[dst_start:dst_start + row_bytes] = src_view[
                src_start:src_start + row_bytes
            ]

    def _copy_frame_recolor(
        self,
        src_view: memoryview,
        src_line: int,
        dst_view: memoryview,
        dst_line: int,
        frame_index: int,
        frame_size: int,
        bytes_per_pixel: int,
        endian: int,
        new_color: int
    ) -> None:
        frame_offset = frame_index * frame_size * bytes_per_pixel
        new_bytes = self._color_to_bytes(new_color, endian)

        for y in range(frame_size):
            src_row = y * src_line + frame_offset
            dst_row = y * dst_line
            for x in range(frame_size):
                src_pos = src_row + x * bytes_per_pixel
                dst_pos = dst_row + x * bytes_per_pixel
                pixel = src_view[src_pos:src_pos + bytes_per_pixel]
                if self._is_red_tint(pixel, endian):
                    dst_view[dst_pos:dst_pos + bytes_per_pixel] = new_bytes
                else:
                    dst_view[dst_pos:dst_pos + bytes_per_pixel] = pixel

    def _color_to_bytes(self, color: int, endian: int) -> bytes:
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        a = (color >> 24) & 0xFF
        if endian == 0:
            return bytes((b, g, r, a))
        return bytes((r, g, b, a))

    def _is_red_tint(self, pixel: memoryview, endian: int) -> bool:
        if endian == 0:
            b, g, r = pixel[0], pixel[1], pixel[2]
        else:
            r, g, b = pixel[0], pixel[1], pixel[2]
        return r >= 160 and (r - g) >= 20 and (r - b) >= 20

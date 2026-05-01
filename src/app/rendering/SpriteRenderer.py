from pathlib import Path
from mlx import Mlx


class SpriteRenderer:
    def __init__(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        cell_size: int
    ) -> None:
        """Initialize sprite rendering and caching.

        Args:
            mlx (Mlx): MLX wrapper instance.
            mlx_ptr (int): Pointer to MLX context.
            win_ptr (int): Pointer to the MLX window.
            cell_size (int): Size of a maze cell in pixels.
        """
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.cell_size = cell_size
        self._sprite_cache: dict[tuple[str, int | None], list[int]] = {}

    def render_sprite_frame(
        self,
        grid_x: float,
        grid_y: float,
        frames: list[int],
        frame_index: int,
        offset_x: int,
        offset_y: int
    ) -> None:
        """Render a specific frame from a sprite sheet at grid coordinates.

        Args:
            grid_x (float): Sprite x position in grid coordinates.
            grid_y (float): Sprite y position in grid coordinates.
            frames (list[int]): MLX image pointers for each frame.
            frame_index (int): Index of the frame to draw.
            offset_x (int): Horizontal offset to apply when rendering.
            offset_y (int): Vertical offset to apply when rendering.
        """
        if not frames:
            return
        img_ptr = frames[frame_index % len(frames)]
        px = int(round(grid_x * self.cell_size + offset_x))
        py = int(round(grid_y * self.cell_size + offset_y))
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            img_ptr,
            px,
            py
        )

    def load_sprite_frames(
        self,
        sprite_path: str,
        recolor: int | None = None
    ) -> list[int]:
        """Load a PNG sprite sheet and split it into frame images.

        Args:
            sprite_path (str): Relative sprite path inside the assets folder.
            recolor (int | None): Optional RGBA color to replace red pixels.

        Returns:
            list[int]: MLX image pointers for each frame.
        """
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
            frame_img = self.mlx.mlx_new_image(
                self.mlx_ptr,
                frame_size,
                frame_size
            )
            frame_view, frame_bpp, frame_line, frame_endian = (
                self.mlx.mlx_get_data_addr(
                    frame_img
                )
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
        """Resolve a sprite path within the assets directory.

        Args:
            sprite_path (str): Relative sprite path.

        Returns:
            Path: Absolute path to the sprite file.
        """
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
        """Copy a single frame from the source sheet to a frame buffer.

        Args:
            src_view (memoryview): Source image buffer.
            src_line (int): Source bytes per row.
            dst_view (memoryview): Destination image buffer.
            dst_line (int): Destination bytes per row.
            frame_index (int): Index of the frame to copy.
            frame_size (int): Width/height of a frame in pixels.
            bytes_per_pixel (int): Number of bytes per pixel.
        """
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
        """Copy a frame and replace red-tinted pixels with a target color.

        Args:
            src_view (memoryview): Source image buffer.
            src_line (int): Source bytes per row.
            dst_view (memoryview): Destination image buffer.
            dst_line (int): Destination bytes per row.
            frame_index (int): Index of the frame to copy.
            frame_size (int): Width/height of a frame in pixels.
            bytes_per_pixel (int): Number of bytes per pixel.
            endian (int): Endianness flag from MLX.
            new_color (int): RGBA color to apply to red pixels.
        """
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
        """Convert an RGBA integer to byte order expected by MLX.

        Args:
            color (int): 32-bit RGBA color.
            endian (int): Endianness flag from MLX.

        Returns:
            bytes: Byte sequence representing the color.
        """
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        a = (color >> 24) & 0xFF
        if endian == 0:
            return bytes((b, g, r, a))
        return bytes((r, g, b, a))

    def _is_red_tint(self, pixel: memoryview, endian: int) -> bool:
        """Check whether a pixel is a red tint suitable for recoloring.

        Args:
            pixel (memoryview): Pixel bytes.
            endian (int): Endianness flag from MLX.

        Returns:
            bool: True if the pixel is a red tint.
        """
        if endian == 0:
            b, g, r = pixel[0], pixel[1], pixel[2]
        else:
            r, g, b = pixel[0], pixel[1], pixel[2]
        return r >= 160 and (r - g) >= 20 and (r - b) >= 20

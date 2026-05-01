from pathlib import Path
import sys


def get_resource_path(relative_path: str) -> Path:
    """Resolve a resource path for dev and PyInstaller builds.

    Args:
        relative_path (str): Relative path from the project root
            (e.g., 'config.json', 'assets/ghost/fear.png').

    Returns:
        Path: Absolute path to the resource.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).resolve().parents[2]
    return base_dir / relative_path

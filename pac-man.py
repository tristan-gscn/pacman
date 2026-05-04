#!/usr/bin/env python3
"""Entry point script for the Pacman game.

Usage:
    python3 pac-man.py config.json
"""

import sys


def _get_bundled_config() -> str:
    """Return the path to the bundled config.json."""
    from src.models.resources import get_resource_path
    return str(get_resource_path("config.json"))


if __name__ == '__main__':
    is_frozen = getattr(sys, "frozen", False)

    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    elif is_frozen:
        config_path = _get_bundled_config()
    else:
        print("Usage: pacman <config.json>")
        sys.exit(1)

    if not config_path.endswith(".json"):
        print("Error: configuration file must be a .json file")
        sys.exit(1)

    try:
        from src.app.App import App
        app = App(config_path=config_path)
        app.run()
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

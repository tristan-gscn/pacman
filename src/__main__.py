import sys
from src.app.App import App


def main() -> None:
    """Entry point that initializes and runs the Pacman application."""
    if len(sys.argv) != 2:
        print("Usage: pacman <config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    if not config_path.endswith(".json"):
        print("Error: configuration file must be a .json file")
        sys.exit(1)

    try:
        app = App(config_path=config_path)
        app.run()
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

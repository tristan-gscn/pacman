from mazegenerator.mazegenerator import MazeGenerator
from src.parsing import ConfigParser
from src.app.rendering import GlobalRenderer


def main() -> None:

    try:
        print(ConfigParser().parse('truc.json'))
    except Exception as e:
        print(f"{type(e).__name__} error occured while parsing: {e}")

    try:
        mazegen = MazeGenerator()
        mazegen.generate()
        GlobalRenderer(mazegen.maze)
    except RuntimeError as e:
        print(f"Renderer initialization skipped: {e}")


if __name__ == '__main__':
    main()

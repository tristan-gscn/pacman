from mazegenerator.mazegenerator import (  # type: ignore[import-untyped]
    MazeGenerator,
)
from src.parsing import ConfigParser
from src.app.game.GameEngine import GameEngine
from src.app.rendering import GlobalRenderer


def main() -> None:

    try:
        print(ConfigParser().parse('truc.json'))
    except Exception as e:
        print(f"{type(e).__name__} error occured while parsing: {e}")

    try:
        mazegen = MazeGenerator()
        mazegen.generate()
        game_engine = GameEngine()
        GlobalRenderer(mazegen.maze, game_engine)
    except RuntimeError as e:
        print(f"Renderer initialization skipped: {e}")


if __name__ == '__main__':
    main()

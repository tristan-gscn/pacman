from enum import Enum, auto


class UIMode(Enum):
    MAIN_MENU = auto()
    IN_GAME = auto()
    PAUSE_MENU = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()

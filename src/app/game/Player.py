from .Actor import Actor
from src.models import PlayerSprites


class Player(Actor):
    """The player character (Pacman) controlled by the user."""

    def __init__(self) -> None:
        """Initialize the player with default direction and sprites."""
        super().__init__()
        self.direction = "right"
        self.sprites = PlayerSprites(
            death="pacman/death.png",
            mov_left="pacman/mov_left.png",
            mov_right="pacman/mov_right.png",
            mov_up="pacman/mov_up.png",
            mov_down="pacman/mov_down.png",
            mov_left_god="pacman/mov_left_god.png",
            mov_right_god="pacman/mov_right_god.png",
            mov_up_god="pacman/mov_up_god.png",
            mov_down_god="pacman/mov_down_god.png"
        )

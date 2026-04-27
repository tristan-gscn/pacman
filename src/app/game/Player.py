from app.game.Actor import Actor
from models import PlayerSprites


class Player(Actor):
    def __init__(self):
        super().__init__()
        self.sprites = PlayerSprites(
            death="pacman/death.png",
            mov_left="pacman/mov_left.png",
            mov_right="pacman/mov_right.png",
            mov_top="pacman/mov_up.png",
            mov_bottom="pacman/mov_down.png",
        )

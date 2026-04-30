from .Actor import Actor


class SuperPacGum(Actor):
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        super().__init__(x=x, y=y)

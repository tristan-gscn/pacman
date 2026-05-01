from .Actor import Actor


class SuperPacGum(Actor):
    """A power pellet that enables the player to eat ghosts."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Initialize a super pacgum at the given coordinates.

        Args:
            x (float): X-coordinate in the maze. Defaults to 0.0.
            y (float): Y-coordinate in the maze. Defaults to 0.0.
        """
        super().__init__(x=x, y=y)

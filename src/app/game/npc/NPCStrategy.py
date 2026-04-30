from abc import ABC


class NPCStrategy(ABC):
    path: list[tuple[int, int]] = []

    def act(self) -> None:
        pass

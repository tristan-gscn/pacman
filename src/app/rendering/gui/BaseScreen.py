from abc import ABC, abstractmethod
from mlx import Mlx


class BaseScreen(ABC):
    @abstractmethod
    def render(
        self,
        mlx: Mlx,
        mlx_ptr: int,
        win_ptr: int,
        win_width: int,
        win_height: int
    ) -> None:
        pass

from pydantic import BaseModel


class PlayerSprites(BaseModel):
    death: str
    mov_left: str
    mov_right: str
    mov_up: str
    mov_down: str
    mov_left_god: str
    mov_right_god: str
    mov_up_god: str
    mov_down_god: str

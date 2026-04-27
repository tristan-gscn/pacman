from pydantic import BaseModel


class PlayerSprites(BaseModel):
    death: str
    mov_left: str
    mov_right: str
    mov_top: str
    mov_bottom: str

from pydantic import BaseModel


class NPCSprites(BaseModel):
    fear: str
    mov_left: str
    mov_right: str
    mov_up: str
    mov_down: str

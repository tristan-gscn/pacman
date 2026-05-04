from pydantic import BaseModel, Field


class GameStates(BaseModel):
    score: int = Field(0, ge=0)
    level: int = Field(1, ge=1)
    time_remaining: int = Field(90, ge=1)
    max_lives: int = Field(3, ge=1)
    current_lives: int = Field(3, ge=0)
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int

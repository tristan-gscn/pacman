from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional


class Configuration(BaseModel):

    model_config = ConfigDict(extra='forbid')
    highscore_filename: str
    width: int = Field(..., gt=0, le=30)
    height: int = Field(..., gt=0, le=30)
    lives: int = Field(3, ge=1)
    pacgum: float = Field(..., ge=0, le=1.0)
    points_per_pacgum: int = Field(..., ge=0)
    points_per_super_pacgum: int = Field(..., ge=0)
    points_per_ghost: int = Field(..., ge=0)
    seed: Optional[str | int] = None
    level_max_time: int = Field(..., ge=1)

    @field_validator('highscore_filename', mode='after')
    @classmethod
    def check_extension(cls, value: str) -> str:
        if not value.endswith('.json'):
            raise ValueError('Your highscore_filename must end with .json')
        return value

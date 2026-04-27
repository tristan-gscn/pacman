from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional


class Configuration(BaseModel):

    model_config = ConfigDict(extra='forbid')
    highscore_filename: str
    width: int = Field(..., gt=0, le=100)
    height: int = Field(..., gt=0, le=100)
    lives: int = Field(3, ge=1)
    pacgum: int = Field(..., ge=4)
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

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# Auth

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user_id: int


# Pet

class PetResponse(BaseModel):
    id: int
    name: str
    level: int
    current_exp: float
    required_exp: float
    hunger: float
    mood: str
    image: str
    streak_count: int = 0
    streak_active: bool = False
    streak_multiplier: float = 1.0

    model_config = {"from_attributes": True}


class PetNameUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


# Task

def _validate_deadline(value: str) -> str:
    """Check that the string is a valid date in DD.MM.YYYY format."""
    try:
        datetime.strptime(value, "%d.%m.%Y")
    except ValueError:
        raise ValueError("Дедлайн должен быть в формате ДД.ММ.ГГГГ")
    return value


class TaskCreate(BaseModel):
    title: str = Field(max_length=200)
    category: str = Field(max_length=50)
    deadline: str

    @field_validator("deadline")
    @classmethod
    def check_deadline(cls, value: str) -> str:
        return _validate_deadline(value)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = Field(default=None, max_length=50)
    deadline: Optional[str] = None

    @field_validator("deadline")
    @classmethod
    def check_deadline(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_deadline(value)


class TaskResponse(BaseModel):
    id: int
    title: str
    category: str
    deadline: str
    difficulty: Optional[str] = None
    exp_reward: Optional[float] = None
    hunger_reward: Optional[float] = None
    is_activated: bool
    is_completed: bool
    is_overdue: bool

    model_config = {"from_attributes": True}


class TaskActivateResponse(BaseModel):
    activated_count: int
    tasks: list[TaskResponse]
    message: Optional[str] = None


class TaskCompleteResponse(BaseModel):
    exp_gained: float
    hunger_gained: float
    streak_active: bool
    streak_multiplier: float
    level_up: bool
    pet: PetResponse

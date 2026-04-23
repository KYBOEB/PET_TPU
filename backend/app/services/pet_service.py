from datetime import datetime
from math import floor

from sqlalchemy.orm import Session

from app.models import Pet

HUNGER_MAX = 100
HUNGER_DECAY_HOURS = 48
HUNGER_RATE = HUNGER_MAX / HUNGER_DECAY_HOURS
EXP_PENALTY_PER_HOUR = 10


def recompute_hunger(pet: Pet, db: Session) -> None:
    now = datetime.utcnow()
    elapsed_hours = (now - pet.last_hunger_update).total_seconds() / 3600
    pet.hunger = max(0, pet.hunger - elapsed_hours * HUNGER_RATE)
    pet.last_hunger_update = now

    if pet.hunger == 0 and pet.hunger_zero_since is None:
        pet.hunger_zero_since = now
    elif pet.hunger > 0:
        pet.hunger_zero_since = None

    db.commit()


def apply_exp_penalty(pet: Pet, db: Session) -> None:
    if pet.hunger_zero_since is None:
        return

    now = datetime.utcnow()
    penalty_hours = (now - pet.hunger_zero_since).total_seconds() / 3600
    penalty = floor(penalty_hours) * EXP_PENALTY_PER_HOUR
    pet.current_exp = max(0, pet.current_exp - penalty)

    db.commit()


def get_mood(hunger: float) -> str:
    if hunger > 80:
        return "happy"
    if hunger >= 21:
        return "neutral"
    return "sad"


def get_required_exp(level: int) -> float:
    return 200 * (1.5 ** level)


def get_pet_image(level: int, mood: str) -> str:
    return f"pet_level{level}_{mood}.png"

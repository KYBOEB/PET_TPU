from datetime import date, datetime, timedelta
from math import floor

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Pet, Task
from app.services.pet_service import get_mood, get_pet_image, get_required_exp


def check_streak(user_id: int, db: Session) -> tuple[bool, float]:
    since = datetime.utcnow() - timedelta(hours=24)
    count = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.is_completed == True,
            Task.completed_at >= since,
        )
        .count()
    )
    if count > 3:
        return (True, 1.25)
    return (False, 1.0)


def complete_task(task_id: int, user_id: int, db: Session) -> dict:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if not task.is_activated:
        raise HTTPException(status_code=400, detail="Задача не активирована")
    if task.is_completed:
        raise HTTPException(status_code=400, detail="Задача уже выполнена")

    pet = db.query(Pet).filter(Pet.user_id == user_id).first()

    streak_active, multiplier = check_streak(user_id, db)

    final_exp = floor(task.exp_reward * multiplier)
    final_hunger = floor(task.hunger_reward * multiplier)

    pet.hunger = min(100, pet.hunger + final_hunger)
    pet.current_exp += final_exp

    if pet.hunger > 0:
        pet.hunger_zero_since = None

    required = get_required_exp(pet.level)
    level_up = False
    if pet.current_exp >= required and pet.level < 3:
        pet.level += 1
        pet.current_exp = 0
        level_up = True

    task.is_completed = True
    task.completed_at = datetime.utcnow()

    db.commit()

    mood = get_mood(pet.hunger)

    return {
        "exp_gained": final_exp,
        "hunger_gained": final_hunger,
        "streak_active": streak_active,
        "streak_multiplier": multiplier,
        "level_up": level_up,
        "pet": {
            "id": pet.id,
            "name": pet.name,
            "level": pet.level,
            "current_exp": pet.current_exp,
            "required_exp": get_required_exp(pet.level),
            "hunger": pet.hunger,
            "mood": mood,
            "image": get_pet_image(pet.level, mood),
        },
    }


def check_overdue_tasks(user_id: int, db: Session) -> int:
    today = date.today()
    overdue = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.is_activated == True,
            Task.is_completed == False,
            Task.is_overdue == False,
            Task.deadline < today,
        )
        .all()
    )

    if not overdue:
        return 0

    pet = db.query(Pet).filter(Pet.user_id == user_id).first()

    for task in overdue:
        pet.current_exp = max(0, pet.current_exp - task.exp_reward)
        pet.hunger = max(0, pet.hunger - task.hunger_reward)

        if pet.hunger == 0 and pet.hunger_zero_since is None:
            pet.hunger_zero_since = datetime.utcnow()

        task.is_overdue = True

    db.commit()

    return len(overdue)

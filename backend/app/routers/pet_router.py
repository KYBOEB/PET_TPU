from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Pet, Task
from app.schemas import PetNameUpdate, PetResponse
from app.services.pet_service import (
    apply_exp_penalty,
    get_mood,
    get_pet_image,
    get_required_exp,
    recompute_hunger,
)
from app.services.task_service import check_overdue_tasks

router = APIRouter(prefix="/api/pet", tags=["pet"])


@router.get("", response_model=PetResponse)
def get_pet(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pet = db.query(Pet).filter(Pet.user_id == user_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден")

    check_overdue_tasks(user_id, db)
    recompute_hunger(pet, db)
    apply_exp_penalty(pet, db)

    mood = get_mood(pet.hunger)
    required_exp = get_required_exp(pet.level)

    # Count tasks completed in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    completed_today = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_completed == True,
        Task.completed_at != None,
        Task.completed_at >= twenty_four_hours_ago,
    ).count()

    streak_active = completed_today > 3
    streak_multiplier = 1.25 if streak_active else 1.0

    return PetResponse(
        id=pet.id,
        name=pet.name,
        level=pet.level,
        current_exp=pet.current_exp,
        required_exp=required_exp,
        hunger=pet.hunger,
        mood=mood,
        image=get_pet_image(pet.level, mood),
        streak_count=completed_today,
        streak_active=streak_active,
        streak_multiplier=streak_multiplier,
    )


@router.put("/name")
def update_pet_name(
    body: PetNameUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pet = db.query(Pet).filter(Pet.user_id == user_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден")

    pet.name = body.name
    db.commit()

    return {"name": pet.name}

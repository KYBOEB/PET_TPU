from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Pet, Task
from app.schemas import TaskActivateResponse, TaskCompleteResponse, TaskCreate, TaskResponse, TaskUpdate
from app.services.llm_service import evaluate_tasks
from app.services.pet_service import apply_exp_penalty, recompute_hunger
from app.services.task_service import check_overdue_tasks, complete_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _format_deadline(d) -> str:
    return d.strftime("%d.%m.%Y")


def _task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        category=task.category,
        deadline=_format_deadline(task.deadline),
        difficulty=task.difficulty,
        exp_reward=task.exp_reward,
        hunger_reward=task.hunger_reward,
        is_activated=task.is_activated,
        is_completed=task.is_completed,
        is_overdue=task.is_overdue,
    )


@router.get("", response_model=dict)
def get_tasks(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_overdue_tasks(user_id, db)

    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.is_overdue == False,
        )
        .order_by(Task.deadline)
        .all()
    )

    return {"tasks": [_task_to_response(t) for t in tasks]}


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deadline_date = datetime.strptime(body.deadline, "%d.%m.%Y").date()

    task = Task(
        user_id=user_id,
        title=body.title,
        category=body.category,
        deadline=deadline_date,
        is_activated=False,
        is_completed=False,
        is_overdue=False,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return _task_to_response(task)


@router.post("/activate", response_model=TaskActivateResponse)
async def activate_tasks(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.is_activated == False,
            Task.is_completed == False,
            Task.is_overdue == False,
        )
        .all()
    )

    if not tasks:
        return TaskActivateResponse(
            activated_count=0,
            tasks=[],
            message="Нет новых задач для активации",
        )

    titles = [t.title for t in tasks]
    results = await evaluate_tasks(titles)

    results_by_title = {r["title"]: r for r in results}

    for task in tasks:
        r = results_by_title.get(task.title, {})
        task.difficulty = r.get("difficulty", "medium")
        task.exp_reward = r.get("exp_reward", 25)
        task.hunger_reward = r.get("hunger_reward", 20)
        task.is_activated = True

    db.commit()

    return TaskActivateResponse(
        activated_count=len(tasks),
        tasks=[_task_to_response(t) for t in tasks],
    )


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    body: TaskUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if body.title is not None:
        task.title = body.title
    if body.category is not None:
        task.category = body.category
    if body.deadline is not None:
        task.deadline = datetime.strptime(body.deadline, "%d.%m.%Y").date()

    if task.is_activated:
        task.difficulty = None
        task.exp_reward = None
        task.hunger_reward = None
        task.is_activated = False

    db.commit()
    db.refresh(task)

    return _task_to_response(task)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    db.delete(task)
    db.commit()

    return {"detail": "Задача удалена"}


@router.post("/{task_id}/complete", response_model=TaskCompleteResponse)
def complete_task_endpoint(
    task_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pet = db.query(Pet).filter(Pet.user_id == user_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден")
    recompute_hunger(pet, db)
    apply_exp_penalty(pet, db)

    result = complete_task(task_id, user_id, db)

    return TaskCompleteResponse(**result)

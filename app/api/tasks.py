from typing import Annotated, Optional, List

from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_db
from ..models.user import User
from ..models.task import Task, TaskStatus, Priority, Category
from ..schemas.tasks import TaskCreate, TaskResponse, TaskUpdate
from .deps import get_current_user, get_user, get_admin

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    task_data: TaskCreate,
):
    existing_task = (
        db.query(Task)
        .filter(Task.name == task_data.name, Task.user_id == user.user_id)
        .first()
    )
    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task already exists."
        )
    existing_task_category = (
        db.query(Category)
        .filter(Category.category_id == task_data.category_id)
        .first()
    )
    if not existing_task_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist."
        )
    new_task = Task(
        name=task_data.name,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        category_id=task_data.category_id,
        user_id=user.user_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


@router.get("/", response_model=List[TaskResponse])
def get_task_list(
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    status: Optional[TaskStatus] = None,
):
    query = db.query(Task).filter(Task.user_id == user.user_id)
    if status is not None:
        query = query.filter(Task.status == status)

    tasks = query.all()
    return tasks


@router.get("/{pk}", response_model=TaskResponse)
def get_one_task(
    pk: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    task = db.query(Task).filter(Task.task_id == pk, Task.user_id == user.user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found."
        )

    return task


@router.put("/{pk}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def update_task(
    pk: int,
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    task_data: TaskUpdate,
):
    task = db.query(Task).filter(Task.task_id == pk, Task.user_id == user.user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found."
        )

    if task.name:
        existing_task = (
            db.query(Task)
            .filter(Task.name == task_data.name, Task.user_id == user.user_id)
            .first()
        )
        if existing_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Task with this name already exists."
            )
        task.name = task_data.name

    task.description = task_data.description if task_data.description else task.description
    task.status = task_data.status if task_data.status else task.status
    task.due_date = task_data.due_date if task_data.due_date else task.due_date
    if task_data.category_id:
        existing_task_category = (
            db.query(Category)
            .filter(Category.category_id == task_data.category_id)
            .first()
        )
        if not existing_task_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist."
            )
        task.category_id = task_data.category_id

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    pk: int,
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
):
    task = db.query(Task).filter(Task.task_id == pk, Task.user_id == user.user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found."
        )

    db.delete(task)
    db.commit()

    return {"detail": "Task deleted successfully."}

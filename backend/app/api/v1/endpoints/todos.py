from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.core.dependencies import SessionDep
from app.models.todo import Todo, TodoCreate, TodoPublic, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[TodoPublic])
def read_todos(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    todos = session.exec(select(Todo).offset(offset).limit(limit)).all()
    return todos


@router.post("/", response_model=TodoPublic, status_code=201)
def create_todo(todo: TodoCreate, session: SessionDep):
    db_todo = Todo.model_validate(todo)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.get("/{todo_id}", response_model=TodoPublic)
def read_todo(todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoPublic)
def update_todo(todo_id: int, todo: TodoUpdate, session: SessionDep):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_data = todo.model_dump(exclude_unset=True)
    db_todo.sqlmodel_update(todo_data)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return None

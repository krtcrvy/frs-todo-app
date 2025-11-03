from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.core.dependencies import CurrentUser, SessionDep
from app.models.todo import Todo, TodoCreate, TodoPublic, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[TodoPublic])
def read_todos(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Get all todos for the current authenticated user."""
    statement = (
        select(Todo).where(Todo.user_id == current_user.id).offset(offset).limit(limit)
    )
    todos = session.exec(statement).all()
    return todos


@router.post("/", response_model=TodoPublic, status_code=201)
def create_todo(todo: TodoCreate, session: SessionDep, current_user: CurrentUser):
    """Create a new todo for the current authenticated user."""
    db_todo = Todo.model_validate(todo, update={"user_id": current_user.id})
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.get("/{todo_id}", response_model=TodoPublic)
def read_todo(todo_id: int, session: SessionDep, current_user: CurrentUser):
    """Get a specific todo by ID. Only returns todos owned by the current user."""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this todo"
        )
    return todo


@router.patch("/{todo_id}", response_model=TodoPublic)
def update_todo(
    todo_id: int, todo: TodoUpdate, session: SessionDep, current_user: CurrentUser
):
    """Update a todo. Only allows updating todos owned by the current user."""
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this todo"
        )
    todo_data = todo.model_dump(exclude_unset=True)
    db_todo.sqlmodel_update(todo_data)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: SessionDep, current_user: CurrentUser):
    """Delete a todo. Only allows deleting todos owned by the current user."""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this todo"
        )
    session.delete(todo)
    session.commit()
    return None

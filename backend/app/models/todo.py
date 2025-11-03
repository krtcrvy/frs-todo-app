from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class TodoBase(SQLModel):
    title: str = Field(index=True, min_length=3, max_length=50)
    description: str | None = Field(default=None, max_length=100)
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = Field(default=False)


class Todo(TodoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user: User = Relationship(back_populates="todos")
    user_id: int = Field(foreign_key="user.id")


class TodoCreate(TodoBase):
    pass


class TodoPublic(TodoBase):
    id: int


class TodoUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, max_length=100)
    priority: int | None = Field(default=None, ge=1, le=5)
    completed: bool | None = None

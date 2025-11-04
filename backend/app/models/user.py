from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import IDMixin

if TYPE_CHECKING:
    from app.models.todo import Todo


class UserBase(SQLModel):
    first_name: str = Field(index=True, min_length=3, max_length=50)
    last_name: str = Field(index=True, min_length=3, max_length=50)
    email: EmailStr = Field(index=True, unique=True, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class User(IDMixin, UserBase, table=True):
    todos: list["Todo"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    pass


class UserPublic(SQLModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdate(SQLModel):
    first_name: str | None = Field(default=None, min_length=3, max_length=50)
    last_name: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)

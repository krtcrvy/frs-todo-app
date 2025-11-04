from sqlmodel import Field, SQLModel


class IDMixin(SQLModel):
    id: int | None = Field(default=None, primary_key=True)

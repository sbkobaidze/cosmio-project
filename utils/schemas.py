from typing import Any, Generic, Optional, TypedDict, TypeVar

from pydantic import BaseModel, EmailStr, constr


class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # Password must be at least 8 chars


class UserLogin(BaseModel):
    email: EmailStr
    password: str


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[list[dict[str, Any]]] = None


class IncomingFilterMessage(TypedDict):
    type: str
    pageSize: int
    from_date: Optional[str]
    to_date: Optional[str]

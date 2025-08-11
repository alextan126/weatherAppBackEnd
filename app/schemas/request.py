from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RequestBase(BaseModel):
    location: str
    request_type: str  # "current", "forecast", "historical"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class RequestInDBBase(RequestBase):
    id: int
    user_id: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Request(RequestInDBBase):
    pass


class RequestInDB(RequestInDBBase):
    pass 
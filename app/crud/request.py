from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.request import Request
from app.schemas.request import RequestCreate, RequestUpdate


def get_request(db: Session, request_id: int) -> Optional[Request]:
    return db.query(Request).filter(Request.id == request_id).first()


def get_requests(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Request]:
    query = db.query(Request)
    if user_id:
        query = query.filter(Request.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def create_request(db: Session, request: RequestCreate, user_id: Optional[int] = None) -> Request:
    db_request = Request(
        **request.dict(),
        user_id=user_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_request(db: Session, request_id: int, request: RequestUpdate) -> Optional[Request]:
    db_request = get_request(db, request_id)
    if not db_request:
        return None
    
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_request, field, value)
    
    db.commit()
    db.refresh(db_request)
    return db_request


def delete_request(db: Session, request_id: int) -> bool:
    db_request = get_request(db, request_id)
    if not db_request:
        return False
    
    db.delete(db_request)
    db.commit()
    return True


def get_requests_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Request]:
    return db.query(Request).filter(Request.status == status).offset(skip).limit(limit).all()


def get_requests_by_location(db: Session, location: str, skip: int = 0, limit: int = 100) -> List[Request]:
    return db.query(Request).filter(Request.location == location).offset(skip).limit(limit).all() 
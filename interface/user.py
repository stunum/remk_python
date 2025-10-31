from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
from typing import List

router = APIRouter()

@router.post("/users", response_model=dict)
def create_user(user: User, db: Session = Depends(get_db)):
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"code": 200, "msg": "success", "data": {"user_id": user.id}}

@router.get("/users/{user_id}", response_model=dict)
def find_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return {"code": 200, "msg": "success", "data": user}

@router.get("/users", response_model=dict)
def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    users = db.query(User).offset(offset).limit(page_size).all()
    total = db.query(User).count()
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "users": users,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
            },
        },
    }

@router.put("/users/{user_id}", response_model=dict)
def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    for key, value in user_data.items():
        setattr(user, key, value)
    db.commit()
    return {"code": 200, "msg": "success", "data": {}}

@router.delete("/users", response_model=dict)
def delete_users(user_ids: List[int], db: Session = Depends(get_db)):
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="用户未找到")
    for user in users:
        user.deleted_at = "CURRENT_TIMESTAMP"
    db.commit()
    return {"code": 200, "msg": "success", "data": {"deleted_count": len(users)}}
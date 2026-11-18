from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User
from backend.schemas.auth import UserResponse
from backend.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return db.query(User).all()

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    if role not in ["admin", "manager", "analyst"]:
        raise HTTPException(status_code=400, detail="Invalid role specified.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.role = role
    db.commit()
    db.refresh(user)
    return user

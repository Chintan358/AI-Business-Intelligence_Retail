from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, BusinessProfile
from backend.schemas.business import BusinessProfileResponse, BusinessProfileUpdate
from backend.dependencies import get_current_user

router = APIRouter(prefix="/business", tags=["Business Profile"])

@router.get("/profile", response_model=BusinessProfileResponse)
def get_business_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        profile = BusinessProfile(
            user_id=current_user.id,
            company_name="Apex Retail Global",
            industry="Retail",
            team_size="50-100",
            target_margin=25.00,
            business_goals="Drive gross profit margin to 25%, minimize digital return leakage, and eliminate stockouts on key inventory."
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/profile", response_model=BusinessProfileResponse)
def update_business_profile(
    profile_in: BusinessProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        profile = BusinessProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return profile


from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database.connection import get_db
from backend.database.models import Design, User
from backend.designs.schemas import DesignResponse


router = APIRouter(
    prefix="/api/designs",
    tags=["Design History"],
)


# Get all designs belonging to the logged-in user.
@router.get("/", response_model=list[DesignResponse])
def get_my_designs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = (
        select(Design)
        .where(Design.user_id == current_user.id)
        .order_by(Design.created_at.desc())
    )

    designs = db.scalars(statement).all()

    return designs

@router.get("/{design_id}", response_model=DesignResponse)
def get_design_by_id(
    design_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = select(Design).where(
        Design.id == design_id,
        Design.user_id == current_user.id,
    )

    design = db.scalar(statement)

    if design is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design not found.",
        )

    return design

@router.delete("/{design_id}")
def delete_design(
    design_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = select(Design).where(
        Design.id == design_id,
        Design.user_id == current_user.id,
    )

    design = db.scalar(statement)

    if design is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design not found.",
        )

    db.delete(design)
    db.commit()

    return {
        "message": "Design deleted successfully.",
        "design_id": str(design_id),
    }

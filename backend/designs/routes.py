
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database.connection import get_db
from backend.database.models import Design, User
from backend.designs.schemas import (
    DesignResponse,
    DesignListResponse,
)

from math import ceil

router = APIRouter(
    prefix="/api/designs",
    tags=["Design History"],
)


# Get all designs belonging to the logged-in user.
@router.get("/", response_model=DesignListResponse)
def get_my_designs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    room_type: str | None = Query(None),

    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Always filter by the authenticated user's ID.
    filters = [
        Design.user_id == current_user.id
    ]

    # Apply room-type filtering when provided.
    if room_type and room_type.strip():
        filters.append(
            Design.room_type.ilike(
                f"%{room_type.strip()}%"
            )
        )

    # Get the total number of matching designs.
    count_statement = (
        select(func.count())
        .select_from(Design)
        .where(*filters)
    )

    total = db.scalar(count_statement) or 0

    # Calculate how many pages are available.
    total_pages = ceil(total / page_size)

    # Calculate how many records to skip.
    offset = (page - 1) * page_size

    # Retrieve only the requested page.
    statement = (
        select(Design)
        .where(*filters)
        .order_by(Design.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    designs = db.scalars(statement).all()

    return {
        "items": designs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

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

from sqlalchemy.orm import Session

from backend.database.models import Design


def save_design(
    db: Session,
    user_id,
    room_type: str,
    design_input: dict,
    design_result: dict,
) -> Design:

    new_design = Design(
        user_id=user_id,
        room_type=room_type,
        design_input=design_input,
        design_result=design_result,
    )

    try:
        db.add(new_design)
        db.commit()
        db.refresh(new_design)

        return new_design

    except Exception:
        db.rollback()
        raise
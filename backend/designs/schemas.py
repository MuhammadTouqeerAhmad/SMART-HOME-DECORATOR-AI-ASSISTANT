from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DesignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    room_type: str
    design_input: dict
    design_result: dict
    created_at: datetime
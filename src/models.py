# from pydantic import BaseModel


# class RoomAnalysis(BaseModel):
#     room_type: str
#     visible_furniture: list[str]
#     colors: list[str]
#     lighting: str
#     storage: list[str]
#     layout_issues: list[str]
#     opportunities: list[str]


# class RecommendedItem(BaseModel):
#     product_id: int
#     name: str
#     reason: str
#     price: float


# class DesignStrategy(BaseModel):
#     design_summary: str
#     furniture_changes: list[str]
#     lighting_plan: list[str]
#     storage_plan: list[str]
#     color_plan: list[str]
#     recommended_products: list[RecommendedItem]
#     estimated_total: float
#     budget_status: str
#     explanation: str

from pydantic import BaseModel


class RoomAnalysis(BaseModel):

    room_type: str

    visible_furniture: list[str]

    colors: list[str]

    lighting: str

    storage: list[str]

    layout_issues: list[str]

    opportunities: list[str]


# class RecommendedProduct(BaseModel):

#     product_id: int

#     name: str

#     reason: str

#     price: float
#     priority: str


# class DesignStrategy(BaseModel):

#     design_summary: str

#     furniture_changes: list[str]

#     lighting_plan: list[str]

#     storage_plan: list[str]

#     color_plan: list[str]

#     recommended_products: list[
#         RecommendedProduct
#     ]

#     estimated_total: float

#     budget_status: str

#     explanation: str

class ImprovementPriority(BaseModel):
    category: str
    priority: str
    reason: str

class DesignStrategy(BaseModel):
    design_summary: str
    furniture_changes: list[str]
    lighting_plan: list[str]
    storage_plan: list[str]
    color_plan: list[str]
    improvement_priorities: list[ImprovementPriority]
    explanation: str
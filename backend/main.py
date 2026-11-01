
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

#from src.agent import graph
from backend.auth.routes import router as auth_router
from backend.designs.routes import router as designs_router

from backend.services.design_service import generate_design

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_optional_current_user
from backend.database.connection import get_db
from backend.database.models import User
from backend.designs.service import save_design

import logging

from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Home Decorator API",
    description="API for AI-powered interior design recommendations.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(designs_router)

# Allow the React development frontend to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_text(value: str, field_name: str) -> str:
    value = value.strip()

    if not value:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} cannot be empty.",
        )

    return value

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}

@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request, exc):
    logger.error(
        "Database error: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database error occurred. Please try again later."
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    logger.error(
        "Unexpected server error: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred. Please try again later."
        },
    )

@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Home Decorator API!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Home Decorator API",
    }

def validate_uploaded_image(image: UploadFile) -> tuple[bytes, str]:
    # Check the declared MIME type.
    mime_type = image.content_type or ""

    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WEBP images are supported.",
        )

    # Read only one byte more than the allowed limit.
    image_bytes = image.file.read(MAX_IMAGE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    # Check file size.
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size cannot exceed 5 MB.",
        )

    # Check the actual file signature.
    is_jpeg = image_bytes.startswith(b"\xff\xd8\xff")
    is_png = image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    is_webp = (
        len(image_bytes) >= 12
        and image_bytes.startswith(b"RIFF")
        and image_bytes[8:12] == b"WEBP"
    )

    valid_signatures = {
        "image/jpeg": is_jpeg,
        "image/png": is_png,
        "image/webp": is_webp,
    }

    if not valid_signatures[mime_type]:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not match its declared image format.",
        )

    return image_bytes, mime_type

@app.post("/api/design")
def create_design(
    image: UploadFile = File(...),
    room_type: str = Form(...),
    dimensions: str = Form(...),
    budget: float = Form(..., gt=0),
    currency: str = Form("PKR"),
    style: str = Form(...),
    existing_furniture: str = Form(...),
    requirements: str = Form(...),

    # Optional authentication:
    # Guests can generate designs without a token.
    # Registered users can generate and save designs.
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    # Validate the uploaded image.
    image_bytes, mime_type = validate_uploaded_image(image)

    # Prepare input for the existing LangGraph agent.
    design_input = {
        "room_type": validate_text(room_type, "Room type"),
        "dimensions": validate_text(dimensions, "Dimensions"),
        "budget": budget,
        "currency": validate_text(currency, "Currency"),
        "style": validate_text(style, "Style"),
        "existing_furniture": existing_furniture.strip(),
        "requirements": requirements.strip(),
        
    }

    initial_state = {
        "user_requirements": design_input,
        "image_bytes": image_bytes,
        "mime_type": mime_type,
        "room_analysis": {},
        "retrieved_knowledge": [],
        "available_products": [],
        "design_strategy": {},
        "selected_products": [],
        "budget_result": {},
        "budget_adjustment_attempts": 0,
        "budget_adjustment_made": False,
        "user_feedback": "",
        "final_plan": {},
    }

    try:
        # Generate the design using the existing AI workflow.
        result = generate_design(initial_state)

    except Exception as exc:
        print(f"AI design workflow failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail=(
                "The AI design workflow failed. "
                "Check the backend terminal for details."
            ),
        ) from exc

    # Prepare the response.
    response = {
        "message": "Design generated successfully.",
        "room_analysis": result.get("room_analysis", {}),
        "retrieved_knowledge": result.get(
            "retrieved_knowledge", []
        ),
        "design_strategy": result.get("design_strategy", {}),
        "selected_products": result.get(
            "selected_products", []
        ),
        "budget_result": result.get("budget_result", {}),
        "final_plan": result.get("final_plan", {}),
    }

    # Save the design only when the user is authenticated.
    if current_user is not None:
        try:
            saved_design = save_design(
                db=db,
                user_id=current_user.id,
                room_type=room_type.strip(),
                design_input=design_input,
                design_result=response,
            )

            response["saved"] = True
            response["design_id"] = str(saved_design.id)

        except Exception as exc:
            print(f"Design saving failed: {exc}")

            raise HTTPException(
                status_code=500,
                detail="Design was generated but could not be saved.",
            ) from exc

    else:
        response["saved"] = False
        response["design_id"] = None

    return jsonable_encoder(response)

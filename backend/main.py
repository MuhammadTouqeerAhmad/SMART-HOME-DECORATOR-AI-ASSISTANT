
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

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
    mime_type = image.content_type or ""

    if not mime_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file.",
        )

    image_bytes = image.file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    # Prepare input for the existing LangGraph agent.
    design_input = {
        "room_type": room_type.strip(),
        "dimensions": dimensions.strip(),
        "budget": budget,
        "currency": currency.strip(),
        "style": style.strip(),
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


from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from src.agent import graph


app = FastAPI(
    title="AI Home Decorator API",
    description="API for AI-powered interior design recommendations.",
    version="1.0.0",
)


# Allow the React development frontend to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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

    # Prepare the input in the format expected by
    # the existing LangGraph agent.
    initial_state = {
        "user_requirements": {
            "room_type": room_type.strip(),
            "dimensions": dimensions.strip(),
            "budget": budget,
            "currency": currency.strip(),
            "style": style.strip(),
            "existing_furniture": existing_furniture.strip(),
            "requirements": requirements.strip(),
        },
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
        # Run the existing AI workflow.
        result = graph.invoke(initial_state)

    except Exception as exc:
        # Details remain in the backend terminal for debugging.
        print(f"AI design workflow failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail=(
                "The AI design workflow failed. "
                "Check the backend terminal for details."
            ),
        ) from exc

    # Do not return image_bytes or the entire internal state.
    # Return only the information needed by the frontend.
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

    return jsonable_encoder(response)

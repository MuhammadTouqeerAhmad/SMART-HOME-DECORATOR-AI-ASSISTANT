import base64

from google import genai

from src.config import GEMINI_API_KEY
from src.models import RoomAnalysis


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


def analyze_room(
    image_bytes: bytes,
    mime_type: str
) -> RoomAnalysis:

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")


    prompt = """
You are an expert interior decoration assistant.

Analyze the uploaded room image.

Identify:

1. The likely room type
2. Visible furniture
3. Main colors
4. Lighting conditions
5. Existing storage
6. Layout problems
7. Decoration opportunities

Important rules:

- Only report things that are visible or reasonably
  inferable from the image.
- Do not invent furniture.
- Do not recommend replacing existing furniture at
  this stage.
- Focus on observations rather than design suggestions.
"""


    interaction = client.interactions.create(

        model=MODEL_NAME,

        input=[

            {
                "type": "text",
                "text": prompt
            },

            {
                "type": "image",
                "data": image_base64,
                "mime_type": mime_type
            }
        ],

        response_format={

            "type": "text",

            "mime_type": "application/json",

            "schema":
                RoomAnalysis.model_json_schema()
        }
    )


    return RoomAnalysis.model_validate_json(
        interaction.output_text
    )
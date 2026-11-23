import base64
import json
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("chefai")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "global")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-3.5-flash")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
app = FastAPI(title="ChefAI")


class RecipeRequest(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    max_time: int = Field(ge=5, le=180)


class Section(BaseModel):
    title: str
    items: list[str]


class Recipe(BaseModel):
    name: str
    prep_time: int
    cook_time: int
    ingredients: list[Section]
    instructions: list[Section]


def generate_recipe_text(description: str, max_time: int) -> Recipe:
    prompt = (
        f"Write a recipe for: {description}.\n"
        f"Prep time plus cook time must not exceed {max_time} minutes.\n"
        "Group ingredients and instructions into named sections "
        '(e.g. "Sauce", "Pasta"). Times are whole minutes.'
    )
    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Recipe,
            temperature=0.7,
        ),
    )
    return Recipe.model_validate(json.loads(response.text))


def generate_recipe_image(dish_name: str) -> str | None:
    """Returns a base64 PNG, or None if image generation fails."""
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=f"Professional food photography of {dish_name}, plated, natural light.",
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                return base64.b64encode(part.inline_data.data).decode()
    except Exception:
        log.exception("Image generation failed")
    return None


# Plain `def` (not async): the SDK calls are blocking, so FastAPI runs this
# in a worker thread instead of freezing the event loop.
@app.post("/recipe")
def create_recipe(req: RecipeRequest):
    try:
        recipe = generate_recipe_text(req.description, req.max_time)
    except Exception:
        log.exception("Recipe generation failed")
        raise HTTPException(status_code=502, detail="Couldn't generate a recipe. Try again.")

    data = recipe.model_dump()
    data["total_time"] = recipe.prep_time + recipe.cook_time
    data["image"] = generate_recipe_image(recipe.name)
    return data


@app.get("/")
def home():
    return FileResponse("templates/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

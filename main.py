import base64
import json
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.preview.vision_models import ImageGenerationModel

# --- CLOUD RUN AUTH BYPASS ---
# This ensures the "Robot Key" is used even when deployed
GOOGLE_CREDS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if GOOGLE_CREDS and os.path.exists(GOOGLE_CREDS):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDS
app = FastAPI()

# --- CONFIGURATION ---
PROJECT_ID = os.getenv("PROJECT_ID", "your-default-project")
LOCATION = os.getenv("LOCATION", "us-central1")
EMPL_ID_LASTNAME = os.getenv("EMPL_ID_LASTNAME", "PRIVATE")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

class RecipeRequest(BaseModel):
    description: str
    max_time: int

def generate_recipe_text(description, max_time):
    # Matches the 'Workhorse' model verified in your Studio
    model = GenerativeModel("gemini-2.0-flash-001")

    prompt = f"""
    Generate a recipe for {description}.
    IMPORTANT: The total time (prep + cook) MUST NOT exceed {max_time} minutes.
    Return ONLY a JSON object with this exact structure:
    {{
        "name": "string",
        "prep_time": 0,
        "cook_time": 0,
        "total_time": 0,
        "ingredients": [ {{"Part Name": ["item 1", "item 2"]}} ],
        "instructions": [ {{"Part Name": ["step 1", "step 2"]}} ]
    }}
    Note: prep_time, cook_time, and total_time must be integers (minutes).
    """
    
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7
        )
    )
    return json.loads(response.text)

def generate_recipe_image(dish_name):
    IMAGEN_MODEL_NAME = "imagen-3.0-generate-001" 
    try:
        model = ImageGenerationModel.from_pretrained(IMAGEN_MODEL_NAME)
        images = model.generate_images(
            prompt=f"A professional food photography shot of {dish_name}",
            number_of_images=1,
        )
        img_bytes = images[0]._image_bytes
        return base64.b64encode(img_bytes).decode("utf-8")
    except Exception as e:
        print(f"Image Generation Error: {str(e)}")
        return "" 

@app.get("/id")
def get_id():
    return EMPL_ID_LASTNAME

@app.post("/recipe")
async def create_recipe(req: RecipeRequest):
    try:
        # 1. Generate Recipe Text
        recipe_data = generate_recipe_text(req.description, req.max_time)
        
        # --- FIX FOR "List Indices" ERROR ---
        # If the AI returns a list like [ {...} ], take the first item
        if isinstance(recipe_data, list):
            recipe_data = recipe_data[0]
        # -------------------------------------
         # time calculation
        prep = recipe_data.get('prep_time', 0)
        cook = recipe_data.get('cook_time', 0)
        recipe_data['total_time'] = int(prep) + int(cook)
        # 2. Generate Recipe Image
        # Use .get() to avoid crashing if a key is missing
        dish_name = recipe_data.get('name', req.description)
        image_b64 = generate_recipe_image(dish_name)
        recipe_data['image'] = image_b64
        
        return recipe_data
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        # This sends the error to your browser console so you can see it
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        # Looking in the templates folder
        with open("templates/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: index.html not found in templates folder."

if __name__ == "__main__":
    import uvicorn
    # Important: host 0.0.0.0 is required for Cloud Run
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

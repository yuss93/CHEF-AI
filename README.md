# ChefAI

Describe a dish and set a time limit, and ChefAI writes a recipe that fits it, along with a generated photo of the finished dish.

Built with FastAPI and Google's Gemini models on Vertex AI.

## How it works

- `POST /recipe` takes a dish description and a max time (5–180 minutes).
- Gemini returns the recipe as JSON. The output is constrained to a schema and validated with Pydantic, so the frontend always gets the same shape back.
- The total time is calculated on the server from prep + cook time, not taken from the model.
- A second Gemini call generates a photo of the dish. If that call fails, the recipe still comes back without an image.
- The frontend is plain HTML/CSS/JS. Leave the dish field empty and it picks a surprise.

## Tech

Python · FastAPI · Pydantic · Google Gen AI SDK (Vertex AI) · HTML/CSS/JavaScript

## Run it locally

You need a Google Cloud project with the Vertex AI API enabled.

```bash
git clone https://github.com/yuss93/CHEF-AI.git
cd CHEF-AI
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

gcloud auth application-default login
export PROJECT_ID="your-gcp-project-id"

uvicorn main:app --reload --port 8080
```

Then open http://localhost:8080.

Optional environment variables: `LOCATION` (default `global`), `TEXT_MODEL` (default `gemini-3.5-flash`), `IMAGE_MODEL` (default `gemini-3.1-flash-image`).

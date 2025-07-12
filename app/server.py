# app/server.py

import os
import yaml
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from pydantic import BaseModel
from langserve import add_routes

# Import the agent factory from our other file
from app.agent import create_business_agent

# --- 1. Initial Setup ---
load_dotenv()

# Create the main FastAPI app instance
app = FastAPI(
    title="Business Analyst Server",
    version="1.0",
    description="A server combining the business agent with a custom UI.",
)

# --- 2. Add the LangServe Agent Routes ---
# This makes the agent available at the /agent path with a playground
add_routes(
    app,
    create_business_agent(),
    path="/agent",
)

# --- 3. Add Custom UI Routes ---

# Setup directories for our static files and HTML templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
CONFIG_FILE = os.path.join(BASE_DIR, "..", "config.yaml")

class LLMSettings(BaseModel):
    provider_url: str
    model_name: str
    temperature: float

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main custom chat interface."""
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "llm_settings": config.get("llm_settings", {}),
    })

@app.post("/update-settings", response_class=JSONResponse)
async def update_settings(settings: LLMSettings):
    """Saves configuration changes from the UI."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            current_config = yaml.safe_load(f)
        current_config['llm_settings'] = settings.dict()
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(current_config, f, indent=2)
        return {"message": "Settings updated successfully!"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to save settings: {e}"})

@app.post("/analyze", response_class=JSONResponse)
async def analyze_data(
    daily_revenue: float = Form(...), daily_cost: float = Form(...), daily_customers: int = Form(...),
    prev_revenue: float = Form(...), prev_cost: float = Form(...), prev_customers: int = Form(...),
):
    """Endpoint for the UI to call. It invokes the agent internally."""
    try:
        agent = create_business_agent()
        input_data = {
            "daily_data": {"revenue": daily_revenue, "cost": daily_cost, "number_of_customers": daily_customers},
            "previous_day_data": {"revenue": prev_revenue, "cost": prev_cost, "number_of_customers": prev_customers}
        }
        # LangSmith will trace this invocation automatically
        result = agent.invoke(input_data)
        return JSONResponse(content={"report": result.get("recommendations", {})})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An unexpected error occurred: {str(e)}"})
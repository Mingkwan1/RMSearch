from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os, httpx, asyncio

app = FastAPI()

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

load_dotenv()

headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {os.getenv('RUNPOD_API_KEY')}"}

# CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace this with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the URL for your Runpod Serverless API endpoint
RUNPOD_URL = "https://api.runpod.ai/v2/obhiuyqj2cpkhy/run"  # Replace YOUR_RUNPOD_ID
RUNPOD_ENDPOINT_ID = "obhiuyqj2cpkhy"
# Serve index.html on root
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/index.html") as f:
        content = f.read()
    return content


# Define request and response model for sending a query to Runpod
class Prompt(BaseModel):
    prompt: str

@app.post("/ask")
async def ask(prompt: Prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('RUNPOD_API_KEY')}"
    }

    payload = {"input": {"prompt": prompt.prompt}}

    # Submit job
    async with httpx.AsyncClient() as client:
        submit_res = await client.post(RUNPOD_URL, json=payload, headers=headers)

    if submit_res.status_code != 200:
        return {"error": "Runpod submission failed", "details": submit_res.text}

    job_id = submit_res.json().get("id")
    status_url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}"

    # Poll for result
    while True:
        async with httpx.AsyncClient() as client:
            status_res = await client.get(status_url, headers=headers)

        status_json = status_res.json()
        status = status_json.get("status")

        if status == "COMPLETED":
            return {"answer": status_json["output"]}
        elif status == "FAILED":
            return {"error": "Runpod job failed"}
        
        await asyncio.sleep(1)  # wait before polling again
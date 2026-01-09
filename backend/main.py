import csv
import os
from fastapi import FastAPI, UploadFile, File, Form
import json
from fastapi.middleware.cors import CORSMiddleware
from quadrat_crop import crop_quadrat_from_points
from openai_context import get_images_from_crop
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/crop-quadrat")
async def crop_quadrat(image: UploadFile = File(...), points: str = Form(...), name: str = Form(...)):
    image_bytes = await image.read()
    pts = json.loads(points)

    crop_result = crop_quadrat_from_points(image_bytes, pts)

    ai_result = get_images_from_crop(crop_result["cropped_image"], crop_result["context_image"], name)

    return {
        "cropped_image": base64.b64encode(crop_result["cropped_image"]).decode(),
        "context_image": base64.b64encode(crop_result["context_image"]).decode(),
        "corners": pts,
        "ai_result": ai_result
    }

CSV_PATH = "./quadrat_data.csv"

@app.get("/api/quadrat-data")
def get_quadrat_data():
    if not os.path.exists(CSV_PATH):
        return {"data": []}

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    return {"data": data}
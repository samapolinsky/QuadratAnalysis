from fastapi import FastAPI, UploadFile, File, Form
import json
from fastapi.middleware.cors import CORSMiddleware
from quadrat_crop import crop_quadrat_from_points
from openai_context import get_images_from_crop
import base64
from openai import OpenAI

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
async def crop_quadrat(image: UploadFile = File(...), points: str = Form(...)):
    image_bytes = await image.read()
    pts = json.loads(points)

    result = crop_quadrat_from_points(image_bytes, pts)

    get_images_from_crop(result["cropped_image"], result["context_image"], 0)

    return {
        "cropped_image": base64.b64encode(result["cropped_image"]).decode(),
        "context_image": base64.b64encode(result["context_image"]).decode(),
        "corners": pts
    }

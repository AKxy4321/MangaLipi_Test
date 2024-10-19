from fastapi import FastAPI, HTTPException
from pipeline.llm import LLM
from pipeline.models import TranslateRequest, MangaRequest
from pipeline.scraper import MangaScraper
import os
from fastapi.staticfiles import StaticFiles
from pipeline.image_processory import OCR
import base64
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from PIL import Image
from io import BytesIO

app = FastAPI()

ocr = OCR()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = LLM()
app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get('/v1/api/health')
def health_check():
    return {"status": "ok"}

@app.post('/v1/api/translate')
def translate(request: TranslateRequest):
    return llm.translate(request.text, request.source_lang, request.target_lang)

@app.post('/v2/api/translate')
def translate_v2(request: TranslateRequest):
    return llm.translate_sarvam(request.text, request.source_lang, request.target_lang)

@app.get('/v1/api/manga-list')
def get_manga_list():
    data_dir = 'data/images'
    try:
        folders = [name for name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, name))]
        return {"chapters": folders}  # Return the actual list of manga chapters
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data directory not found.")

@app.post('/v1/api/submit/manga')
async def submit_manga(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # contents is in bytes


        # Convert the uploaded file content to a PIL image
        try:
            image = Image.open(BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
        

        image.save('manga.jpg')

        try:
            ocr_response = await ocr.translate_image('manga.jpg')
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error during OCR processing: {str(e)}")



        try:
            encoded_image = base64.b64encode(ocr_response).decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error encoding image: {str(e)}")

        return {"encoded_image": encoded_image}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
from fastapi import FastAPI
from pipeline.llm import LLM
from pipeline.models import TranslateRequest
import os

app = FastAPI()
llm = LLM()


@app.get('/v1/api/health')
def health_check():
    return {"status": "ok"}

@app.post('/v1/api/translate')
def translate(Request : TranslateRequest):
    return llm.translate(Request.text, Request.source_lang, Request.target_lang)

@app.get('/v1/api/manga-list')
def get_manga_list():
    data_dir = 'data/images'
    folders = [name for name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, name))]
    return {"chapters": folders}

@app.post('/v1/api/submit/manga')
def submit_manga():
    return {"status": "ok"}


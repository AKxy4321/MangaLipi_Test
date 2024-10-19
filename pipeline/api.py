from fastapi import FastAPI
from pipeline.llm import LLM
from pipeline.models import TranslateRequest

app = FastAPI()
llm = LLM()


@app.get('/v1/api/health')
def health_check():
    return {"status": "ok"}

@app.post('/v1/api/translate')
def translate(Request : TranslateRequest):
    return llm.translate(Request.text, Request.source_lang, Request.target_lang)

from pydantic import BaseModel
from typing import List

class OCR_Response(BaseModel):
    boxes: List[List[int]]
    texts: List[str]

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str


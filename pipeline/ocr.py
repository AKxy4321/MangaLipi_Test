# from paddleocr import PaddleOCR, draw_ocr
# import matplotlib.pyplot as plt
# from PIL import Image

# # Initialize PaddleOCR
# ocr = PaddleOCR(use_angle_cls=True, lang='en')

# # Path to your image
# image_path = 'data/images/berserk.png'

# # Perform OCR on the image
# result = ocr.ocr(image_path, cls=True)

# # Extract bounding boxes and text
# boxes = [line[0] for line in result[0]]
# texts = [line[1][0] for line in result[0]]

# # Print bounding boxes and text
# for box, text in zip(boxes, texts):
#     print(f"Box: {box}, Text: {text}")

# # Visualize the results
# image = Image.open(image_path).convert('RGB')

# this code is not working on my machine 


from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from pipeline.models import OCR_Response

class OCR:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def extract_text(self, image_path):
        result = self.ocr.ocr(image_path, cls=True)
        boxes = [line[0] for line in result[0]]
        texts = [line[1][0] for line in result[0]]
        return OCR_Response(boxes=boxes, texts=texts)
    





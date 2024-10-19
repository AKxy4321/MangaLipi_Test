from paddleocr import PaddleOCR
from pydantic import BaseModel
import cv2
import numpy as np


# # Initialize the OCR model; use GPU if available
# ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='en')  # Use lang='ch' for Chinese, etc.

# # Specify the image path
# image_path = 'data/images/berserk.png'  # Replace with your image path

# # Perform OCR on the image
# result = ocr.ocr(image_path, cls=True)

# # Print the result
# for line in result:
#     for word_info in line:
#         print(f'Text: {word_info[1][0]}, Confidence: {word_info[1][1]}')

class OCR_Response(BaseModel):
    boxes: list
    texts: list


class OCR:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='en')  
    

    def get_ocr(self, image_path: str):
        """
        Performs OCR on the given image.

        Args:
            image_path (str): The path to the image.

        Returns:
            OCR_Response: An OCR_Response object containing the bounding boxes and texts.
        """
        result = self.ocr.ocr(image_path, cls=True)
        boxes = []
        texts = []
        for line in result:
            for word_info in line:
                boxes.append(word_info[0])
                texts.append(word_info[1][0])
        return OCR_Response(boxes=boxes, texts=texts)
    
    def does_intersect(self, box1, box2) -> bool:
        """
        Checks if two boxes intersect.

        Args:
            box1 (list): The first box.
            box2 (list): The second box.

        Returns:
            bool: True if the boxes intersect, False otherwise.
        """


        acord1, acord2, acord3, acord4 = box1
        bcord1, bcord2, bcord3, bcord4 = box2

        box_1_y_average = (acord1[1] + acord2[1] + acord3[1] + acord4[1]) / 4
        box_2_y_average = (bcord1[1] + bcord2[1] + bcord3[1] + bcord4[1]) / 4

        box_1_x_average = (acord1[0] + acord2[0] + acord3[0] + acord4[0]) / 4
        box_2_x_average = (bcord1[0] + bcord2[0] + bcord3[0] + bcord4[0]) / 4



        if(abs(box_1_y_average - box_2_y_average) > 3 and abs(box_1_x_average - box_2_x_average) > 3):
            return False
        else:
            return True
    
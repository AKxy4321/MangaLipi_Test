from paddleocr import PaddleOCR
from pydantic import BaseModel
import cv2
import numpy as np
from matplotlib import pyplot as plt

class OCR_Response(BaseModel):
    boxes: list
    texts: list

class OCR:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='en')

    def get_ocr(self, image_path: str) -> OCR_Response:
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
    
    def merge_boxes(self, OCR_Response : OCR_Response):

        merged_boxes = []

        for text,box in zip(OCR_Response.texts, OCR_Response.boxes):
            box = [tuple(map(int, point)) for point in box]

            # Calculate the area of the bounding box
            area = cv2.contourArea(np.array(box))
            # Define the area threshold
            area_threshold = 100

            box = [tuple(map(int, point)) for point in box]

            x_average = sum([point[0] for point in box]) / 4
            y_average = sum([point[1] for point in box]) / 4

            for point in box:
                x_low = min([point[0] for point in box])
                y_low = min([point[1] for point in box])
                x_high = max([point[0] for point in box])
                y_high = max([point[1] for point in box])

            nearest_neighbor = None
            min_distance = float('inf')


            for mb in merged_boxes:
                distance = np.sqrt((mb[0] - x_average) ** 2 + (mb[1] - y_average) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_neighbor = mb

            if nearest_neighbor and min_distance < 50:
                merged_boxes.remove(nearest_neighbor)
                merged_boxes.append([x_average, y_average, nearest_neighbor[2] + " " + text, nearest_neighbor[3], nearest_neighbor[4], x_high, y_high])
            else:
                merged_boxes.append([x_average, y_average, text, x_low, y_low, x_high, y_high])

        return merged_boxes


# Initialize OCR
ocr = OCR()

# Read the image
image_path = 'data/images/jojo-no-kimyou-na-bouken-part-7-steel-ball-run-chapter-93/17.jpg'
image = cv2.imread(image_path)

# Perform OCR on the image
response = ocr.get_ocr(image_path)

# Merge the bounding boxes
merged_boxes = ocr.merge_boxes(response)

# Draw the merged bounding boxes
for box in merged_boxes:
    x, y, text, x_low, y_low, x_high, y_high = box
    cv2.rectangle(image, (x_low, y_low), (x_high, y_high), (0, 255, 0), 2)
    cv2.putText(image, text, (x_low, y_low - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save the image
cv2.imwrite('21_annotated.jpg', image)

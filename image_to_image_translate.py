import cv2
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image, ImageDraw, ImageFont

import numpy as np

# groq_translation.py
import json
from typing import Optional

from groq import Groq
from pydantic import BaseModel

import textwrap

# Set up the Groq client
client = Groq(api_key="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")

# Model for the translation
class Translation(BaseModel):
    text: str
    comments: Optional[str] = None


# Translate text using the Groq API
def groq_translate(query, from_language, to_language):
    # Create a chat completion
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that translates text from {from_language} to {to_language}."
                           f"You will only reply with the translation text and nothing else in JSON."
                           f" The JSON object must use the schema: {json.dumps(Translation.model_json_schema(), indent=2)}",
            },
            {
                "role": "user",
                "content": f"Translate '{query}' from {from_language} to {to_language}."
            }
        ],
        model="llama3-70b-8192", # "llama-3.2-90b-text-preview"
        temperature=0.2,
        max_tokens=1024,
        stream=False,
        response_format={"type": "json_object"},
    )
    # Return the translated text
    return Translation.model_validate_json(chat_completion.choices[0].message.content)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def apply_paddle_ocr(image_path):
    # Perform OCR on the image
    result = ocr.ocr(image_path, cls=True)

    # Extract bounding boxes and text
    boxes = [line[0] for line in result[0]]
    texts = [line[1][0] for line in result[0]]

    print("paddle ocr boxes and texts:")
    # Print bounding boxes and text
    for box, text in zip(boxes, texts):
        print(f"Box: {box}, Text: {text}")
    
    return boxes, texts

# Assuming 'image' is your NumPy image and 'boxes' is the list of bounding boxes
def draw_boxes(image, boxes):
    image_np = image
    if isinstance(image, Image.Image):
        image_np = np.array(image)
    image_np = np.array(image)  # Convert PIL Image to NumPy array if needed

    np_untexted_image = image_np.copy()  # Create a copy of the image to draw on

    for box in boxes:
        x1, y1 = int(min(box[0][0], box[1][0])), int(min(box[0][1], box[1][1]))
        x2, y2 = int(max(box[2][0], box[3][0])), int(max(box[2][1], box[3][1]))
        cv2.rectangle(np_untexted_image, (x1, y1), (x2, y2), (255, 255, 255), -1)  # Draw a white filled rectangle

    untexted_image = Image.fromarray(np_untexted_image)
    # Now you can save or display the new_image_pil
    untexted_image.save('image_with_white_boxes.jpg')

    return np_untexted_image

def get_bounding_box(rectangle):
    """
    Given a rectangle defined by its corner coordinates, return the bounding box.

    Parameters:
    - rectangle: A list of four points, where each point is a list of [x, y].

    Returns:
    - A tuple (x_min, y_min, x_max, y_max) representing the bounding box.
    """
    x_coords = [point[0] for point in rectangle]
    y_coords = [point[1] for point in rectangle]

    x_min = min(x_coords)
    y_min = min(y_coords)
    x_max = max(x_coords)
    y_max = max(y_coords)

    return (x_min, y_min, x_max, y_max)

def intersecting_boxes(box1, box2, threshold=3):
    """
    Check if two boxes intersect with a given threshold, considering both expansion (+threshold)
    and contraction (-threshold).

    Args:
        box1 (list): Coordinates of the first box [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
        box2 (list): Coordinates of the second box [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
        threshold (float): Distance threshold for considering boxes as intersecting.

    Returns:
        bool: True if the boxes intersect within the threshold, False otherwise.
    """
    
    # Extract x and y coordinates for both boxes
    x1_coords = [point[0] for point in box1]
    x2_coords = [point[0] for point in box2]
    y1_coords = [point[1] for point in box1]
    y2_coords = [point[1] for point in box2]

    # Determine the bounding box for both sets of coordinates
    x1_min, y1_min = min(x1_coords), min(y1_coords)
    x1_max, y1_max = max(x1_coords), max(y1_coords)

    x2_min, y2_min = min(x2_coords), min(y2_coords)
    x2_max, y2_max = max(x2_coords), max(y2_coords)

    # Check if the boxes intersect considering both expansion (+threshold) and contraction (-threshold)
    
    # For x-coordinates
    x_overlap_expanded = not (x1_max + threshold < x2_min or x2_max + threshold < x1_min)
    x_overlap_contracted = not (x1_max - threshold < x2_min or x2_max - threshold < x1_min)
    
    # For y-coordinates
    y_overlap_expanded = not (y1_max + threshold < y2_min or y2_max + threshold < y1_min)
    y_overlap_contracted = not (y1_max - threshold < y2_min or y2_max - threshold < y1_min)

    # Return True if either expanded or contracted ranges overlap in both x and y coordinates
    return (x_overlap_expanded and y_overlap_expanded) or (x_overlap_contracted and y_overlap_contracted)


def merge_boxes(box1, box2):
    """
    Merges two boxes.

    Args:
        box1 (list): The first box.
        box2 (list): The second box.

    Returns:
        list: The merged box.
    """

    x_coords = [point[0] for point in box1+box2]
    y_coords = [point[1] for point in box1+box2]

    x1 = min(x_coords)
    x2 = max(x_coords)
    y1 = min(y_coords)
    y2 = max(y_coords)

    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def merge_intersecting_boxes(super_boxes):
    """
    Merges intersecting boxes.

    Args:
        boxes (list): A list of boxes.

    Returns:
        list: A list of merged boxes.
    """
    merged_super_boxes = []
    for super_box in super_boxes:
        box, text = super_box
        if not merged_super_boxes:
            merged_super_boxes.append(super_box)
        else:
            intersecting = False
            for i, merged_super_box in enumerate(merged_super_boxes):
                merged_box, merged_text = merged_super_box
                if intersecting_boxes(merged_box, box):

                    new_super_box = (merge_boxes(merged_box, box), merged_text + " " + text)

                    merged_super_boxes[i] = new_super_box
                    intersecting = True
                    break
            if not intersecting:
                merged_super_boxes.append(super_box)
    return merged_super_boxes

def draw_text_in_rectangle(image, text, font_path, box, max_font_size):
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1

    for font_size in range(max_font_size, 0, -1):
        font = ImageFont.truetype(font_path, font_size)
        # Initial wrap based on bounding box width
        lines = textwrap.wrap(text, width=int(w / draw.textbbox((0, 0), ' ', font=font)[2]))
        wrapped_lines = []
        for line in lines:
            # Further wrap each line if it exceeds the bounding box width
            while draw.textbbox((0, 0), line, font=font)[2] > w:
                split_index = line.rfind(' ', 0, int(len(line) * w / draw.textbbox((0, 0), line, font=font)[2]))
                if split_index == -1:
                    break
                wrapped_lines.append(line[:split_index])
                line = line[split_index + 1:]
            wrapped_lines.append(line)
        
        total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_lines])
        if total_text_height <= h:
            y_offset = y1 + (h - total_text_height) // 2
            for line in wrapped_lines:
                line_width, line_height = draw.textbbox((0, 0), line, font=font)[2], draw.textbbox((0, 0), line, font=font)[3]
                draw.text(((x1 + (w - line_width) // 2), y_offset), line, font=font, fill="black")
                y_offset += line_height
            break
    return image


# Path to your image
image_path = 'data/images/jojo-no-kimyou-na-bouken-part-7-steel-ball-run-chapter-95/36.jpg'
image = Image.open(image_path).convert('RGB')
boxes,texts = apply_paddle_ocr(image_path)
untexted_image_np = draw_boxes(image, boxes)
super_boxes = list(zip(boxes, texts))
super_boxes.sort(key=lambda super_box:super_box[0][1], reverse=True)
merged_boxes = merge_intersecting_boxes(super_boxes)
merged_boxes = merge_intersecting_boxes(merged_boxes)
merged_boxes = merge_intersecting_boxes(merged_boxes)
merged_boxes = merge_intersecting_boxes(merged_boxes)

translated_image = untexted_image_np.copy()
draw = ImageDraw.Draw(translated_image)
font = ImageFont.truetype("data/fonts/NotoSansKannada-Regular.ttf", size=20)

# Use the function to draw text in each bounding box
for box, text in merged_boxes:
    translated_text = groq_translate(text, from_language="english", to_language="kannada").text
    translated_image = draw_text_in_rectangle(translated_image, translated_text, "data/fonts/NotoSansKannada-Regular.ttf", get_bounding_box(box), max_font_size=20)

# Save the image with the translated text
translated_image.save("translated_image_better.jpg")
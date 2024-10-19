from paddleocr import PaddleOCR
from pydantic import BaseModel
import cv2
import numpy as np
from PIL import Image
from groq import Groq
import requests
from PIL import ImageFont, ImageDraw
import textwrap
import time

class LLM:
    """
    A class to interact with the Groq API for text preprocessing and translation.

    Methods
    -------
    __init__():
        Initializes the LLM class with the Groq client.

    _preprocess_sentence(raw_text):
        Internal method. Must not be called directly.
        Preprocesses the input text by correcting grammatical mistakes and optimizing it for translation.

    translate(raw_text, source_language, target_language):
        Translates the preprocessed text from the source language to the target language.
    """

    def __init__(self):
        self.client = Groq(
            # I know not secure blah blah blah dotenv is not fucking working
            api_key="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"
        )

    def _preprocess_sentence(self, raw_text) -> str:
        """
        Preprocesses the given raw text by correcting grammatical mistakes and optimizing it for translation.

        This method sends the raw text to a language model to:
        - Correct grammatical errors.
        - Substitute less frequent words with more frequent ones.
        - Ensure the text is optimized for translation.

        Parameters:
        raw_text (str): The raw text to be preprocessed.

        Returns:
        str: The preprocessed text with corrections and optimizations applied.
        """
        return self.client.chat.completions.create(
            messages=[
                {
                    "role" : "system",
                    "content" : "You must take the text and correct for grammatical mistakes and optimize the text for translation. Substitute Less Frequent Words with More Freuqent words used.You must only return the text asked. Don't return any additional text."
                },
                {
                    "role" : "user",
                    "content" : f"{raw_text}"
                }
            ],
            model="llama3-70b-8192"
        ).choices[0].message.content

    def translate(self, raw_text, source_language, target_language) -> str:
        """
        Translates the given raw text from the source language to the target language.

        Args:
            raw_text (str): The text to be translated.
            source_language (str): The language of the input text.
            target_language (str): The language to translate the text into.

        Returns:
            str: The translated text.

        """

        processed_text = self._preprocess_sentence(raw_text=raw_text)
        print(processed_text)
        return self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You must translate Text from {source_language} to {target_language}. Return only the translated text. Dont be formal with your translation.",
                },
                {
                    "role": "user",
                    "content": processed_text,
                }
            ],
            model="llama3-70b-8192",
        ).choices[0].message.content    
    

    def translate_sarvam(self, raw_text, source_language, target_language) -> str:
        """
        Translates the given raw text from the source language to the target language.

        Args:
            raw_text (str): The text to be translated.
            source_language (str): The language of the input text.
            target_language (str): The language to translate the text into.

        Returns:
            str: The translated text.

        """

        url = "https://api.sarvam.ai/translate"

        payload = {
            "model": "mayura:v1",
            "enable_preprocessing": True,
            "source_language_code": source_language,
            "target_language_code": target_language,
            "mode": "code-mixed",
            "input": raw_text
        }
        headers = {
            "api-subscription-key": "223f1de5-2860-4900-b3bb-e733ad9653a8",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        return response.text
    




class OCR_Response(BaseModel):
    boxes: list
    texts: list

class OCR:
    def __init__(self):
        self.llm = LLM()
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

        if result:
            for line in result:
                if line:
                    for word_info in line:
                        boxes.append(word_info[0])
                        texts.append(word_info[1][0])

        # Draw all the bounding boxes on the image
        image = cv2.imread(image_path)
        for box in boxes:
            box = [tuple(map(int, point)) for point in box]
            x_low = min([point[0] for point in box])
            y_low = min([point[1] for point in box])
            x_high = max([point[0] for point in box])
            y_high = max([point[1] for point in box])
            cv2.rectangle(image, (x_low, y_low), (x_high, y_high), (255, 0, 0), 2)

        # Save the image with all bounding boxes
        cv2.imwrite('unmerged.jpg', image)
        return OCR_Response(boxes=boxes, texts=texts)
    

# Assuming 'image' is your NumPy image and 'boxes' is the list of bounding boxes
    def draw_boxes(self, image, boxes):
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
    
    def merge_boxes(self, OCR_Response : OCR_Response, line_by_line = False):
        merged_boxes = []


        if line_by_line:
            for text, box in zip(OCR_Response.texts, OCR_Response.boxes):

                if text == " ":
                    continue
                box = [tuple(map(int, point)) for point in box]
                x_low = min([point[0] for point in box])
                y_low = min([point[1] for point in box])
                x_high = max([point[0] for point in box])
                y_high = max([point[1] for point in box])
                merged_boxes.append([x_low, y_low, text, x_low, y_low, x_high, y_high])


            return merged_boxes



        for text,box in zip(OCR_Response.texts, OCR_Response.boxes):
            box = [tuple(map(int, point)) for point in box]

            x_average = sum([point[0] for point in box]) / 4
            y_average = sum([point[1] for point in box]) / 4


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
                nearest_neighbor[3] = min(x_low, nearest_neighbor[3])
                nearest_neighbor[4] = min(y_low, nearest_neighbor[4])

                x_high = max(x_high, nearest_neighbor[5])
                y_high = max(y_high, nearest_neighbor[6])

                merged_boxes.append([x_average, y_average, nearest_neighbor[2] + " " + text, nearest_neighbor[3], nearest_neighbor[4], x_high, y_high])
            
                        
            else:
                merged_boxes.append([x_average, y_average, text, x_low, y_low, x_high, y_high])

        return merged_boxes
    
    def draw_text_in_rectangle(self, image, text, font_path, box, max_font_size):
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


    def translate_and_write(self, merged_boxes, white_image):
        # font_path = "../data/fonts/NotoSansTamil-Regular.ttf"
        translated_image = white_image.copy()

        translated_image = Image.fromarray(translated_image)

        for box in merged_boxes:
            x1, y1, x2, y2 = box[-4:]
            text = box[2]
            translated_text = self.llm.translate(text, "english", "tamil")

            ### comment this later time.sleep()
            # time.sleep(1)
            print(text, translated_text)
            translated_image = self.draw_text_in_rectangle(translated_image, translated_text, font_path, (x1, y1, x2, y2), 10)
            print("Iteration")
        # Save the translated image
        # translated_image.save('translated_image.jpg')

        return translated_image

    def translate_and_write_sarvam(self, merged_boxes, white_image):
        font_path = "../data/fonts/NotoSansTamil-Regular.ttf"
        translated_image = white_image.copy()

        translated_image = Image.fromarray(translated_image)

        for box in merged_boxes:
            x1, y1, x2, y2 = box[-4:]
            text = box[2]
            translated_text = self.llm.translate_sarvam(text, "en", "kn")
            print(text, translated_text)
            translated_image = self.draw_text_in_rectangle(translated_image, translated_text, font_path, (x1, y1, x2, y2), 10)
            print("Iteration")
        # Save the translated image
        translated_image.save('translated_image.jpg')

    def translate_image(self, image_path):
        response = self.get_ocr(image_path)
        merged_boxes = self.merge_boxes(response, line_by_line=False)
        untexted_image = self.draw_boxes(cv2.imread(image_path), response.boxes)
        reponseImage = self.translate_and_write(merged_boxes=merged_boxes, white_image=untexted_image)
        return reponseImage
    
    def translate_base64_image(self, base64_image):
        image = Image.open(base64_image)
        image.save('image.jpg')
        response = self.get_ocr('image.jpg')
        merged_boxes = self.merge_boxes(response, line_by_line=False)
        untexted_image = self.draw_boxes(image, response.boxes)
        reponseImage = self.translate_and_write(merged_boxes=merged_boxes, white_image=untexted_image)
        return reponseImage
    



# ocr = OCR()
# ocr.translate_image('./manga.jpg')


# # Initialize OCR
# ocr = OCR()

# # Read the image
# image_path = 'manga.jpg'
# image = cv2.imread(image_path)

# # Perform OCR on the image
# response = ocr.get_ocr(image_path)
# merged_boxes = ocr.merge_boxes(response, line_by_line=True)

# # Draw the bounding boxes on the image
# real_image = image.copy()

# for box in merged_boxes:
#     x1, y1, x2, y2 = box[-4:]
#     cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

# # Save the image with merged bounding boxes
# cv2.imwrite('merged.jpg', image)





# untexted_image = ocr.draw_boxes(real_image, response.boxes)
# ocr.translate_and_write(merged_boxes=merged_boxes, white_image=untexted_image)



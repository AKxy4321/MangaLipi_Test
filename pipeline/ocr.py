import paddle
paddle.device.set_device("gpu")

import paddleocr
ocr = paddleocr.OCR()
img_path = 'data/images/spotlight.png'
result = ocr.ocr(img_path)
for line in result:
    print(line)


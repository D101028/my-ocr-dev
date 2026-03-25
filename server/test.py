# Initialize PaddleOCR instance
import os
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
from paddleocr import PaddleOCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

# Run OCR inference on a sample image 

while True:
    filename = input(">>>")
    result = ocr.predict(input=filename)

    # Visualize the results and save the JSON results
    for res in result:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")
import json
import os
import re
from subprocess import Popen, PIPE

from texify.inference import batch_inference
from texify.model.model import load_model
from texify.model.processor import load_processor
from PIL import Image

from app.config import Config

# 定義不顯示視窗的 flag
CREATE_NO_WINDOW = 0x08000000

def convert_surya_to_latex(text):
    # 處理區塊數學式 <math display="block">...</math> -> \[ ... \]
    text = re.sub(r'<math display="block">(.*?)</math>', r'\\[ \1 \\]', text, flags=re.DOTALL)
    
    # 處理行內數學式 <math>...</math> -> \(...\)
    text = re.sub(r'<math>(.*?)</math>', r'\(\1\)', text, flags=re.DOTALL)
    
    # 處理加粗標籤 <b>...</b> -> \textbf{...}
    text = re.sub(r'<b>(.*?)</b>', r'\\textbf{\1}', text, flags=re.DOTALL)
    
    # 移除剩餘的 HTML 標籤（如有需要）
    text = re.sub(r'<[^>]+>', '', text)

    # 跳脫字元
    text = text.replace("$", r"\$")
    
    return text

def latex_ocr(img_path: str) -> str:
    process = Popen(
        ["surya_latex_ocr", img_path, "--output_dir", Config.TMP_SAVING_PATH], 
        stdout=PIPE, stderr=PIPE, text=True, creationflags=CREATE_NO_WINDOW
    )
    stdout, stderr = process.communicate()
    if process.returncode:
        raise Exception(stderr)
    process.wait()
    path = f"{Config.TMP_SAVING_PATH}/snip_output/results.json"
    if not os.path.isfile(path):
        raise Exception("OCR failed")
    with open(path, mode="r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    text = data["snip_output"][0]["equation"]

    return convert_surya_to_latex(text)

    # model = load_model()
    # processor = load_processor()
    # img = Image.open("out/snip_output.png") # Your image name here
    # results = batch_inference([img], model, processor)
    # code = "\n".join(results)
    # return code

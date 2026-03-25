from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
import torch
# 新版路徑改為 Predictor 模式
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.ocr import run_ocr

app = FastAPI()

# --- 全域預載入：啟動時只執行一次 ---
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"正在預載入 Surya 模型至 {device}...")
# 初始化 Predictor 就會自動載入模型權重
# 這兩個物件會一直佔用顯存，確保後續辨識是「熱啟動」
langs = ["ja", "zh", "en"] # 預設支援日、中、英
det_predictor = DetectionPredictor() # 預設會找 GPU
rec_predictor = RecognitionPredictor()

# 針對 GeForce 優化：使用編譯模式 (CUDA 13.0+)
# 這會讓第一次慢，但之後極快
# det_predictor.model = torch.compile(det_predictor.model) 
# rec_predictor.model = torch.compile(rec_predictor.model)

@app.post("/ocr")
async def do_ocr(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # 使用預載好的 Predictor 進行辨識
    # 注意：新版 run_ocr 接收的是 Predictor 物件
    predictions = run_ocr([image], [langs], det_predictor, rec_predictor)
    
    return {"status": "success", "data": predictions}
#!c:: ; Win + Alt + C
SetWorkingDir, D:\Projects\my-ocr-dev\client
Run, "D:\Projects\my-ocr-dev\client\.venv\Scripts\pythonw.exe" main.py --model ocr, , Hide
return

#!x:: ; Win + Alt + X
SetWorkingDir, D:\Projects\my-ocr-dev\client
Run, "D:\Projects\my-ocr-dev\client\.venv\Scripts\pythonw.exe" main.py --model latex, , Hide
return
PYTHONW_PATH := "your/path/to/pythonw.exe"

#!c:: ; Win + Alt + C
    SetWorkingDir, D:\Projects\Python\my-ocr-dev\client
    Run, "%PYTHONW_PATH%" main.py -c test.yaml --model ocr, , Hide
return

#!x:: ; Win + Alt + X
    SetWorkingDir, D:\Projects\Python\my-ocr-dev\client
    Run, "%PYTHONW_PATH%" main.py -c test.yaml --model latex, , Hide
return
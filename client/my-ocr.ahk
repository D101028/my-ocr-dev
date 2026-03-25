#!c:: ; Win + Alt + C
SetWorkingDir, D:\Projects\my-ocr-dev\client
; We add two commas to skip the "WorkingDir" parameter (since it's set above) and use "Hide"
Run, cmd.exe /c ".venv\Scripts\activate.bat && pythonw.exe main.py --model ocr", , Hide
return

#!x:: ; Win + Alt + X
SetWorkingDir, D:\Projects\my-ocr-dev\client
Run, cmd.exe /c ".venv\Scripts\activate.bat && pythonw.exe main.py --model latex", , Hide
return
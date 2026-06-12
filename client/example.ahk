#Requires AutoHotkey v2.0

global PYTHONW_PATH := "path/to/your/pythonw.exe"
global WORKING_DIR := "path/to/your/client/dir"

#!c:: ; Win + Alt + C (OCR 模式)
{
    targetCmd := '"' PYTHONW_PATH '" main.py -c test.yaml --model ocr'
    Run(targetCmd, WORKING_DIR, "Hide")
}

#!x:: ; Win + Alt + X (LaTeX 模式)
{
    targetCmd := '"' PYTHONW_PATH '" main.py -c test.yaml --model latex'
    Run(targetCmd, WORKING_DIR, "Hide")
}
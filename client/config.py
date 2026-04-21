import argparse
import os
import shutil
import subprocess
import yaml
from typing import Literal

if not os.path.isfile("settings.yaml"):
    raise Exception("settings.yaml not found")
with open("settings.yaml", mode = "r", encoding="utf-8") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

parser = argparse.ArgumentParser(description="A desktop ocr client.")
# parser.add_argument("-h", "--help", action="help", help="show this help message and exit")
parser.add_argument("-m", "--model", type=str, default="ocr", choices=["ocr", "latex"], help="choose the mode (model) to use")
args = parser.parse_args()
MODEL: Literal["ocr", "latex"] = args.model

def install_katex_env(cwd: str):
    p = subprocess.Popen(
        ["npm", "install", "katex", "jsdom"], 
        cwd=cwd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, 
        shell=True
    )
    p.wait()
    return p.returncode, p.stdout, p.stderr

class Config:
    TMP_SAVING_PATH = config.get("TMP_SAVING_PATH")
    if TMP_SAVING_PATH is None:
        TMP_SAVING_PATH = f"./out"
    if not os.path.isdir(TMP_SAVING_PATH):
        os.mkdir(TMP_SAVING_PATH)
    WORKING_DIR = os.path.join(TMP_SAVING_PATH, os.urandom(8).hex())
    if not os.path.isdir(WORKING_DIR):
        os.mkdir(WORKING_DIR)

    LOADING_GIF = "./loading.gif"
    if not os.path.isfile(LOADING_GIF):
        raise Exception("loading.gif not found")

    OCR_SERVER_API = config.get("OCR_SERVER_API")
    if OCR_SERVER_API is None:
        OCR_SERVER_API = "http://localhost:5000/ocr"
    GTTS_DEFAULT_LANG = config.get("GTTS_DEFAULT_LANG")
    if GTTS_DEFAULT_LANG is None:
        GTTS_DEFAULT_LANG = "ja"

    LATEX_OCR_SERVER_API = config.get("LATEX_OCR_SERVER_API")
    if LATEX_OCR_SERVER_API is None:
        LATEX_OCR_SERVER_API = "http://localhost:5000/texify"
    KATEX_WORKING_DIR = config.get("KATEX_WORKING_DIR")
    if KATEX_WORKING_DIR is None:
        KATEX_WORKING_DIR = "./.katex-env"
    if not os.path.isdir(KATEX_WORKING_DIR):
        os.mkdir(KATEX_WORKING_DIR)
        returncode, stdout, stderr = install_katex_env(KATEX_WORKING_DIR)
        if returncode:
            raise Exception(f"Unable to install katex: \n{stdout}\n\n{stderr}")

    @classmethod
    def delete_tmp_files(cls):
        shutil.rmtree(cls.WORKING_DIR)

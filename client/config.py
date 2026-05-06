import argparse
import os
import shutil
import yaml
from typing import Literal

parser = argparse.ArgumentParser(description="A desktop ocr client.")
# parser.add_argument("-h", "--help", action="help", help="show this help message and exit")
parser.add_argument("-c", "--config", type=str, default="settings.yaml", help="select the specific config file")
parser.add_argument("-m", "--model", type=str, default="ocr", choices=["ocr", "latex"], help="choose the mode (model) to use")
args = parser.parse_args()
MODEL: Literal["ocr", "latex"] = args.model if args.model == "ocr" else "latex"

CONFIG_YAML = args.config
if not os.path.isfile(CONFIG_YAML):
    raise Exception(f"{CONFIG_YAML} not found")
with open(CONFIG_YAML, mode = "r", encoding="utf-8") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

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

    @classmethod
    def delete_tmp_files(cls):
        shutil.rmtree(cls.WORKING_DIR)

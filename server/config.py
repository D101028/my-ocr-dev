import configparser
import os

config = configparser.ConfigParser()

config.read("config.conf")

default_section = config["DEFAULT"]
paddle_ocr_section = config["PADDLE_OCR"]
texify_section = config["TEXIFY"]

class Config:
    HOST: str
    PORT: int
    TEMP_DIR: str
    # WORKING_DIR: str
    PADDLE_OCR_ROUTE: str
    TEXIFY_ROUTE: str

    _HOST = default_section.get("HOST")
    _PORT = default_section.get("PORT")
    _TEMP_DIR = default_section.get("TEMP_DIR")

    if not _HOST:
        HOST = "localhost"
    else:
        HOST = _HOST
    if not _PORT:
        PORT = 5000
    else:
        PORT = int(_PORT)
    if not _TEMP_DIR:
        TEMP_DIR = "./temp_dir"
    else:
        TEMP_DIR = _TEMP_DIR
    if not os.path.isdir(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    # WORKING_DIR = os.path.join(TEMP_DIR, os.urandom(8).hex())
    # if not os.path.isdir(WORKING_DIR):
    #     os.mkdir(WORKING_DIR)

    _PADDLE_OCR_ROUTE = paddle_ocr_section.get("PADDLE_OCR_ROUTE")

    if not _PADDLE_OCR_ROUTE:
        PADDLE_OCR_ROUTE = "/ocr"
    else:
        PADDLE_OCR_ROUTE = _PADDLE_OCR_ROUTE

    _TEXIFY_ROUTE = texify_section.get("TEXIFY_ROUTE")

    if not _TEXIFY_ROUTE:
        TEXIFY_ROUTE = "/texify"
    else:
        TEXIFY_ROUTE = _TEXIFY_ROUTE

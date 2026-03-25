import configparser

config = configparser.ConfigParser()

config.read("config.conf")

default_section = config["DEFAULT"]
paddle_ocr_section = config["PADDLE_OCR"]
texify_section = config["TEXIFY"]

class Config:
    HOST: str
    PORT: int
    PADDLE_OCR_ROUTE: str
    TEXIFY_ROUTE: str

    _HOST = default_section.get("HOST")
    _PORT = default_section.get("PORT")

    if not _HOST:
        HOST = "localhost"
    else:
        HOST = _HOST
    if not _PORT:
        PORT = 5000
    else:
        PORT = int(_PORT)

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


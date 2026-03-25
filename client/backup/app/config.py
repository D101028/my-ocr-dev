import os
import yaml

if not os.path.isfile("settings.yaml"):
    raise Exception("settings.yaml not found")
with open("settings.yaml", mode = "r", encoding="utf-8") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

class Config:
    TMP_SAVING_PATH = config.get("TMP_SAVING_PATH")
    if TMP_SAVING_PATH is None:
        TMP_SAVING_PATH = "./out"
    if not os.path.isdir(TMP_SAVING_PATH):
        os.mkdir(TMP_SAVING_PATH)

    LOADING_GIF = "./loading.gif"
    if not os.path.isfile(LOADING_GIF):
        raise Exception("loading.gif not found")

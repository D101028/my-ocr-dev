from texify.inference import batch_inference
from texify.model.model import load_model
from texify.model.processor import load_processor
from PIL import Image

model = load_model()
processor = load_processor()
img = Image.open("out/snip_output.png") # Your image name here
results = batch_inference([img], model, processor)
print(results)
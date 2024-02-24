import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import warnings

warnings.filterwarnings("ignore")

def pretrained(hf_model="Salesforce/blip-image-captioning-large"):
    '''
    Initialize the pretrined Processor and Model to generate
    captions for images.
    Parameters:
        hf_model - The pre-trained model that we are using to generate captions.
        (Defualt: https://huggingface.co/Salesforce/blip-image-captioning-large)
    '''
    # A more lightweight alternative: "Salesforce/blip-image-captioning-base"
    processor = BlipProcessor.from_pretrained(hf_model)
    model = BlipForConditionalGeneration.from_pretrained(hf_model)
    return processor, model

def caption_text(processor, model,
                 iamge_path='static/images/howl.jpeg',image_url=None):
    if image_url:
        try:
            raw_image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
        except requests.exceptions.RequestException:
            return 'Invalid URL, Try Again'
    else:
        try:
            raw_image = Image.open(iamge_path).convert('RGB')
        except FileNotFoundError:
            return 'File Not Found, Try Again'
    # conditional image captioning
    # text = "a photography of"
    # inputs = processor(raw_image, text, return_tensors="pt")
    # out = model.generate(**inputs, max_new_tokens=50)
    # print(processor.decode(out[0], skip_special_tokens=True))

    # unconditional image captioning
    inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=50)
    txt = processor.decode(out[0], skip_special_tokens=True)

    return txt.title()
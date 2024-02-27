import requests
from PIL import Image

import torch
import scipy
from transformers import BlipProcessor, BlipForConditionalGeneration, VitsModel, AutoTokenizer
import warnings

# Ignore warnings
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
    # note: the base model is less accurate than the large model
    # hf_model = "Salesforce/blip-image-captioning-base"
    processor = BlipProcessor.from_pretrained(hf_model)
    model = BlipForConditionalGeneration.from_pretrained(hf_model)
    return processor, model


def pretrained_tts(hf_model="facebook/mms-tts-eng"):
    '''
    Initialize the pretrined Processor and Model to generate
    text-to-speech for the captions.
    Parameters:
        hf_model - The pre-trained model that we are using to generate captions.
        (Defualt: https://huggingface.co/facebook/mms-tts-eng)
    '''
    tokenizer = AutoTokenizer.from_pretrained(hf_model)
    model = VitsModel.from_pretrained(hf_model)
    return tokenizer, model

def caption_text(processor, model,
                 iamge_path='static/images/sample3.jpeg',image_url=None):
    '''
    This function takes the image and returns the caption for the image.
    Parameters:
        processor - The pre-trained processor for the model.
        model - The pre-trained model to generate captions for the image.
        iamge_path - The path of the image file.
        image_url - The url of the image file.
    Returns:
        txt.title() - The caption for the image in title case.
    '''
    if image_url:
        raw_image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
    else:
        raw_image = Image.open(iamge_path).convert('RGB')
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

def tts(tokenizer, model, text="Hello World", upload_folder='./static/audio/'):
    '''
    This function takes the text and returns the audio file path
    of the generated audio.
    Parameters:
        tokenizer - The tokenizer for the model.
        model - The pre-trained model to generate audio from text.
        text - The text that we want to convert to audio.
        upload_folder - The folder where we want to save the audio file.
    Returns:
        AUDIO_PATH - The path of the audio file.
    '''
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    AUDIO_PATH = upload_folder+"response.wav"
    scipy.io.wavfile.write(AUDIO_PATH,
                           rate=model.config.sampling_rate,
                           data=output.float().numpy().T
                           )
    return AUDIO_PATH
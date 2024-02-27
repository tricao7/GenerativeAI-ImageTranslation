import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from image_captioning import *

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the pre-trained model
processor, model = pretrained()
tts_tokenizer, tts_model = pretrained_tts()


def allowed_file(filename):
    '''Check if the file is allowed'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def home_page():
    '''This is the home page'''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('homepage.html')


@app.route('/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    '''This is the uploaded file page'''
    file_path = os.path.join('static', 'images', filename)
    # Generate Caption
    caption = caption_text(processor, model, file_path)
    # Add Audio to Caption
    audio_path = tts(tts_tokenizer, tts_model, caption)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

    return render_template('response.html', image_file=file_path, caption=caption,
                           audio_file=audio_path)


@app.route('/test')
def testing_page():
    '''This is the testing page'''
    return render_template('tester.html')

def delete_files():
    '''
    This function deletes all the files that were uploaded by
    the user.
    '''
    base_images = os.path.join('static', 'images')
    iamges = ['header_background.jpg', 'sample1.jpg',
              'sample2.jpg', 'sample3.jpeg', 'sample4.jpg']
    base_audio = os.path.join('static', 'audio')
    audio = ['sample1.wav', 'sample2.wav',
             'sample3.wav', 'sample4.wav']
    # delete images that are not in the base images
    # Note: This is to prevent user images from being saved
    for file in os.listdir(base_images):
        if file not in iamges:
            os.remove(os.path.join(base_images, file))
    # delete audio that are not in the base audio
    # Note: This is to prevent user audio from being saved
    for file in os.listdir(base_audio):
        if file not in audio:
            os.remove(os.path.join(base_audio, file))


if __name__ == "__main__":
    port = os.environ.get('PORT', 8080)
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port)
    # if the app is closed, the model, processor
    # and the files will be deleted
    delete_files()
    del processor
    del model


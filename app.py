import os
from flask import Flask, render_template, request,\
    redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

from image_to_text import *


UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
img = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# initialize the pre-trained model
processor, model = pretrained()


def allowed_file(filename):
    '''Check if the file is allowed'''
    return '.' in filename and\
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',  methods=['GET', 'POST'])
def home_page():
    '''This is the home page'''
    file = os.path.join(img, 'sample1.jpg')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # url = request.files['image_url']
        # # if user does not select file, browser also
        # # submit an empty part without filename
        # if url != '':
        #     return redirect(url_for('uploaded_file', iamge_path=url))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template('homepage.html', image_file=file)

@app.route('/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename, image_path=None):
    '''
    This is the uploaded file page
    https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
    '''
    file = os.path.join(img, filename)
    caption = caption_text(processor, model, file)

    # allow the user to perform another captioning
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template('response.html', image_file=file, caption=caption)


if __name__ == "__main__":
    app.run(debug=True, port=2000)

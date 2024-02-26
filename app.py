import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from image_to_text import pretrained, caption_text

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the pre-trained model
processor, model = pretrained()


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
    caption = caption_text(processor, model, file_path)
    
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

    return render_template('response.html', image_file=file_path, caption=caption)


@app.route('/test')
def testing_page():
    '''This is the testing page'''
    return render_template('tester.html')


if __name__ == "__main__":
    port = os.environ.get('PORT', 5000)
    base_images = os.path.join('static', 'images')
    iamges = ['header_background.jpg', 'sample1.jpg',
              'sample2.jpg', 'sample3.jpeg', 'sample4.jpg']
    # delete images taht are not in the base images
    # Note: This is to prevent user images from being saved
    for file in os.listdir(base_images):
        if file not in iamges:
            os.remove(os.path.join(base_images, file))
    app.run(debug=True, host='0.0.0.0', port=port)
    # if the app is closed, the model will be deleted
    del processor
    del model


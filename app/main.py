from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home_page(dct=None):
    '''This is the home page'''
    dct = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}
    return render_template('test.html', dct=dct)


if __name__ == "__main__":
    app.run(debug=True, port=2000)

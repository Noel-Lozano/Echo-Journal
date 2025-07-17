from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return '<h1>About Us</h1>'

@app.route('/features')
def features():
    return '<h1>Features</h1>'

@app.route('/reviews')
def reviews():
    return '<h1>Reviews</h1>'

@app.route('/contact')
def contact():
    return '<h1>Contact</h1>'

@app.route('/login')
def login():
    return '<h1>Login</h1>'

@app.route('/signup')
def signup():
    return '<h1>Sign Up</h1>'

if __name__ == '__main__':
    app.run(debug=True, port=5001)

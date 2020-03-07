from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/david")
def david():
    return "Hello, David!"

@app.route("/prasham")
def prasham():
    return "Hello Prasham"
    print("Hello Prasham")
@app.route("/bhuta")
def bhuta():
    return "Bhuta, Hi!"
    

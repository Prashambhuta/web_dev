from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    headline = "Hello,all" 
    return render_template("index.html", headline=headline)

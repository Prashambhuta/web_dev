from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    now = datetime.datetime.now()
    diwali = now.month == 10 and now.date == 28
    #diwali = True
    return render_template("index.html", diwali = diwali)
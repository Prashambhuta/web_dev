import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), pool_size=10, max_overflow=10)
db = scoped_session(sessionmaker(bind=engine))

# Default route
@app.route("/", methods=["POST", "GET"])
def index():
    # for 'get' method
    if request.method == "GET":
        try:
            if session["user_id"]:
                return redirect(url_for("search"))
        except KeyError:
            return render_template("index.html") 
        else:
        # if session["user_id"]:
        #     return render_template("index.html", session=session["user_id"])
            return render_template("index.html")        
    
# registration route
@app.route("/register", methods=["POST", "GET"])
def register():
    """ Register a new user """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username.strip(" ") != "":

            check_available_username = db.execute("SELECT * from users WHERE username=:username", {"username": username}).fetchall()
            if not check_available_username:
                # execute insertion
                db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
                db.commit()
                
                # execute selection
                user_details = db.execute("SELECT * from users WHERE username=:username and password=:password", {"username": username, "password": password}).fetchone()
                session["user_id"] = user_details[0]
                return redirect(url_for("search"))
            else:
                return render_template("error.html", error_message="Username exists. Try again with different username.")
        elif username.strip(" ") == "":
            return  render_template ("error.html", error_message ="Enter valid username & password.")
            

    elif request.method == "GET":
        render_template ("register.html")
        # return render_template("error.html",error_message="Kindly provide a username and password.")
    
    return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """ Logging in a user. """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check credentials
        check_login_credentials = db.execute("SELECT * FROM users where username= '%s' AND password= '%s'" % (username, password)).fetchone()
        if not check_login_credentials:
            return render_template("error.html", error_message="Invalid credentials.")
            return redirect(url_for("login"))
        else:
            session["user_id"] = check_login_credentials[0]
            return redirect(url_for("search"))
    else:
        return render_template("login.html")


# Logout route
@app.route("/logout", methods=["GET"])
def logout():
    """ Logging out a user """
    session.clear()
    return render_template("index.html")

# Search route
@app.route("/search", methods=["POST", "GET"])
def search():
    """ Defining the search method. """
    # check here
    if request.method == "GET":
        try:
            if session["user_id"]:
                return render_template("search.html")
        except:
            return render_template("error.html", error_message="Kindly login or register")

    if request.method == "POST":
        isbn_search = request.form.get("isbn")
        title_search = request.form.get("title")
        author_search = request.form.get("author")

        if isbn_search != "":
            result = db.execute("SELECT * FROM books WHERE isbn ~* :isbn LIMIT 10", {"isbn": isbn_search}).fetchall()
            db.commit()
            return render_template("search.html", result=result)
        elif title_search != "":
            title_search = title_search.title()
            result = db.execute("SELECT * FROM books WHERE title ~* :title LIMIT 10", {"title": title_search}).fetchall()
            db.commit()
            return render_template("search.html", result=result)
        elif author_search != "":
            author_search = author_search.title()
            result = db.execute("SELECT * FROM books WHERE author ~* :author LIMIT 10", {"author": author_search}).fetchall()
            db.commit()
            return render_template("search.html", result=result)
        else:
            return render_template("error.html", error_message="Enter valid search parameters.")

# Book route
@app.route("/book/<int:book_id>", methods=["POST", "GET"])
def book(book_id):
    """ List details about book, inc. goodreads number. """

    # cross check if books exists
    if request.method == "GET": 
        book = db.execute("SELECT * FROM books WHERE id = %s" % book_id).fetchone()

        # getting no_of_ratings & avg_rating from goodreads api
        goodreads_object = requests.get("https://goodreads.com/book/review_counts.json?", params={"key": "OmILO8KjgxHJOvvnGxDtUw", "isbns": "%s" % book.isbn})
        goodreads_data_raw = goodreads_object.json()
        goodreads_data = goodreads_data_raw['books']

        # get average rating
        avg_rating = float(goodreads_data[0]['average_rating']) 
        # get total no of reviews
        no_of_rating = goodreads_data[0]['work_ratings_count']

        # display existing user reviews
        existing_reviews = db.execute("SELECT username, rating, text from reviews INNER JOIN users ON reviews.user_id = users.id INNER JOIN books ON reviews.book_id = books.id WHERE books.id = %s" % (book_id)).fetchall()


        return render_template("book.html", result=book, avg_rating=avg_rating, no_of_rating=no_of_rating, existing_reviews=existing_reviews)
        
    elif request.method == "POST":
        user_rating = request.form.get("rating")
        user_review = request.form.get("review")

        # checking for user_id
        user_id = session["user_id"]

        # check if user_review is non None
        if user_review == "":
            return render_template("error.html", error_message="Cannot have empty fields")

        # check if previous entry exists
        else:
            get_review = db.execute("SELECT username, rating, text from reviews INNER JOIN users ON reviews.user_id = users.id INNER JOIN books ON reviews.book_id = books.id WHERE users.id = %s AND books.id = %s" % (user_id, book_id)).fetchall()

            if not get_review:
                # commit the review to database table review
                db.execute("INSERT INTO reviews (book_id, rating, text, user_id) VALUES (:book_id, :rating, :text, :user_id)", {"book_id": book_id, "rating": user_rating, "text": user_review, "user_id": user_id})
                db.commit()
                return redirect("/book/" + str(book_id))
            else:
                return render_template("error.html", error_message="You have already reviewed this book.")

        


    # adding fields for user to leave review
    else:
        return render_template("error.html", error_message="No such book found")

# api return
@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    """ API route for users """
    if isbn == "":
        return render_template("error.html", error_message="ISBN not found")

    if isbn:
        books_object = db.execute("SELECT * FROM books WHERE isbn = '%s'" % isbn).fetchone()
        if books_object:
            reviews_object = db.execute("SELECT COUNT(*), AVG(rating) FROM reviews WHERE book_id = %d" % books_object.id).fetchone()

            # converting to printable objects
            review_count = reviews_object.count
            review_average_rating = reviews_object.avg
            if review_average_rating != None:
                api_result = {
                    "title":            books_object.title,
                    "author":           books_object.author,
                    "year":             int(books_object.year),
                    "isbn":             str(isbn),
                    "review_count":     review_count,
                    "average_rating":   float('%.2f' % review_average_rating)
                }
                return (api_result)
            if review_average_rating == None:
                api_result = {
                    "title":            books_object.title,
                    "author":           books_object.author,
                    "year":             int(books_object.year),
                    "isbn":             str(isbn),
                    "review_count":     review_count,
                    "average_rating":   'N/A'
                }
                return (api_result)

        else:
            error_404 = {
                "Error":    404,
                "Type":     "ISBN NOT FOUND",
            }

            return render_template("error_404.html")
    else:
        error_404 = {
            "Error":    404,
            "Type":     "ISBN NOT FOUND",
        }

        return render_template("error_404.html")

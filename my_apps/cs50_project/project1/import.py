import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# create engine, set up db
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    csv_file = open("books.csv")
    csv_reader = csv.reader(csv_file)
    books_done = 0
    for isbn, title, author, year in csv_reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        books_done += 1
        if books_done % 50 == 0:
            print("Books done: %d" % books_done)
    db.commit()

if __name__ == "__main__":
    main()
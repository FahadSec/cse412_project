#!/usr/bin/env python3

# This is a temprary HelloWorld Flask app to test db/flask connection

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

import models

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cse412_dev"
db = SQLAlchemy(app)

@app.route("/")
def hello_world():

    # example query: print all discord server links to console
    results = db.session.execute(db.select(models.Server)).scalars()
    for r in results:
        print (r.link)

    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    db.init_app(app)
    app.run()

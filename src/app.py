#!/usr/bin/env python3

# This is a temprary HelloWorld Flask app to test db/flask connection

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

import models

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cse412_dev"
db = SQLAlchemy(app)

def search(subject, number, ext):
    results = db.session.execute(f"""
        SELECT Course.subject, Course.course_number, Course.number_ext, Course.title, Professor.name, Server.link
        FROM Section
        LEFT JOIN Discord_for on Discord_for.section_number = Section.section_number 
        LEFT JOIN Server on Server.server_id = Discord_for.server_id
        INNER JOIN Teaches on Teaches.section_number = Section.section_number
        INNER JOIN Professor on Professor.professor_id = Teaches.professor_id
        INNER JOIN Scheduled on Scheduled.section_number = Section.section_number 
        INNER JOIN Course on (Course.subject = Scheduled.subject 
            AND Course.course_number=Scheduled.course_number 
            AND Course.number_ext=Scheduled.number_ext)
        WHERE Course.subject = :subject AND Course.course_number = :number AND Course.number_ext = :ext;
    """, {
        "subject" : subject,
        "number" : number,
        "ext" : ext
        })
    return results

@app.route("/")
def hello_world():
    results = search("CSE", 412, "")
    for r in results:
        print(r)

    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    db.init_app(app)
    app.run()


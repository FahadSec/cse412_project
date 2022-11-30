#!/usr/bin/env python3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request#, url_for
import models

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cse412_dev"
db = SQLAlchemy(app)


def search(subject, number, ext):
    query = """
    SELECT Course.subject, Course.course_number, Course.number_ext, Section.section_number, Course.title, Professor.name, Server.link
        FROM Section
        LEFT JOIN Discord_for on Discord_for.section_number = Section.section_number
        LEFT JOIN Server on Server.server_id = Discord_for.server_id
        INNER JOIN Teaches on Teaches.section_number = Section.section_number
        INNER JOIN Professor on Professor.professor_id = Teaches.professor_id
        INNER JOIN Scheduled on Scheduled.section_number = Section.section_number
        INNER JOIN Course on (Course.subject = Scheduled.subject
            AND Course.course_number=Scheduled.course_number
            AND Course.number_ext=Scheduled.number_ext)
        WHERE 
    """
    if subject:
        query += ' Course.subject = :subject AND'
    if number:
        query += ' Course.course_number = :number AND'
    if ext:
        query += ' Course.number_ext = :ext AND'
    query += ' TRUE;'
    results = db.session.execute(query,
        {
        "subject" : subject,
        "number" : number,
        "ext" : ext
        })
    return results


@app.route("/")
def index() -> str:
    # results = search("CSE", 412, "")
    return render_template('index.html')

@app.route("/",  methods =["GET", "POST"])
def search_page():
    if request.method == "POST":
        subject = request.form.get("subject")
        number = request.form.get("number")
        ext = ''
        if number!='':
            if len(number) > 3:
                ext = number[3:]
                number = number[:3]
        
        print(subject,number,ext)
        results = search(subject, number, ext)
        if number is None: number = ''
        if subject is None: subject = ''
        if ext is None: ext = ''
        return render_template("index.html", rows=results, subject=subject, number=number, ext=ext)
    return render_template("index.html", rows=())

"""
    for r in results:
        print(r)

    #x = models.Server.query.all() 
    x = db.session.execute(db.select(models.Server)).scalars()

    print(results[0])
    
    for r in x:
        print(r)
"""


def main() -> None:
    db.init_app(app)
    app.run(debug=True, host='localhost', port=5000)


if __name__ == "__main__":
    main()

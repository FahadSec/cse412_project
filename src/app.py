#!/usr/bin/env python3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request
import models

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cse412_dev"
app.config['SECRET_KEY'] = 'secret_lol'
db = SQLAlchemy(app)

def insert_server(section_number, server_link):
    r0 = db.session.execute("""
    SELECT link FROM Server WHERE link=:link;
    """, {"link":server_link})
    print("R0", r0)
    print("is none?", (r0 is None))
    if r0 is None:
        r1 = db.session.execute("""
        INSERT INTO Server (link) VALUES (:link) ;
        """, { "link":server_link})
    try:
        results = db.session.execute("""
        INSERT INTO Discord_For (server_id, section_number) VALUES
        ((SELECT server_id FROM Server WHERE link=:link), :section);
        """,
        {"section":section_number,
        "link":server_link
        })
    except:
        db.session.commit()
        return None
    db.session.commit()
    return results

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

@app.route("/modal")
def modal():
    return render_template("modal.html")

@app.route("/submit")
def submit():
    section_number = request.args.get('section_number', None)
    link = request.args.get('link', None)
    subject = request.args.get('subject', None)
    course_number  = request.args.get('course_number', None)
    ext = request.args.get('ext', None)

    new_server = models.Server(link)
    db.session.add(new_server)
    db.session.commit()

    server_for = models.DiscordFor(new_server.server_id, section_number) 
    db.session.add(server_for)
    db.session.commit()

    results = search(subject, course_number, ext)
    return render_template("index.html", rows=results, subject=subject, number=course_number, ext=ext)

@app.route("/")
def index() -> str:


    #print("Hello World")
    #r1 = insert_server(78141, "testlink")
    # results = search("CSE", 355, "")
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


def main() -> None:
    db.init_app(app)
    app.run(debug=True, host='localhost', port=5000)


if __name__ == "__main__":
    main()

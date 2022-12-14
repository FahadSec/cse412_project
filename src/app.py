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


def search(subject=None, number=None, ext=None, term=None, session=None, min_credits=None, max_credits=None, professor_name=None, seats=None):
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
        subject = subject.upper()
    if number:
        query += ' Course.course_number = :number AND'
    if ext:
        query += ' Course.number_ext = :ext AND'
    if term:
        query += ' Section.semester = :term AND'
    if session:
        query += ' Section.session = :session AND'
    if min_credits:
        query += ' Course.credits >= :min_credits AND'
    if max_credits:
        query += ' Course.credits <= :max_credits AND'
    if professor_name:
        query += ' Professor.name = :prof_name AND'
    if seats:
        query += ' Section.open_seats >= :seats AND'

    query += ' TRUE;'
    results = db.session.execute(query,
        {
        "subject" : subject,
        "number" : number,
        "ext" : ext,
        "term": term,
        "session":session,
        "min_credits":min_credits,
        "max_credits":max_credits,
        "prof_name": professor_name,
        "seats": seats,

        })
    return results

@app.route("/modal", methods=["GET", "POST"])
def modal():
    if request.method == "POST":
        subject = request.args.get('subject', None)
        course_number  = request.args.get('course_number', None)
        section_number = request.args.get('section_number', None)
        a = request.form.keys()
        sections = []
        for key in a:
            sections.append(int(key.split('_')[1]))
        ext = request.args.get('ext', None)
        return render_template("modal.html", subject=subject, course_number=course_number, section_number=section_number, sections=sections, ext=ext)

@app.route("/bot")
def bot():
    subject = request.args.get('subject', None)
    course_number  = request.args.get('course_number', None)
    section_number = request.args.get('section_number', None)
    server_id= request.args.get('server_id', None)
    ext = request.args.get('ext', None)
    return render_template("bot.html", subject=subject, course_number=course_number, section_number=section_number, ext=ext, server_id=server_id)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        section_number = request.args.get('section_number', None)
        subject = request.args.get('subject', None)
        course_number  = request.args.get('course_number', None)
        ext = request.args.get('ext', None)
        sections = request.args.getlist('sections')
        link = request.form.get('link')

        new_server = models.Server(link.split("discord.gg/")[-1])
        db.session.add(new_server)
        db.session.commit()

        for section in sections:
            server_for = models.DiscordFor(new_server.server_id, section)
            db.session.add(server_for)
        db.session.commit()

        results = search(subject, course_number, ext)
        return render_template("bot.html", subject=subject, course_number=course_number, section_number=section_number, ext=ext, server_id=new_server.server_id)
    return None


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

        results = search(subject, number, ext)
        if number is None: number = ''
        if subject is None: subject = ''
        if ext is None: ext = ''
        return render_template("index.html", rows=results, subject=subject, number=number, ext=ext)

    subject = request.args.get('subject', None)
    number  = request.args.get('number', None)
    ext = request.args.get('ext', None)
    if (subject is not None):
        results = search(subject, number, ext)
    else:
        results = ()
    if number is None: number = ''
    if subject is None: subject = ''
    if ext is None: ext = ''
    return render_template("index.html", rows=results, subject=subject, number=number, ext=ext)


def main() -> None:
    db.init_app(app)
    app.run(debug=True, host='localhost', port=5000)

if __name__ == "__main__":
    main()

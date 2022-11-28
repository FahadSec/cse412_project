#!/usr/bin/env python3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template#, url_for

import models

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cse412_dev"
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
def search(subject, number, ext):
    results = db.session.execute("""
        SELECT Course.subject, Course.course_number, Course.number_ext, Course.title, Professor.name, Server.link, Section.section_number
        FROM Section
        LEFT JOIN Discord_for on Discord_for.section_number = Section.section_number 
        LEFT JOIN Server on Server.server_id = Discord_for.server_id
        INNER JOIN Teaches on Teaches.section_number = Section.section_number
        INNER JOIN Professor on Professor.professor_id = Teaches.professor_id
        INNER JOIN Scheduled on Scheduled.section_number = Section.section_number 
        INNER JOIN Course on (Course.subject = Scheduled.subject 
            AND Course.course_number=Scheduled.course_number 
            AND Course.number_ext=Scheduled.number_ext)
        WHERE Course.subject = :subject AND Course.course_number = :number AND Course.number_ext = :ext;""", 
        {
        "subject" : subject,
        "number" : number,
        "ext" : ext
        })
    return results

@app.route("/")
def index() -> str:
    r1 = insert_server(78141, "testlink")
    results = search("CSE", 355, "")

    for r in results:
        print(r)

    results = db.session.execute("""SELECT * FROM Server;""")
    for r in results:
        print(r)
    
    

    return render_template('index.html')

def main() -> None:
    db.init_app(app)
    app.run(debug=True, host='localhost', port=5000)

if __name__ == "__main__":
    main()

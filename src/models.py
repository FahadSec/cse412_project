from app import db


class Server(db.Model):
    __tablename__ = "server"
    server_id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(150), nullable=False)
    member_count = db.Column(db.Integer)

    def __init__(self, link, member_count):
        self.link = link
        self.member_count = member_count


class Course(db.Model):
    __tablename__ = "course"
    subject = db.Column(db.CHAR(3), primary_key=True)
    course_number = db.Column(db.SmallInteger, primary_key=True)
    number_ext = db.Column(db.String(8), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.SmallInteger)
    general_studies = db.Column(db.String(20))
    description = db.Column(db.Text())

    def __init__(self, subject, course_number, number_ext, title, credits, general_studies, description):
        self.subject = subject
        self.course_number = course_number
        self.number_ext = number_ext
        self.title = title
        self.credits = credits
        self.general_studies = general_studies
        self.description = description


class Section(db.Model):
    __tablename__ = "section"
    section_number = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(25))
    semester = db.Column(db.String(30), nullable=False)
    session = db.Column(db.String(8), nullable=False)
    open_seats = db.Column(db.Integer)

    def __init__(self, section_number, location, semester, session, open_seats):
        self.section_number = section_number
        self.location = location
        self.semester = semester
        self.session = session
        self.open_seats = open_seats


class Discord_for(db.Model):
    __tablename__ = "discord_for"
    server_id = db.Column(db.Integer, db.ForeignKey("Server.server_id"), primary_key=True)
    section_number = db.Column(db.Integer, db.ForeignKey("Section.section_number"), primary_key=True)

    def __init__(self, server_id, section_number):
        self.server_id = server_id
        self.section_number = section_number


class Professor(db.Model):
    __tablename__ = "professor"
    professor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(35))
    phone_number= db.Column(db.String(14))
    bio= db.Column(db.Text())
    website= db.Column(db.String(80))

    def __init__(self, professor_id, name, email, phone_number, bio, website):
        self.professor_id = professor_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.bio = bio
        self.website = website


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    asu_email = db.Column(db.String(35))
    discord_id = db.Column(db.String(35))

    def __init__(self, name, asu_email, discord_id):
        self.name = name
        self.asu_email = asu_email
        self.discord_id = discord_id


class Enrolled(db.Model):
    __tablename__ = "enrolled"
    student_id = db.Column(db.Integer, db.ForeignKey("Student.student_id"), primary_key=True)
    section_number = db.Column(db.Integer, db.ForeignKey("Section.section_number"), primary_key=True)

    def __init__(self, student_id, section_number):
        self.student_id = student_id
        self.section_number = section_number


class Joined(db.Model):
    __tablename__ = "joined"
    student_id = db.Column(db.Integer, db.ForeignKey("Student.student_id"), primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey("Server.server_id"), primary_key=True)
    role = db.Column(db.String(8))

    def __init__(self, student_id, server_id):
        self.student_id = student_id
        self.server_id = server_id


class Scheduled(db.Model):
    __tablename__ = "scheduled"
    subject = db.Column(db.CHAR(3), db.ForeignKey("Course.subject"), nullable=False)
    course_number = db.Column(db.SmallInteger, db.ForeignKey("Course.course_number"), nullable=False)
    number_ext = db.Column(db.String(8), db.ForeignKey("Course.number_ext"))
    section_number = db.Column(db.Integer, db.ForeignKey("Section.section_number"), primary_key=True)

    def __init__(self, subject, course_number, number_ext, section_number):
        self.subject = subject
        self.course_number = course_number
        self.number_ext = number_ext
        self.section_number = section_number


class Teaches(db.Model):
    __tablename__ = "teaches"
    professor_id = db.Column(db.Integer, db.ForeignKey("Professor.professor_id"), nullable=False)
    section_number = db.Column(db.Integer, db.ForeignKey("Section.section_number"), primary_key=True)

    def __init__(self, professor_id, section_number):
        self.professor_id = professor_id
        self.section_number = section_number

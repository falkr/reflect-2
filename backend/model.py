from sqlalchemy import JSON
from database import Base
from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKeyConstraint, Table

enum_values = Enum("lecturer", "teaching assistant", "student", name="enrollment_roles")

# Course question (specify a relationship between a course and a question)


class User(Base):
    __tablename__ = "users"

    email = Column(String, unique=True, primary_key=True)
    enrollments = relationship("Enrollment", back_populates="user")
    reflections = relationship("Reflection", back_populates="user")
    admin = Column(Boolean, default=False)


class Course(Base):
    __tablename__ = "courses"

    name = Column(String, default="")
    id = Column(String, primary_key=True)
    semester = Column(String, primary_key=True)
    responsible = Column(String, default="")
    website = Column(String, default="")
    units = relationship("Unit", back_populates="course")
    reports = relationship("Report", back_populates="course")
    users = relationship("Enrollment", back_populates="course")
    questions = relationship(
        "Question", secondary="course_question", back_populates="courses"
    )


class Enrollment(Base):
    __tablename__ = "enrollment"

    user_email = Column(String, ForeignKey("users.email"), primary_key=True)
    course_id = Column(String, primary_key=True)
    course_semester = Column(String, primary_key=True)
    role = Column(enum_values, primary_key=False)
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="users")
    __table_args__ = (
        ForeignKeyConstraint(
            [course_id, course_semester], [Course.id, Course.semester]
        ),
        {},
    )


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    date_available = Column(Date)
    course_id = Column(String)
    course_semester = Column(String)
    __table_args__ = (
        ForeignKeyConstraint(
            [course_id, course_semester], [Course.id, Course.semester]
        ),
        {},
    )
    course = relationship("Course", back_populates="units")
    reflections = relationship("Reflection", back_populates="unit")
    reports = relationship("Report", back_populates="unit")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    question = Column(String)
    comment = Column(String)
    courses = relationship(
        "Course", secondary="course_question", back_populates="questions"
    )


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True)
    body = Column(String)
    timestamp = Column(Date)
    category = Column(String)
    is_interesting = Column(Boolean)
    is_problematic = Column(Boolean)
    is_sorted = Column(Boolean)
    user_id = Column(String, ForeignKey("users.email"))
    user = relationship("User", back_populates="reflections")
    unit_id = Column(Integer, ForeignKey("units.id"))
    unit = relationship("Unit", back_populates="reflections")
    question_id = Column(Integer, ForeignKey("questions.id"))


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    report_content = Column(JSON)

    unit_id = Column(Integer, ForeignKey("units.id"))
    unit = relationship("Unit", back_populates="reports")

    course_id = Column(String)
    course_semester = Column(String)
    __table_args__ = (
        ForeignKeyConstraint(
            [course_id, course_semester], [Course.id, Course.semester]
        ),
        {},
    )
    course = relationship("Course", back_populates="reports")


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True)
    email = Column(String, primary_key=False)
    course_id = Column(String)
    course_semester = Column(String)
    __table_args__ = (
        ForeignKeyConstraint(
            [course_id, course_semester], [Course.id, Course.semester]
        ),
        {},
    )
    role = Column(String, primary_key=False)


class CourseQuestion(Base):
    __tablename__ = "course_question"
    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    course_id = Column(String, primary_key=True)
    course_semester = Column(String, primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint(
            [course_id, course_semester], [Course.id, Course.semester]
        ),
        {},
    )

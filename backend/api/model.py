from sqlalchemy import JSON
from .database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, class_mapper
from sqlalchemy.schema import ForeignKeyConstraint
from datetime import date

enum_values = Enum("lecturer", "teaching assistant", "student", name="enrollment_roles")


class User(Base):
    __tablename__ = "users"

    uid = Column(String, unique=True, primary_key=True)
    email = Column(String, unique=False, primary_key=False)
    enrollments = relationship("Enrollment", back_populates="user")
    reflections = relationship("Reflection", back_populates="user")
    admin = Column(Boolean, default=False)

    def __init__(self, uid, email, admin):
        self.uid = uid
        self.email = email
        self.admin = admin


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

    uid = Column(String, ForeignKey("users.uid"), primary_key=True)
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
    hidden = Column(Boolean, default=False)
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
    reflections_since_last_report = Column(Integer, default=0)
    reports = relationship("Report", back_populates="unit")

    # Has its own to_dict method to include the number of reflections since last report
    def to_dict(self):
        unique_user_ids = {reflection.user_id for reflection in self.reflections}
        return {
            "total_reflections": len(unique_user_ids),
            **{
                c.key: getattr(self, c.key)
                for c in class_mapper(self.__class__).columns
            },
        }


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
    user_id = Column(String, ForeignKey("users.uid"))
    user = relationship("User", back_populates="reflections")
    unit_id = Column(Integer, ForeignKey("units.id"))
    unit = relationship("Unit", back_populates="reflections")
    question_id = Column(Integer, ForeignKey("questions.id"))


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    report_content = Column(JSON)

    number_of_answers = Column(Integer, default=0)

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

    """ def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in class_mapper(self.__class__).columns
        } """

    # Has its own so that Summary get moved to the top level of the dict
    # This also makes it easier to serialize the object to JSON
    def to_dict(self):
        report_content = self.report_content.copy()  # Create a copy of report_content
        summary = report_content.pop("Summary", None)

        return {
            "Summary": summary,
            **{
                "number_of_answers": self.number_of_answers,
                "report_content": report_content,
                "unit_id": self.unit_id,
                "id": self.id,
                "course_id": self.course_id,
                "course_semester": self.course_semester,
            },
        }


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True)
    uid = Column(String, primary_key=False)
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


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    sent_at = Column(Date, default=date.today)


class UserUnitNotificationCount(Base):
    __tablename__ = "user_unit_notification_counts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, ForeignKey("users.uid"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    notification_count = Column(Integer, default=0, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "unit_id", name="_user_unit_uc"),)

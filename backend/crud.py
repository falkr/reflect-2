from datetime import datetime

import model
import schemas
from sqlalchemy.orm import Session
from sqlalchemy import delete


from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List


# --- User ---
def get_user(db: Session, user_email: str):
    return db.query(model.User).filter(model.User.email == user_email).first()


# Creates user from email address
def create_user(db: Session, user_email: str):
    db_user = model.User(email=user_email)
    print("creating user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Enrolls user in a course
def create_enrollment(
    db: Session, user_email: str, course_id: str, course_semester: str, role: str
):
    # getting student
    db_user = get_user(db, user_email=user_email)
    # getting course
    db_course = get_course(db, course_id=course_id, course_semester=course_semester)
    # Creating enrollment
    db_enrollment = model.Enrollment(
        user_email=user_email,
        course_id=course_id,
        course_semester=course_semester,
        role=role,
    )
    print("Creating enrollment")
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    db.refresh(db_user)
    db.refresh(db_course)
    return db_enrollment


# --- Course ---
# Creates course
def create_course(db: Session, course: schemas.CourseCreate):
    db_course = model.Course(**course)
    questions = [
        create_question(
            db=db,
            question="Teaching",
            comment="What did you learn in this unit? What was your best learning achievement?",
        ),
        create_question(
            db=db,
            question="Difficult",
            comment="What was difficult in this unit? Was there a concept that you struggled with the most, or something that you found unclear?",
        ),
    ]
    for q in questions:
        db_course.questions.append(q)
    print("creating course")
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_course(db: Session, course_id: str, course_semester: str):
    return (
        db.query(model.Course)
        .filter(model.Course.id == course_id, model.Course.semester == course_semester)
        .first()
    )


# --- Enrollment ---


def get_enrollment(db: Session, course_id: str, course_semester: str, user_email: str):
    return (
        db.query(model.Enrollment)
        .filter(
            model.Enrollment.course_id == course_id,
            model.Enrollment.course_semester == course_semester,
            model.Enrollment.user_email == user_email,
        )
        .first()
    )


# --- Unit ---
# create unit
def create_unit(
    db: Session,
    title: str,
    date_available: str,
    course_id: str,
    course_semester: str,
):
    print("creating unit")
    db_obj = model.Unit(
        title=title,
        date_available=date_available,
        course_id=course_id,
        course_semester=course_semester,
    )

    db.add(db_obj)

    db.commit()
    db.refresh(db_obj)

    new_unit = (
        db.query(model.Unit)
        .filter(
            model.Unit.title == title and model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
        )
        .first()
    )
    report_obj = model.Report(
        report_content=[],
        course_id=course_id,
        course_semester=course_semester,
        unit_id=new_unit.id,
    )
    db.add(report_obj)
    db.commit()
    db.refresh(report_obj)
    return db_obj


def get_unit(db: Session, unit_id: int):
    return db.query(model.Unit).filter(model.Unit.id == unit_id).first()


def get_units(db: Session, course_id: int, course_semester):
    return (
        db.query(model.Unit)
        .filter(
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
        )
        .all()
    )


def update_unit_hidden(db: Session, unit_id: int, hidden: bool):
    unit = get_unit(db, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    setattr(unit, "hidden", hidden)
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


def create_question(db: Session, question: str, comment: str):
    db_obj = model.Question(question=question, comment=comment)
    print("creating question")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- Reflection ---
def create_reflection(db: Session, reflection: schemas.ReflectionCreate):
    db_obj = model.Reflection(**reflection, timestamp=datetime.now())
    print("creating reflection")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_reflections(db: Session, user_id: str, unit_id: int):
    return (
        db.query(model.Reflection)
        .filter(model.Reflection.user_id == user_id)
        .filter(model.Reflection.unit_id == unit_id)
        .all()
    )


# --- Invitation ---
def create_invitation(db: Session, invitation: schemas.InvitationBase):
    db_obj = model.Invitation(**invitation)
    print("creating invitation")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_invitations(db: Session, email: str):
    return db.query(model.Invitation).filter(model.Invitation.email == email).all()


def get_priv_invitations_course(
    db: Session, email: str, course_id: str, course_semester: str
):
    return (
        db.query(model.Invitation)
        .filter(
            model.Invitation.email == email,
            model.Invitation.course_id == course_id,
            model.Invitation.course_semester == course_semester,
            model.Invitation.role != "student",
        )
        .all()
    )


def delete_invitation(db: Session, id: int):
    invitation = db.query(model.Invitation).filter(model.Invitation.id == id).first()
    if invitation:
        db.delete(invitation)
        db.commit()
        return invitation
    else:
        raise HTTPException(status_code=404, detail="Invitation not found")


def get_number_of_unit_questions(db: Session, unit_id: int):
    return (
        db.query(model.Course.units)
        .filter(model.Unit.id == unit_id)
        .filter(model.Course.questions)
        .count()
    )


# --- Report ---
def create_report(db: Session, report: schemas.ReportCreate):
    existing_report = (
        db.query(model.Report)
        .filter(
            model.Report.course_id == report.get("course_id"),
            model.Report.unit_id == report.get("unit_id"),
        )
        .first()
    )

    if existing_report:
        existing_report.report_content = report.get("report_content")
        existing_report.number_of_answers = report.get("number_of_answers")
        db_obj = existing_report
    else:
        db_obj = model.Report(**report)
        db.add(db_obj)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_report(db: Session, course_id: str, unit_id: int):
    return (
        db.query(model.Report)
        .filter(model.Report.unit_id == unit_id)
        .filter(model.Report.course_id == course_id)
        .first()
    )


def edit_created_report(
    db: Session, course_id: int, unit_id: int, report: list[dict], course_semester: str
):

    db_obj = (
        db.query(model.Report)
        .filter(model.Report.course_id == course_id)
        .filter(model.Report.course_semester == course_semester)
        .filter(model.Report.unit_id == unit_id)
        .first()
    )
    if db_obj:
        db_obj.report_content = report

    db.commit()
    db.refresh(db_obj)
    return db_obj

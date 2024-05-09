from datetime import date, datetime, timedelta
from fastapi import HTTPException

from . import model
from . import schemas
from sqlalchemy.orm import Session
from sqlalchemy import not_
from starlette.config import Config

config = Config(".env")

# --- User ---


# Returns user based on uid
def get_user(db: Session, uid: str):
    return db.query(model.User).filter(model.User.uid == uid).first()


# Returns all units for a course
def get_units_for_course(db: Session, course_id: str, course_semester: str):
    return (
        db.query(model.Unit)
        .filter(
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
        )
        .all()
    )


# Creates user from email
def create_user(db: Session, uid: str, user_email: str, admin: bool = False):
    print("creating user")
    # For developers, we can create an admin user
    if uid in config("DEVELOPERS", cast=str, default="").split(","):
        print("Developer user detected")
        admin = True
    db_user = model.User(uid=uid, email=user_email, admin=admin)
    print("creating user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Enrolls user in a course
async def create_enrollment(
    db: Session, uid: str, course_id: str, course_semester: str, role: str
):
    db_user = get_user(db, uid)
    db_course = get_course(db, course_id, course_semester)
    db_enrollment = model.Enrollment(
        uid=uid,
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


# Deletes a student's enrollment from a course
def delete_enrollment(db: Session, uid: str, course_id: str, course_semester: str):
    enrollment = (
        db.query(model.Enrollment)
        .filter(
            model.Enrollment.uid == uid,
            model.Enrollment.course_id == course_id,
            model.Enrollment.course_semester == course_semester,
        )
        .first()
    )
    if enrollment:
        db.delete(enrollment)
        db.commit()
        return enrollment
    else:
        raise HTTPException(status_code=404, detail="Enrollment not found")


# --- Course ---


# Creates course
def create_course(db: Session, course: schemas.CourseCreate):
    course_data = {key: value for key, value in course.items() if key != "questions"}
    db_course = model.Course(**course_data)

    questions = []
    if len(course["questions"]) == 0:
        questions = [
            create_question(
                db=db,
                question="Teaching",
                comment="What was your best learning success in this unit? Why?",
            ),
            create_question(
                db=db,
                question="Difficult",
                comment="What was your least understood concept in this unit? Why?",
            ),
        ]
    else:
        for q in course["questions"]:
            questions.append(
                create_question(db=db, question=q["question"], comment=q["comment"])
            )

    for q in questions:
        db_course.questions.append(q)

    print("Creating course")
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


# Returns course based on course_id and course_semester
def get_course(db: Session, course_id: str, course_semester: str):
    return (
        db.query(model.Course)
        .filter(model.Course.id == course_id, model.Course.semester == course_semester)
        .first()
    )


# Deletes from database
def delete_records(db: Session, model, filters):
    records = db.query(model).filter(*filters).all()
    for record in records:
        db.delete(record)
    db.commit()


# Deletes course from database, inlcuding all related records such as enrollments, units, invitations, and questions
def delete_course(db: Session, course_id: str, course_semester: str):
    delete_records(
        db,
        model.Enrollment,
        [
            model.Enrollment.course_id == course_id,
            model.Enrollment.course_semester == course_semester,
        ],
    )
    delete_records(
        db,
        model.Unit,
        [
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
        ],
    )
    delete_records(
        db,
        model.Invitation,
        [
            model.Invitation.course_id == course_id,
            model.Invitation.course_semester == course_semester,
        ],
    )
    delete_records(db, model.Question, [~model.Question.courses.any()])

    course = get_course(db, course_id, course_semester)
    if course:
        db.delete(course)
        db.commit()
        return course
    else:
        raise HTTPException(status_code=404, detail="Course not found")


# --- Enrollment ---


# Returns enrollment for a course based on course_id, course_semester, and uid
def get_enrollment(db: Session, course_id: str, course_semester: str, uid: str):
    return (
        db.query(model.Enrollment)
        .filter(
            model.Enrollment.course_id == course_id,
            model.Enrollment.course_semester == course_semester,
            model.Enrollment.uid == uid,
        )
        .first()
    )


# --- Unit ---


# Creates an unit
def create_unit(
    db: Session,
    title: str,
    date_available: str,
    course_id: str,
    course_semester: str,
):
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


# Updates an unit
def update_unit(
    db: Session,
    unit_id: int,
    title: str,
    date_available: str,
    course_id: str,
    course_semester: str,
):
    db_obj = db.query(model.Unit).filter(model.Unit.id == unit_id).first()
    if db_obj:
        db_obj.title = title
        db_obj.date_available = date_available
        db_obj.course_id = course_id
        db_obj.course_semester = course_semester
        db_obj.unit_id = unit_id

        db.commit()
        db.refresh(db_obj)
        return db_obj
    else:
        raise HTTPException(status_code=404, detail="Unit not found")


# Deletes an unit
def delete_unit(db: Session, unit_id: int, course_id: str, course_semester: str):
    reflections = (
        db.query(model.Reflection).filter(model.Reflection.unit_id == unit_id).all()
    )
    report = get_report(db, course_id, unit_id, course_semester)
    unit = db.query(model.Unit).filter(model.Unit.id == unit_id).first()

    for reflection in reflections:
        db.delete(reflection)
    if report:
        db.delete(report)
    if unit:
        db.delete(unit)
        db.commit()
        return unit
    else:
        raise HTTPException(status_code=404, detail="Unit not found")


# Returns a single unit based on unit_id
def get_unit(db: Session, unit_id: int):
    return db.query(model.Unit).filter(model.Unit.id == unit_id).first()


# Returns multiple units that belongs to a course based on course_id, course_semester
def get_units(db: Session, course_id: int, course_semester):
    return (
        db.query(model.Unit)
        .filter(
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
        )
        .all()
    )


# Returns all units
def get_all_units(db: Session):
    return db.query(model.Unit).all()


# Returns all units that are available, regardless of course
def get_all_available_units(db: Session):
    current_date = datetime.utcnow().date()
    return db.query(model.Unit).filter(model.Unit.date_available <= current_date).all()


# Creates a question that will be used in a unit reflection
def create_question(db: Session, question: str, comment: str):
    db_obj = model.Question(question=question, comment=comment)
    print("Creating question")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- Reflection ---


# Creates a reflection
def create_reflection(db: Session, reflection_data: dict):
    db_obj = model.Reflection(**reflection_data, timestamp=datetime.now())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Check if a reflection with the same unit_id and user_id already exists
    existing_reflection_count = (
        db.query(model.Reflection)
        .filter(
            model.Reflection.unit_id == reflection_data["unit_id"],
            model.Reflection.user_id == reflection_data["user_id"],
        )
        .count()
    )

    # Increment reflections_since_last_report for the unit if this is the first reflection of its kind
    if existing_reflection_count == 1:  # Includes the reflection we just added
        unit = (
            db.query(model.Unit)
            .filter(model.Unit.id == reflection_data["unit_id"])
            .first()
        )
        if unit:
            unit.reflections_since_last_report += 1
            db.commit()

    return db_obj


# Resets the reflections count for a unit
def reset_reflections_count(db: Session, unit_id: int):
    unit = db.query(model.Unit).filter(model.Unit.id == unit_id).first()
    if unit:
        unit.reflections_since_last_report = 0
        db.commit()
        print("Reflections count reset for Unit ID:", unit_id)
        return unit
    else:
        print("Unit not found with ID:", unit_id)
        return None


# Deletes a reflection the database
def delete_reflection(db: Session, user_id: str, unit_id: int):
    reflections = (
        db.query(model.Reflection)
        .filter(
            model.Reflection.user_id == user_id, model.Reflection.unit_id == unit_id
        )
        .all()
    )

    if not reflections:
        raise HTTPException(status_code=404, detail="Reflections not found")

    for reflection in reflections:
        db.delete(reflection)
    db.commit()
    return {"user_id": user_id, "unit_id": unit_id}


# --- Invitation ---


# Creates an invitation
def create_invitation(db: Session, invitation: schemas.InvitationBase):
    db_obj = model.Invitation(**invitation)
    print("creating invitation")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# Returns all invitations that match the uid
def get_invitations(db: Session, uid: str):
    return db.query(model.Invitation).filter(model.Invitation.uid == uid).all()


# TODO
def get_priv_invitations_course(
    db: Session, uid: str, course_id: str, course_semester: str
):
    return (
        db.query(model.Invitation)
        .filter(
            model.Invitation.uid == uid,
            model.Invitation.course_id == course_id,
            model.Invitation.course_semester == course_semester,
            model.Invitation.role != "student",
        )
        .all()
    )


# Deletes an invitation to a course
def delete_invitation(db: Session, id: int):
    invitation = db.query(model.Invitation).filter(model.Invitation.id == id).first()
    if invitation:
        db.delete(invitation)
        db.commit()
        return invitation
    else:
        raise HTTPException(status_code=404, detail="Invitation not found")


# Returns the number of questions in a unit
def get_number_of_unit_questions(db: Session, unit_id: int):
    return (
        db.query(model.Course.units)
        .filter(model.Unit.id == unit_id)
        .filter(model.Course.questions)
        .count()
    )


# Returns a question used in a unit reflection
def get_question(db: Session, question_id: int):
    return db.query(model.Question).filter(model.Question.id == question_id).first()


# Returns a boolean indicating if a user has already reflected on a spesific question in a spesific unit
def user_already_reflected_on_question(
    db: Session, unit_id: int, user_id: int, question_id
):
    existing_reflection = (
        db.query(model.Reflection)
        .filter(
            model.Reflection.unit_id == unit_id,
            model.Reflection.user_id == user_id,
            model.Reflection.question_id == question_id,
        )
        .first()
    )

    return existing_reflection is not None


# Returns a report based on course_id, unit_id, and course_semester
def get_report(db: Session, course_id: str, unit_id: int, course_semester: str):
    return (
        db.query(model.Report)
        .filter(model.Report.unit_id == unit_id)
        .filter(model.Report.course_id == course_id)
        .filter(model.Report.course_semester == course_semester)
        .first()
    )


# Saves or updates a report in the database
def save_report(db: Session, report: schemas.ReportCreate) -> model.Report:
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


# Checks if a notification has been sent within a specified cooldown period
def check_recent_notification(db: Session, cooldown_days: int) -> bool:
    cooldown_date = datetime.utcnow().date() - timedelta(days=cooldown_days)
    return (
        db.query(model.NotificationLog)
        .filter(model.NotificationLog.sent_at > cooldown_date)
        .first()
        is not None
    )


# Creates a new notification log entry in the database with the current UTC time
def create_notification_log(db: Session):
    new_log = model.NotificationLog(sent_at=datetime.utcnow())

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


# Adds a notification count for a specific user and unit
def add_notification_count(db: Session, user_id: str, unit_id: int):
    notification_entry = (
        db.query(model.UserUnitNotificationCount)
        .filter_by(user_id=user_id, unit_id=unit_id)
        .first()
    )

    if notification_entry:
        notification_entry.notification_count += 1
    else:
        notification_entry = model.UserUnitNotificationCount(
            user_id=user_id, unit_id=unit_id, notification_count=1
        )
        db.add(notification_entry)

    db.commit()

    return notification_entry


# Retrieves the notification count for a specific user and unit
def get_notification_count(db: Session, user_id: str, unit_id: int) -> int:
    notification_entry = (
        db.query(model.UserUnitNotificationCount)
        .filter_by(user_id=user_id, unit_id=unit_id)
        .first()
    )

    if notification_entry:
        return notification_entry.notification_count
    else:
        return 0


# Retrieves all courses from the database
def get_all_courses(db: Session):
    return db.query(model.Course).all()


# Retrieves all students enrolled in a specific course and semester
def get_all_students_in_course(db: Session, course_id: str, course_semester: str):
    users_in_course = (
        db.query(model.User)
        .join(model.Enrollment)
        .filter(
            model.Enrollment.course_id == course_id,
            model.Enrollment.course_semester == course_semester,
            model.Enrollment.role == "student",
        )
        .all()
    )

    return users_in_course


# Retrieves units for which a user should be notified, based on a specific course and semester
def get_units_to_notify(
    db: Session,
    user_id: str,
    notification_limit: int,
    course_id: str,
    course_semester: str,
):
    subquery = (
        db.query(model.Reflection.unit_id)
        .filter(
            model.Reflection.unit_id == model.Unit.id,
            model.Reflection.user_id == user_id,
        )
        .exists()
    )

    available_units = (
        db.query(model.Unit)
        .filter(
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
            model.Unit.hidden == False,
            model.Unit.date_available <= date.today(),
            not_(subquery),
        )
        .all()
    )

    units_to_notify = []
    for unit in available_units:
        notification_count = (
            db.query(model.UserUnitNotificationCount)
            .filter(
                model.UserUnitNotificationCount.user_id == user_id,
                model.UserUnitNotificationCount.unit_id == unit.id,
            )
            .first()
        )

        if (
            not notification_count
            or notification_count.notification_count < notification_limit
        ):
            units_to_notify.append(unit)

    return units_to_notify

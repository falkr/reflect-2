from datetime import date, datetime, timedelta
from fastapi import HTTPException

from . import model
from . import schemas
from sqlalchemy.orm import Session


# --- User ---
def get_user(db: Session, uid: str):
    return db.query(model.User).filter(model.User.uid == uid).first()


# Creates user from email
def create_user(db: Session, uid: str, user_email: str, admin: bool = False):
    db_user = model.User(uid=uid, email=user_email, admin=admin)
    print("creating user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Enrolls user in a course
def create_enrollment(
    db: Session, uid: str, course_id: str, course_semester: str, role: str
):
    # getting student
    db_user = get_user(db, uid)
    # getting course
    db_course = get_course(db, course_id, course_semester)
    # Creating enrollment
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


def get_all_units(db: Session):
    return db.query(model.Unit).all()


def get_all_available_units(db: Session):
    """
    Retrieves all unit records from the database where the date_available is before the current date,
    indicating that the units are currently available.

    Parameters:
        db (Session): The database session used to execute the query.

    Returns:
        List[Unit]: A list of Unit model instances that are currently available based on their date_available field.
    """
    # Get the current date to compare against the units' date_available
    current_date = datetime.utcnow().date()

    # Query the database for all units where date_available is before (or equal to) the current date
    return db.query(model.Unit).filter(model.Unit.date_available <= current_date).all()


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


def get_invitations(db: Session, uid: str):
    return db.query(model.Invitation).filter(model.Invitation.uid == uid).all()


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


def get_question(db: Session, question_id: int):
    return db.query(model.Question).filter(model.Question.id == question_id).first()


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


def check_recent_notification(db: Session, cooldown_days: int) -> bool:
    """
    Checks if a notification has been sent within a specified cooldown period.

    Parameters:
        db (Session): The database session to execute the query.
        cooldown_days (int): The number of days to look back from the current date.

    Returns:
        bool: True if a notification has been sent within the cooldown period, False otherwise.
    """
    cooldown_date = datetime.utcnow().date() - timedelta(days=cooldown_days)
    return (
        db.query(model.NotificationLog)
        .filter(model.NotificationLog.sent_at > cooldown_date)
        .first()
        is not None
    )


def create_notification_log(db: Session):
    """
    Creates a new notification log entry in the database with the current UTC time.

    Parameters:
        db (Session): The database session to add and commit the new log entry.

    Returns:
        The newly created NotificationLog object with the current UTC time as the sent timestamp.
    """
    new_log = model.NotificationLog(sent_at=datetime.utcnow())

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


def add_notification_count(db: Session, user_id: str, unit_id: int):
    """
    Increments the notification count for a specific user and unit, or creates a new entry if none exists.

    Parameters:
        db (Session): The database session to execute the query and update records.
        user_id (str): The id of the user for whom to update the notification count.
        unit_id (int): The ID of the unit for which to update the notification count.

    Returns:
        The updated or newly created UserUnitNotificationCount object.
    """
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


def get_notification_count(db: Session, user_id: str, unit_id: int) -> int:
    """
    Retrieves the notification count for a specific user and unit.

    Parameters:
        db (Session): The database session to execute the query.
        user_id (str): The id of the user for whom to retrieve the notification count.
        unit_id (int): The ID of the unit for which to retrieve the notification count.

    Returns:
        int: The notification count for the specified user and unit, or 0 if no entry exists.
    """
    notification_entry = (
        db.query(model.UserUnitNotificationCount)
        .filter_by(user_id=user_id, unit_id=unit_id)
        .first()
    )

    if notification_entry:
        return notification_entry.notification_count
    else:
        return 0


def get_all_courses(db: Session):
    """
    Fetches all courses from the database.

    Parameters:
    - db (Session): The SQLAlchemy session for database access.

    Returns:
    - List[Course]: A list of Course objects representing all courses in the database.
    """
    return db.query(model.Course).all()


def get_all_students_in_course(db: Session, course_id: str, course_semester: str):
    """
    Fetches all students enrolled in a specific course and semester.

    Parameters:
    - db (Session): The SQLAlchemy session for database access.
    - course_id (str): The unique identifier for the course.
    - course_semester (str): The semester during which the course is offered.

    Returns:
    - List[User]: A list of User objects representing the student enrolled in the specified course and semester.
    """
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


def get_units_to_notify(
    db: Session,
    user_id: str,
    notification_limit: int,
    course_id: str,
    course_semester: str,
):
    """
    Retrieves units for which a user should be notified, based on a specific course and semester,
    ensuring the user has not reached the notification limit for those units.

    Parameters:
    - db (Session): The SQLAlchemy session for database access.
    - user_id (str): The unique identifier of the user.
    - notification_limit (int): The maximum number of notifications a user can receive for a unit.
    - course_id (str): The unique identifier of the course.
    - course_semester (str): The semester in which the course is offered.

    Returns:
    - List[Unit]: A list of Unit objects for which the user should be notified.
    """
    available_units = (
        db.query(model.Unit)
        .filter(
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
            model.Unit.hidden == False,
            model.Unit.date_available <= date.today(),
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

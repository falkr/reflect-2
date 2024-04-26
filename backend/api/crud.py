from datetime import date, datetime, timedelta
from fastapi import HTTPException

from . import model
from . import schemas
from sqlalchemy.orm import Session
from starlette.config import Config

config = Config(".env")


# --- User ---
def get_user(db: Session, uid: str):
    return db.query(model.User).filter(model.User.uid == uid).first()


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


def delete_records(db: Session, model, filters):
    records = db.query(model).filter(*filters).all()
    for record in records:
        db.delete(record)
    db.commit()


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
    """
    Creates a new unit and its associated initial report in the database. If a unit with the same
    ID already exists, it updates the existing unit with the provided details.

    Parameters:
    - db (Session): The database session used to perform operations.
    - title (str): The title of the unit.
    - date_available (str): The date the unit becomes available to users, in a string format.
    - course_id (str): The identifier of the course to which the unit belongs.
    - course_semester (str): The semester during which the unit is offered.

    Returns:
    - model.Unit: An instance of the Unit model representing the newly created unit.
    """
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


# update unit
def update_unit(
    db: Session,
    unit_id: int,
    title: str,
    date_available: str,
    course_id: str,
    course_semester: str,
):
    """
    Updates an existing unit with new information provided as parameters. This function
    allows updating the unit's title and availability date.

    Parameters:
    - db (Session): The database session used to perform operations.
    - unit_id (int): The unique identifier of the unit to be updated.
    - title (str): The new title for the unit.
    - date_available (str): The new availability date for the unit.
    - course_id (str): The course ID to which the unit is associated.
    - course_semester (str): The semester during which the unit is offered.

    Returns:
    - model.Unit: The updated unit object if the operation is successful.

    Raises:
    - HTTPException: A 404 error if no unit matches the provided `unit_id`.
    """
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


# delete unit
def delete_unit(db: Session, unit_id: int, course_id: str, course_semester: str):
    """
    Deletes a specified unit, along with all associated reflections and reports, from the database.

    Parameters:
    - db (Session): The database session used to execute the database operations.
    - unit_id (int): The unique identifier of the unit to be deleted.
    - course_id (str): The ID of the course to which the unit belongs. Used to ensure the
      correct report is deleted along with the unit.
    - course_semester (str): The semester of the course to which the unit belongs. Used in
      conjunction with `course_id` to identify the correct report.

    Returns:
    - The deleted unit object if the operation is successful.

    Raises:
    - HTTPException: A 404 error if the specified unit cannot be found in the database.
    """
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


def create_question(db: Session, question: str, comment: str):
    db_obj = model.Question(question=question, comment=comment)
    print("creating question")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- Reflection ---
def create_reflection(db: Session, reflection_data: dict):
    # Create a new reflection with current timestamp
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


def get_reflections(db: Session, user_id: str, unit_id: int):
    return (
        db.query(model.Reflection)
        .filter(model.Reflection.user_id == user_id)
        .filter(model.Reflection.unit_id == unit_id)
        .all()
    )


def delete_reflection(db: Session, user_id: str, unit_id: int):
    """
    Deletes all reflections for a given user and unit.

    Args:
        db (Session): The database session to use for querying and deleting.
        user_id (str): The user identifier to match reflections.
        unit_id (int): The unit identifier to match reflections.

    Returns:
        dict: A dictionary with the `user_id` and `unit_id` of the deleted reflections.

    Raises:
        HTTPException: If no reflections are found for the specified user and unit.
    """
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


def get_report(db: Session, course_id: str, unit_id: int, course_semester: str):
    return (
        db.query(model.Report)
        .filter(model.Report.unit_id == unit_id)
        .filter(model.Report.course_id == course_id)
        .filter(model.Report.course_semester == course_semester)
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


def save_report(db: Session, report: schemas.ReportCreate) -> model.Report:
    """
    Save or update a report in the database based on the provided report details.

    Parameters:
    - db (Session): The database session used to perform database operations.
    - report (schemas.ReportCreate): An instance of ReportCreate schema containing the report details.

    Returns:
    - model.Report: The updated or newly created report object from the database.
    """
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

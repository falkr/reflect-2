import json
import os
from datetime import datetime, date
from typing import List

import requests
from requests.structures import CaseInsensitiveDict
from api.utils.exceptions import DataProcessingError, OpenAIRequestError
from prompting.enforceUniqueCategories import enforce_unique_categories
from prompting.summary import createSummary
from prompting.transformKeysToAnswers import transformKeysToAnswers
from prompting.sort import sort
from prompting.createCategories import createCategories

from . import crud
from . import model
from . import schemas

from authlib.integrations.starlette_client import OAuth, OAuthError
from .database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, Response, JSONResponse

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.responses import FileResponse

model.Base.metadata.create_all(bind=engine)

app = FastAPI()
config = Config(".env")
oauth = OAuth(config)

CONF_URL = "https://auth.dataporten.no/.well-known/openid-configuration"
SECRET_KEY = config("SECRET_KEY", cast=Secret)
CLIENT_ID = str(config("client_id", cast=Secret))
CLIENT_SECRET = str(config("client_secret", cast=Secret))

NOTIFICATION_COOLDOWN_DAYS = config("NOTIFICATION_COOLDOWN_DAYS", cast=int, default=1)
NOTIFICATION_LIMIT = config("NOTIFICATION_LIMIT", cast=int, default=2)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

email_config = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME", cast=str, default=""),
    MAIL_PASSWORD=config("MAIL_PASSWORD", cast=str, default=""),
    MAIL_FROM=config("MAIL_FROM", cast=str, default=""),
    MAIL_PORT=config("MAIL_PORT", cast=int, default=587),
    MAIL_SERVER=config("MAIL_SERVER", cast=str, default=""),
    MAIL_FROM_NAME="Reflection Tool",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False,
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def is_prod():
    return config("production", cast=bool, default=False)


if is_prod():
    REDIRECT_URI = config("REDIRECT_URI", cast=str)
    BASE_URL = config("BASE_URL", cast=str)
else:
    REDIRECT_URI = "http://127.0.0.1:8000/auth"
    BASE_URL = "http://127.0.0.1:5173"


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


oauth.register(
    name="feide",
    server_metdata_url=CONF_URL,
    client_kwards={"scope": "openid"},
    authorize_url="https://auth.dataporten.no/oauth/authorization",
    access_token_url="https://auth.dataporten.no/oauth/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)


def get_user_data(bearer_token):
    """
    This function retrieves user data from the Dataporten API using the provided bearer token.
    """
    url = "https://api.dataporten.no/userinfo/v1/userinfo"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {bearer_token}"
    # print(f"Bearer {bearer_token}")
    resp = requests.get(url, headers=headers)
    return str(resp.content.decode())


def is_logged_in(request):
    user = request.session.get("user")
    return user is not None


def protect_route(request: Request):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")


def is_admin(db, request):
    if config("isAdmin", cast=bool, default=False):
        return True

    user = request.session.get("user")
    if user is None:
        return False
    uid: str = user.get("uid")
    user = crud.get_user(db, uid)
    if user is None:
        return False
    return user.admin


def check_is_admin(bearer_token):
    """
    Checks if the user is an admin by querying the Dataporten API for group memberships.
    """
    url = "https://groups-api.dataporten.no/groups/me/groups"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {bearer_token}"}

    try:
        # Using 'with' ensures the request is closed properly
        with requests.get(url, headers=headers) as resp:
            resp.raise_for_status()
            data = resp.json()

        admin_roles = {"LECTURER", "LÆRER", "HOVEDLÆRER", "KONTAKT"}
        for group in data:
            if group["membership"]["basic"] == "owner":
                return True
            if admin_roles.intersection(group["membership"]["fsroles"]):
                return True

    except requests.RequestException as e:
        raise HTTPException(500, detail="Failed to check admin status")
    except json.JSONDecodeError:
        raise HTTPException(500, detail="Failed to parse admin status")

    return False


@app.on_event("startup")
async def start_db():
    """
    Used for creating dummy data in the database for development purposes when running locally.

    It creates a course, units, and users, and enrolls a test user in the course.
    """
    if is_prod():
        return

    print("init database")
    course_id: str = "TDT4100"
    semester: str = "fall2023"
    course_name: str = "Informasjonsteknologi grunnkurs"
    db = SessionLocal()
    course = crud.get_course(db, course_id=course_id, course_semester=semester)
    if course:
        return

    course = crud.create_course(
        db,
        course={
            "name": course_name,
            "id": course_id,
            "semester": semester,
            "questions": [],
        },
    )

    UID = config("UID", cast=str, default="test")
    EMAIL_USER = config("EMAIL_USER", cast=str, default="test@test.no")

    user = crud.create_user(db, uid=UID, user_email=EMAIL_USER)
    user0 = crud.create_user(db, uid="test2", user_email="test2@test.no")
    user1 = crud.create_user(db, uid="test3", user_email="test3@test.no")

    units = [
        crud.create_unit(
            db=db,
            title="State Machines",
            date_available=datetime(2022, 8, 23),
            course_id=course.id,
            course_semester=semester,
        ),
        crud.create_unit(
            db=db,
            title="HTTP og JSON",
            date_available=datetime(2022, 8, 30),
            course_id=course.id,
            course_semester=semester,
        ),
        crud.create_unit(
            db=db,
            title="MQTT Chat",
            date_available=datetime(2024, 9, 7),
            course_id=course.id,
            course_semester=semester,
        ),
    ]

    for u in units:
        course.units.append(u)
        u.course_id = course.id
        u.course_semester = semester

    await crud.create_enrollment(
        db=db,
        course_id="TDT4100",
        course_semester=semester,
        role="student",
        uid=UID,
    )

    db.commit()
    db.close()


@app.get("/login")
async def login(request: Request):
    return await oauth.feide.authorize_redirect(request, REDIRECT_URI)


@app.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    """
    This is the callback route for the OAuth2 authentication process.
    It retrieves the access token from the request and stores it in the user's session.

    Also creates a user in the database if the user does not already exist.
    """
    try:
        token = await oauth.feide.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>{error.error}</h1>")
    bearer_token = token.get("access_token")
    # print("bearer_token", bearer_token)
    request.session["scope"] = token.get("scope")
    request.session["bearer_token"] = bearer_token
    request.session["user_data"] = get_user_data(bearer_token)
    user = get_user_data(bearer_token)
    if user:
        user = json.loads(user)
        #  For testing purposes, we can set the user to a test user
        if config("TEST_ACCOUNT", cast=bool, default=False):
            user["uid"] = "test"
            user["mail"] = "test@mail.no"
        else:
            user["uid"] = user["uid"][0]
            user["mail"] = user["mail"][0]
        request.session["user"] = user
        email = user.get("mail")
        uid = user.get("uid")
        db_user = crud.get_user(db, uid)
        if not db_user:
            print("creating user")
            crud.create_user(
                db=db, uid=uid, user_email=email, admin=check_is_admin(bearer_token)
            )
        else:
            print("user already exists")
    else:
        print("No user data")
    return RedirectResponse(url=BASE_URL + "/login")


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url=BASE_URL + "/")


@app.post("/reflection", response_model=schemas.Reflection)
async def create_reflection(
    request: Request, ref: schemas.ReflectionCreate, db: Session = Depends(get_db)
):
    """
    Creates a reflection based on the data provided in the `ref` object.
    This saves the response a user has given to a question in a unit.
    """
    protect_route(request)

    unit = crud.get_unit(db, ref.unit_id)
    if unit is None:
        raise HTTPException(404, detail="Unit cannot be found")

    if crud.get_question(db, ref.question_id) is None:
        raise HTTPException(404, detail="Question cannot be found")

    if unit.hidden:
        raise HTTPException(403, detail="Unit cannot be reflected when hidden")

    if crud.user_already_reflected_on_question(
        db, ref.unit_id, ref.user_id, ref.question_id
    ):
        raise HTTPException(403, detail="You have already reflected this question")

    if unit.date_available > date.today():
        raise HTTPException(403, detail="This unit is not available")

    return crud.create_reflection(db, reflection_data=ref.dict())


@app.delete("/delete_reflection", response_model=schemas.ReflectionDelete)
async def delete_reflection(
    request: Request, ref: schemas.ReflectionDelete, db: Session = Depends(get_db)
):
    """
    Deletes a reflection based on the user ID, unit ID, and question ID provided in the `ref` object.
    """
    protect_route(request)

    if is_admin(db, request):
        return crud.delete_reflection(db, ref.user_id, ref.unit_id)
    else:
        raise HTTPException(
            403, detail="You do not have permission to delete this reflection"
        )


# Example: /course?course_id=TDT4100&course_semester=fall2023
@app.get("/course", response_model=schemas.Course)
async def course(
    request: Request,
    course_id: str,
    course_semester: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves a course based on the course ID and course semester provided.
    """
    protect_route(request)

    course = crud.get_course(db, course_id=course_id, course_semester=course_semester)
    if course is None:
        raise HTTPException(404, detail="Course not found")

    print("course found")
    print(course)
    return course


@app.post("/create_course", response_model=schemas.Course)
async def create_course(
    request: Request, ref: schemas.CourseCreate, db: Session = Depends(get_db)
):
    """
    Creates a course based on the data provided in the `ref` object.
    """
    protect_route(request)

    if not is_admin(db, request):
        raise HTTPException(403, detail="You are not an admin user")
    try:
        return crud.create_course(db, course=ref.dict())

    except IntegrityError:
        raise HTTPException(409, detail="Course already exists")


@app.get("/user", response_model=schemas.User)
async def user(request: Request, db: Session = Depends(get_db)):
    """
    Retrieves the user's data based on the user ID stored in the session.

    It will also return the users enrollments and missing units.
    """
    protect_route(request)

    user = request.session.get("user")
    uid: str = user.get("uid")
    user = crud.get_user(db, uid)

    for enrollment in user.enrollments:
        course = crud.get_course(db, enrollment.course_id, enrollment.course_semester)
        enrollment.course_name = course.name
        if enrollment.role not in ["lecturer", "teaching assistant"]:
            today = datetime.now().date()
            enrollment.missingUnits = [
                {"id": unit.id, "date": unit.date_available}
                for unit in crud.get_units_for_course(
                    db, enrollment.course_id, enrollment.course_semester
                )
                if unit.date_available and unit.date_available <= today
            ]
            reflected_units = {reflection.unit_id for reflection in user.reflections}
            enrollment.missingUnits = [
                unit
                for unit in enrollment.missingUnits
                if unit["id"] not in reflected_units
            ]

    if user == None:
        request.session.pop("user")
        raise HTTPException(404, detail="User not found")

    if config("isAdmin", cast=bool, default=False):
        user.admin = True

    return user


# enroll self in course
@app.post("/enroll", response_model=schemas.Enrollment)
async def enroll(
    request: Request, ref: schemas.EnrollmentCreate, db: Session = Depends(get_db)
):
    """
    Enrolls a user in a course based on the data provided in the `ref` object.
    This will also enroll a user if they have a private invitation to the course.
    """
    protect_route(request)

    course = crud.get_course(
        db, course_id=ref.course_id, course_semester=ref.course_semester
    )

    if course == None:
        raise HTTPException(404, detail="Course not found")

    user = request.session.get("user")
    uid: str = user.get("uid")
    if user is None:
        raise HTTPException(401, detail="Cannot find your user")

    invitations = crud.get_invitations(db, uid)
    if invitations is not None:
        priv_inv = crud.get_priv_invitations_course(
            db, uid, ref.course_id, ref.course_semester
        )
        if len(priv_inv) != 0 or is_admin(db, request):
            try:

                return await crud.create_enrollment(
                    db,
                    role=ref.role,
                    course_id=ref.course_id,
                    course_semester=ref.course_semester,
                    uid=uid,
                )
            except IntegrityError:
                raise HTTPException(409, detail="User already enrolled in this course")

    if ref.role == "student" or is_admin(db, request):
        try:
            return await crud.create_enrollment(
                db,
                role=ref.role,
                course_id=ref.course_id,
                course_semester=ref.course_semester,
                uid=uid,
            )
        except IntegrityError:
            raise HTTPException(409, detail="User already enrolled in this course")

    raise HTTPException(403, detail="User not allowed to enroll")


# Example: /units?course_id=TDT4100&course_semester=fall2023
@app.get("/units", response_model=List[schemas.Unit])
async def get_units(
    request: Request,
    course_id: str,
    course_semester: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves all units for a specific course based on the course ID and course semester provided.
    If a user is not enrolled in the course, they will be enrolled as a student.

    And if they are a lecturer or teaching assistant, they will see all units including the hidden ones.
    """
    protect_route(request)

    user = request.session.get("user")
    uid: str = user.get("uid")
    course = crud.get_course(db, course_id, course_semester)
    if course is None:
        raise HTTPException(404, detail="Course not found")

    enrollment = crud.get_enrollment(db, course_id, course_semester, uid)
    if enrollment is None:
        await crud.create_enrollment(
            db,
            role="student",
            course_id=course_id,
            course_semester=course_semester,
            uid=uid,
        )
        enrollment = crud.get_enrollment(db, course_id, course_semester, uid)
        if enrollment is None:
            raise HTTPException(401, detail="You are not enrolled in the course")

    if is_admin(db, request) or enrollment.role in ["lecturer", "teaching assistant"]:
        units = (
            db.query(model.Unit)
            .filter(
                model.Unit.course_id == course_id,
                model.Unit.course_semester == course_semester,
            )
            .all()
        )
        units = [unit.to_dict() for unit in units]
        return units
    else:
        units = (
            db.query(model.Unit)
            .filter(
                model.Unit.course_id == course_id,
                model.Unit.course_semester == course_semester,
                model.Unit.hidden == False,
            )
            .all()
        )

        units = [unit.to_dict() for unit in units]
        return units


@app.post("/create_unit", response_model=schemas.Unit)
async def create_unit(
    request: Request, ref: schemas.UnitCreate, db: Session = Depends(get_db)
):
    """
    Creates a new unit with the unit-details from the 'ref' object, if the user-details provided in `ref` is admin.
    """
    protect_route(request)

    user = request.session.get("user")
    uid: str = user.get("uid")
    enrollment = crud.get_enrollment(db, ref.course_id, ref.course_semester, uid)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    if is_admin(db, request) or enrollment.role in ["lecturer", "teaching assistant"]:
        return crud.create_unit(
            db=db,
            title=ref.title,
            date_available=ref.date_available,
            course_id=ref.course_id,
            course_semester=ref.course_semester,
        )
    raise HTTPException(
        403, detail="You do not have permission to edit a unit for this course"
    )


@app.patch("/update_unit/{unit_id}", response_model=schemas.UnitCreate)
async def update_unit(
    unit_id: int,
    request: Request,
    ref: schemas.UnitCreate,
    db: Session = Depends(get_db),
):
    """
    Updates the details of an existing unit identified by `unit_id` with new information
    provided in the `ref` object, which includes the unit's title and date available.
    """
    protect_route(request)

    user = request.session.get("user")
    uid: str = user.get("uid")
    unit = crud.get_unit(db, unit_id)
    if not unit:
        raise HTTPException(404, detail="Unit not found")
    enrollment = crud.get_enrollment(db, unit.course_id, unit.course_semester, uid)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    if is_admin(db, request) or enrollment.role in ["lecturer", "teaching assistant"]:
        return crud.update_unit(
            db=db,
            unit_id=unit_id,
            title=ref.title,
            date_available=ref.date_available,
            course_id=ref.course_id,
            course_semester=ref.course_semester,
        )
    raise HTTPException(
        403, detail="You do not have permission to edit a unit for this course"
    )


@app.delete("/delete_unit/{unit_id}", response_model=schemas.UnitDelete)
async def delete_unit(
    unit_id: int,
    ref: schemas.UnitDelete,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Deletes a specific unit based on the unit ID, course ID, and course semester provided, if user-details from 'ref' object is admin.
    """
    user = request.session.get("user")
    uid: str = user.get("uid")
    unit = crud.get_unit(db, unit_id)
    if not unit:
        raise HTTPException(404, detail="Unit not found")
    enrollment = crud.get_enrollment(db, unit.course_id, unit.course_semester, uid)
    if is_admin(db, request) or enrollment.role in ["lecturer"]:
        return crud.delete_unit(db, unit_id, ref.course_id, ref.course_semester)
    raise HTTPException(
        403, detail="You do not have permission to delete a unit for this course"
    )


# For deleting a unit after it has been created
class FileResponseWithDeletion(FileResponse):
    def __init__(self, path: str, filename: str, **kwargs):
        super().__init__(path, filename=filename, **kwargs)

    async def __call__(self, scope, receive, send):
        await super().__call__(scope, receive, send)
        os.remove(self.path)


@app.get("/download")
async def download_file(
    request: Request,
    ref: schemas.AutomaticReport = Depends(),
    db: Session = Depends(get_db),
):
    """
    Retrieves a report stored in the database based on course id, unit id, and course semester provided in the `ref` object.
    Downloads the provided report file.
    """
    protect_route(request)

    user = request.session.get("user")
    uid: str = user.get("uid")
    enrollment = crud.get_enrollment(db, ref.course_id, ref.course_semester, uid)
    if is_admin(db, request) or enrollment.role in ["lecturer"]:
        report = await get_report(
            request,
            params=schemas.AutomaticReport(
                course_id=ref.course_id,
                course_semester=ref.course_semester,
                unit_id=ref.unit_id,
            ),
            db=db,
        )

        try:
            report_dict = report.to_dict()
        except Exception as e:
            raise HTTPException(
                500,
                detail=f"An error occurred while generating the report, you may have not generated a report yet. Error: {str(e)}",
            )

        if config("SERVERLESS", cast=bool, default=False):
            return json.dumps(report_dict, indent=4)

        with open("report.txt", "w") as f:
            f.write(json.dumps(report_dict, indent=4))

        path = os.getcwd() + "/report.txt"
        return FileResponseWithDeletion(path, filename="report.txt")

    return Response(status_code=403)


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# Example: /unit_data?course_id=TDT4100&course_semester=fall2023&unit_id=1
@app.get("/unit_data", response_model=schemas.UnitData)
async def get_unit_data(
    request: Request,
    course_id: str,
    course_semester: str,
    unit_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves a specific unit based on the course ID, course semester, and unit ID provided.
    """
    protect_route(request)

    user = request.session.get("user")
    email: str = user.get("uid")
    course = crud.get_course(db, course_id, course_semester)
    if course is None:
        raise HTTPException(404, detail="Course not found")
    enrollment = crud.get_enrollment(db, course_id, course_semester, email)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    unit = (
        db.query(model.Unit)
        .filter(
            model.Unit.id == unit_id,
            model.Unit.course_id == course_id,
            model.Unit.course_semester == course_semester,
        )
        .first()
    )
    if unit:
        questions = [to_dict(question) for question in course.questions]

        if is_admin(db, request) or enrollment.role in [
            "lecturer",
            "teaching assistant",
        ]:
            return {
                "unit": unit,
                "unit_questions": questions,
            }
        else:
            unit = (
                db.query(model.Unit)
                .filter(
                    model.Unit.course_id == course_id,
                    model.Unit.course_semester == course_semester,
                    model.Unit.id == unit_id,
                    model.Unit.hidden == False,
                )
                .first()
            )
            if unit:
                return {
                    "unit": unit,
                    "unit_questions": questions,
                }

    raise HTTPException(404, detail="Unit not found")


# This can be uncommented to test the functionality for development purposes
# @app.post("/save_report", response_model=schemas.ReportCreate)
async def save_report_endpoint(
    request: Request, ref: schemas.ReportCreate, db: Session = Depends(get_db)
):
    if not is_admin(db, request):
        raise HTTPException(403, detail="You are not an admin user")
    try:
        return crud.save_report(db, report=ref.model_dump())
    except IntegrityError as e:
        raise HTTPException(
            409, detail="An error occurred while saving the report: " + str(e)
        )


@app.get("/report")
async def get_report(
    request: Request,
    params: schemas.AutomaticReport = Depends(),
    db: Session = Depends(get_db),
):
    """
    Retrieve a report from the database based on the provided parameters such as course id, unit id, and course semester.
    """
    protect_route(request)
    report = crud.get_report(
        db,
        course_id=params.course_id,
        unit_id=params.unit_id,
        course_semester=params.course_semester,
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.post("/create_invitation", response_model=schemas.Invitation)
async def create_invitation(
    request: Request, ref: schemas.InvitationBase, db: Session = Depends(get_db)
):
    """
    Creates an invitation to an user for a course based on user-details and course-details provided in the `ref` object.
    """
    protect_route(request)
    user = request.session.get("user")
    uid: str = user.get("uid")
    user = crud.get_user(db, uid)
    if user is None:
        raise HTTPException(401, detail="Cannot find your user")
    enrollment = crud.get_enrollment(db, ref.course_id, ref.course_semester, uid)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    if not is_admin(db, request) or not enrollment.role in [
        "lecturer",
        "teaching assistant",
    ]:
        raise HTTPException(403, detail="You are not allowed to invite to this course")
    try:
        return crud.create_invitation(db, invitation=ref.dict())
    except IntegrityError:
        raise HTTPException(409, detail="invitation already exists")


# get all invitations by user
@app.get("/get_invitations", response_model=List[schemas.Invitation])
async def get_invitations(request: Request, db: Session = Depends(get_db)):
    """
    Retrieves all invitations for a user based on the user ID stored in the session.
    """
    protect_route(request)

    user = request.session.get("user")
    uid: str = user.get("uid")

    return crud.get_invitations(db, uid)


# delete invitation
@app.delete("/delete_invitation/{id}")
async def delete_invitation(request: Request, id: int, db: Session = Depends(get_db)):
    """
    Deletes an invitation based on the invitation ID provided.
    """
    protect_route(request)

    return crud.delete_invitation(db, id=id)


@app.post("/send-notifications")
async def send_notifications(db: Session = Depends(get_db)):
    """
    Sends reminder notifications to students about units they need to provide feedback for.

    This function iterates over all courses and their enrolled students, identifying units
    for which students have not yet reached the notification limit. It then sends a reminder
    email to each student about their pending units, updating the notification count for each unit
    per student.
    """
    if crud.check_recent_notification(db, NOTIFICATION_COOLDOWN_DAYS):
        print(
            "Notification already sent in the last", NOTIFICATION_COOLDOWN_DAYS, "days"
        )
        raise HTTPException(
            status_code=400,
            detail="A notification has already been sent in the last "
            + str(NOTIFICATION_COOLDOWN_DAYS)
            + " days.",
        )

    results = []
    courses = crud.get_all_courses(db)

    for course in courses:
        students = crud.get_all_students_in_course(db, course.id, course.semester)

        for student in students:
            units = crud.get_units_to_notify(
                db, student.uid, NOTIFICATION_LIMIT, course.id, course.semester
            )

            if len(units) == 0:
                continue

            try:
                message = MessageSchema(
                    subject=f"{course.id} - Missing Reflection",
                    recipients=[student.email],
                    body=format_email(student.uid, course.id, units),
                    subtype="html",
                )

                fm = FastMail(email_config)
                await fm.send_message(message)

                for unit in units:
                    crud.add_notification_count(db, student.uid, unit.id)

                results.append(
                    {
                        "course": course.id,
                        "units": [unit.id for unit in units],
                        "email": student.email,
                        "status": "success",
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "course": course.id,
                        "units": [unit.id for unit in units],
                        "email": student.email,
                        "status": "error",
                        "message": str(e),
                    }
                )
    crud.create_notification_log(db=db)
    return JSONResponse(status_code=200, content=results)


def format_email(student_id: str, course_id: str, units: List[model.Unit]):
    """
    Generates the HTML content for an email reminder to a student about providing feedback on learning units.
    """
    unit_links = [
        f'<li><a href="https://reflect.iik.ntnu.no/courseview/{unit.course_semester}/{unit.course_id}/{unit.id}">{unit.title}</a></li>'
        for unit in reversed(units)
    ]

    additional_units = (
        ""
        if len(unit_links) <= 1
        else f"<p>Also, you have not yet answered the following units:</p><ul>{''.join(unit_links[1:])}</ul>"
    )

    return f"""<p>Dear {student_id},</p>
    <p>This is a reminder to answer the recent learning unit in {course_id}:</p>
    <ul>{unit_links[0]}</ul>
    {additional_units}
    <p>Your input will directly contribute to improving the lectures for your benefit and the benefit of future students. Your feedback will be shared with your lecturer to help them tailor their teaching approach to your needs.</p>
    <p>Best regards,<br/>The Reflection Tool Team</p>"""


@app.post("/analyze_feedback")
async def analyze_feedback(ref: schemas.ReflectionJSON):
    """
    Analyzes student feedback, sorts it into predefined categories, and generates a summary.

    This function processes student feedback submitted for a learning unit. It categorizes the feedback based on the content, sorts it accordingly, and then generates a summary highlighting key themes. The process involves the following steps:
    1. Filtering relevant information from the submitted feedback.
    2. Categorizing the feedback using the OpenAI API.
    3. Sorting the feedback into the identified categories.
    4. Transforming sorted keys into actual answers for a readable format.
    5. Generating a summary of the categorized feedback.
    """

    # Adds a key to each student feedback dict to identify the student and filter out irrelevant information
    student_feedback_dicts = [
        {
            **{"key": index + 1},
            **{
                key: item[key]
                for key in item
                if key not in ["learning_unit", "participation"]
            },
        }
        for index, item in enumerate(
            (item.model_dump() for item in ref.student_feedback)
        )
    ]

    categories = createCategories(
        ref.api_key, ref.questions, student_feedback_dicts, ref.use_cheap_model
    )

    sorted_feedback = sort(
        ref.api_key,
        ref.questions,
        categories,
        student_feedback_dicts,
        ref.use_cheap_model,
    )

    sorted_feedback = enforce_unique_categories(sorted_feedback)

    stringAnswered = transformKeysToAnswers(
        sorted_feedback, ref.questions, student_feedback_dicts
    )

    summary = createSummary(ref.api_key, stringAnswered, ref.use_cheap_model)
    stringAnswered["Summary"] = summary["summary"]

    return stringAnswered


@app.delete("/unenroll_course")
async def unenroll_course(
    request: Request, ref: schemas.EnrollmentBase, db: Session = Depends(get_db)
):
    """
    Unenrolls the user from a course based on the course ID and course semester provided in the `ref` object.
    """
    protect_route(request)
    try:
        user = request.session.get("user")
        uid = user.get("uid")
        return crud.delete_enrollment(db, uid, ref.course_id, ref.course_semester)
    except IntegrityError:
        raise HTTPException(409, detail="Course already exists")


@app.delete("/delete_course")
async def delete_course(
    request: Request, ref: schemas.CourseBase, db: Session = Depends(get_db)
):
    """
    Deletes a course based on the course ID and course semester provided in the `ref` object.
    """
    protect_route(request)
    if not is_admin(db, request):
        raise HTTPException(403, detail="You are not an admin user")
    try:
        return crud.delete_course(db, ref.id, ref.semester)
    except IntegrityError:
        raise HTTPException(409, detail="Course already exists")


@app.post("/generate_report")
async def generate_report_endpoint(
    request: Request, ref: schemas.AutomaticReport, db: Session = Depends(get_db)
):
    """
    Generates and saves a report for a specific unit based on the course ID, course semester, and unit ID provided in the `ref` object.
    """
    if not is_admin(db, request):
        raise HTTPException(403, detail="You are not an admin user")
    try:
        unit_data = await get_unit_data(
            request, ref.course_id, ref.course_semester, ref.unit_id, db
        )

        questions = [q["comment"] for q in unit_data["unit_questions"]]
        reflections = unit_data["unit"].reflections

        student_answers = {}
        for reflection in reflections:
            if reflection.user_id not in student_answers:
                student_answers[reflection.user_id] = {"answers": [reflection.body]}
            else:
                student_answers[reflection.user_id]["answers"].append(reflection.body)

        student_feedback = [
            {"answers": student_answers[student]["answers"]}
            for student in student_answers
        ]

        feedback = schemas.ReflectionJSON(
            api_key=config("OPENAI_KEY", cast=str),
            questions=questions,
            student_feedback=student_feedback,
            use_cheap_model=True,
        )

        analyze = await analyze_feedback(feedback)

        try:
            await save_report_endpoint(
                request,
                ref=schemas.AnalyzeReportCreate(
                    number_of_answers=len(student_feedback),
                    report_content=analyze,
                    unit_id=ref.unit_id,
                    course_id=ref.course_id,
                    course_semester=ref.course_semester,
                ),
                db=db,
            )
            crud.reset_reflections_count(db, ref.unit_id)
        except:
            raise HTTPException(500, detail="An error occurred while saving the report")
        return HTTPException(200, detail="Report generated and saved successfully")
    except IntegrityError as e:
        raise HTTPException(
            409, detail="An error occurred while generating the report: " + str(e)
        )


@app.exception_handler(DataProcessingError)
async def data_processing_exception_handler(request, exc: DataProcessingError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Data processing error: {exc.message}"},
    )


@app.exception_handler(OpenAIRequestError)
async def openai_request_exception_handler(request, exc: OpenAIRequestError):
    return JSONResponse(
        status_code=502,
        content={"message": f"OpenAI API request failed: {exc.message}"},
    )

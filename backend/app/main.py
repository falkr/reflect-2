import json
import os
from datetime import datetime, date
from typing import List

import requests
from requests.structures import CaseInsensitiveDict

from . import crud
from . import model
from . import schemas
from prompting.main import analyze_student_feedback

from authlib.integrations.starlette_client import OAuth, OAuthError
from .database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Should all this be in .env?
email_config = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME", cast=str),
    MAIL_PASSWORD=config("MAIL_PASSWORD", cast=str),
    MAIL_FROM=config("MAIL_FROM", cast=str),
    MAIL_PORT=config("MAIL_PORT", cast=int),
    MAIL_SERVER=config("MAIL_SERVER", cast=str),
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
    REDIRECT_URI = "http://localhost/auth"
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
# Adds dummy data if in development mode
def start_db():
    print("init database")
    course_id: str = "TDT4100"
    semester: str = "fall2023"
    course_name: str = "Informasjonsteknologi grunnkurs"
    db = SessionLocal()
    course = crud.get_course(db, course_id=course_id, course_semester=semester)

    # Do not populate database if prod or data exists
    if course or is_prod():
        return

    course = crud.create_course(
        db, course={"name": course_name, "id": course_id, "semester": semester}
    )

    UID = config("UID", cast=str)
    EMAIL_USER = config("EMAIL_USER", cast=str)

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

    """
    questions = [
        crud.create_question(
            db=db,
            question="Læringsprestasjon",
            comment="Hva lærte du i denne enheten? Hva var din klareste innsikt, eller din beste læringsprestasjon?",
        ),
        crud.create_question(
            db=db,
            question="Vanskeligst",
            comment="Hva var vanskeling denne gangen? Var det et konsept som du slet mest med, eller noe som du synes var uklart?",
        ),
    ]
    for q in questions:
        course.questions.append(q)
    """

    for u in units:
        course.units.append(u)
        u.course_id = course.id
        u.course_semester = semester

    enrollment = crud.create_enrollment(
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
    try:
        token = await oauth.feide.authorize_access_token(request)
    except OAuthError as error:
        raise error
        return HTMLResponse(f"<h1>{error.error}</h1>")
    bearer_token = token.get("access_token")
    print("bearer_token", bearer_token)
    request.session["scope"] = token.get("scope")
    request.session["bearer_token"] = bearer_token
    request.session["user_data"] = get_user_data(bearer_token)
    user = get_user_data(bearer_token)
    if user:
        user = json.loads(user)
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
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

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

    return crud.create_reflection(db, reflection=ref.dict())


# Example: /course?course_id=TDT4100&course_semester=fall2023
@app.get("/course", response_model=schemas.Course)
async def course(
    request: Request,
    course_id: str,
    course_semester: str,
    db: Session = Depends(get_db),
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in ")

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
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")
    if not is_admin(db, request):
        raise HTTPException(403, detail="You are not an admin user")
    try:
        return crud.create_course(db, course=ref.dict())

    except IntegrityError:
        raise HTTPException(409, detail="Course already exists")


@app.get("/user", response_model=schemas.User)
async def user(request: Request, db: Session = Depends(get_db)):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in ")

    user = request.session.get("user")
    uid: str = user.get("uid")
    user = crud.get_user(db, uid)
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

    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in ")

    course = crud.get_course(
        db, course_id=ref.course_id, course_semester=ref.course_semester
    )

    if course == None:
        raise HTTPException(404, detail="Course not found")

    user = request.session.get("user")
    uid: str = user.get("uid")
    if user is None:
        raise HTTPException(401, detail="Cannot find your user")
    if ref.role == "student":
        try:
            return crud.create_enrollment(
                db,
                role=ref.role,
                course_id=ref.course_id,
                course_semester=ref.course_semester,
                uid=uid,
            )
        except IntegrityError:
            raise HTTPException(409, detail="User already enrolled in this course")
    invitations = crud.get_invitations(db, uid)
    if invitations is not None:
        priv_inv = crud.get_priv_invitations_course(
            db, uid, ref.course_id, ref.course_semester
        )
        if len(priv_inv) != 0 or is_admin(db, request):
            try:

                return crud.create_enrollment(
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
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

    user = request.session.get("user")
    uid: str = user.get("uid")
    course = crud.get_course(db, course_id, course_semester)
    if course is None:
        raise HTTPException(404, detail="Course not found")
    enrollment = crud.get_enrollment(db, course_id, course_semester, uid)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    if is_admin(db, request) or enrollment.role in ["lecturer", "teaching assistant"]:
        return (
            db.query(model.Unit)
            .filter(
                model.Unit.course_id == course_id,
                model.Unit.course_semester == course_semester,
            )
            .all()
        )
    else:
        return (
            db.query(model.Unit)
            .filter(
                model.Unit.course_id == course_id,
                model.Unit.course_semester == course_semester,
                model.Unit.hidden == False,
            )
            .all()
        )


@app.post("/create_unit", response_model=schemas.Unit)
async def create_unit(
    request: Request, ref: schemas.UnitCreate, db: Session = Depends(get_db)
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

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


@app.patch("/update_hidden_unit", response_model=schemas.Unit)
async def update_hidden_unit(
    request: Request, ref: schemas.UnitHidden, db: Session = Depends(get_db)
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

    user = request.session.get("user")
    uid: str = user.get("uid")
    unit = crud.get_unit(db, ref.id)
    if not unit:
        raise HTTPException(404, detail="Unit not found")
    enrollment = crud.get_enrollment(db, unit.course_id, unit.course_semester, uid)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    if is_admin(db, request) or enrollment.role in ["lecturer", "teaching assistant"]:
        return crud.update_unit_hidden(db=db, unit_id=unit.id, hidden=ref.hidden)
    raise HTTPException(
        403, detail="You do not have permission to create a unit for this course"
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
    # request: Request, ref: schemas.ReportCreate, db: Session = Depends(get_db)
):
    # if not is_logged_in(request):
    #     raise HTTPException(401, detail="You are not logged in")

    # user = request.session.get("user")
    # uid: str = user.get("uid")
    # enrollment = crud.get_enrollment(db, ref.course_id, ref.course_semester, uid)
    if (
        True
        # is_admin(db, request) or enrollment.role in ["lecturer"]
    ):
        # TODO: Code that gets the data from ai.
        with open("hello.txt", "w") as f:
            f.write(f"Hello world!")

        path = os.getcwd() + "/hello.txt"
        return FileResponseWithDeletion(path, filename="hello.txt")

    return Response(status_code=403)


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# Get unit data with course and semester required, better error handling/security (unit_id is just an incrementing number)
# Example: /unit_data?course_id=TDT4100&course_semester=fall2023&unit_id=1
@app.get("/unit_data", response_model=schemas.UnitData)
async def get_unit_data(
    request: Request,
    course_id: str,
    course_semester: str,
    unit_id: int,
    db: Session = Depends(get_db),
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

    user = request.session.get("user")
    email: str = user.get("eduPersonPrincipalName")
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
        # Somehow needed to get reflections on Unit dict, even thought its never accessed
        reflections = [to_dict(reflection) for reflection in unit.reflections]

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


@app.post("/report", response_model=schemas.Report)
async def create_report(ref: schemas.ReportCreate, db: Session = Depends(get_db)):
    return crud.create_report(db, report=ref.model_dump())


@app.get("/report/{course_id}/{unit_id}", response_model=schemas.ReportBase)
async def get_report(
    request: Request, course_id: str, unit_id: int, db: Session = Depends(get_db)
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")
    report = crud.get_report(db, course_id=course_id, unit_id=unit_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# Also created new report if not created
@app.post("/edit_created_report", response_model=schemas.Report)
async def edit_created_report(
    request: Request, ref: schemas.ReportCreate, db: Session = Depends(get_db)
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

    user = request.session.get("user")
    uid: str = user.get("uid")
    enrollment = crud.get_enrollment(db, ref.course_id, ref.course_semester, uid)
    if enrollment is None:
        raise HTTPException(401, detail="You are not enrolled in the course")
    if is_admin(db, request) or enrollment.role in ["lecturer", "teaching assistant"]:
        return crud.edit_created_report(
            db,
            ref.course_id,
            ref.unit_id,
            ref.report_content,
            course_semester=ref.course_semester,
        )
    raise HTTPException(
        403, detail="You do not have permission to edit report for this course"
    )


# create new invitation
@app.post("/create_invitation", response_model=schemas.Invitation)
async def create_invitation(
    request: Request, ref: schemas.InvitationBase, db: Session = Depends(get_db)
):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")
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
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

    user = request.session.get("user")
    uid: str = user.get("uid")

    return crud.get_invitations(db, uid)


# delete invitation
@app.delete("/delete_invitation/{id}")
async def delete_invitation(request: Request, id: int, db: Session = Depends(get_db)):
    if not is_logged_in(request):
        raise HTTPException(401, detail="You are not logged in")

    return crud.delete_invitation(db, id=id)


@app.post("/send-notifications")
async def send_notifications(db: Session = Depends(get_db)):
    """
    Sends reminder notifications to students about units they need to provide feedback for.

    This function iterates over all courses and their enrolled students, identifying units
    for which students have not yet reached the notification limit. It then sends a reminder
    email to each student about their pending units, updating the notification count for each unit
    per student.

    Parameters:
    - db (Session): The database session used to perform database operations.

    Raises:
    - HTTPException: If a notification has already been sent within the cooldown period defined
      by NOTIFICATION_COOLDOWN_DAYS.

    Returns:
    - JSONResponse: A summary of the notification sending process, including information on
      successful notifications, skipped notifications due to the notification limit, and any errors encountered.
    """
    if crud.check_recent_notification(db, NOTIFICATION_COOLDOWN_DAYS):
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

    Parameters:
    - student_id (str): The unique identifier of the student receiving the email.
    - course_id (str): The unique identifier of the course for which feedback is requested.
    - units (List[model.Unit]): A list of Unit objects representing the learning units for which feedback is requested.

    Returns:
    - str: A string containing the HTML content for the email body.
    """
    unit_links = "".join(
        [
            f'<li><a href="https://ref.iik.ntnu.no/app/courseview/{unit.course_semester}/{unit.course_id}/{unit.id}">{unit.title}</a></li>'
            for unit in units
        ]
    )

    return f"""<p>Dear {student_id},</p>
    <p>This is a reminder to share your thoughts regarding the recent learning units in {course_id}:</p>
    <ul>{unit_links}</ul>
    <p>Your input will directly contribute to improving the lectures for your benefit and the benefit of future students. Your feedback will be shared with your lecturer to help them tailor their teaching approach to your needs.</p>
    <p>Best regards,<br/>The Reflection Tool Team</p>"""


@app.post("/analyze_feedback")
async def analyze_feedback(ref: schemas.ReflectionJSON):
    data_dicts = [item.model_dump() for item in ref.data]
    return analyze_student_feedback(ref.api_key, data_dicts, ref.use_cheap_model)


# ---------------------------------Code that was meant to send email to students --------#
# @app.post("/invitation_email/{course_id}")
# async def simple_send(email: EmailSchema, course_id:str) -> JSONResponse:
#     html = f"""

#         <p>Hi!</p>
#         <p></p>
#         <p>You have been invited to join {course_id}! Accept the invitation and give your first reflection on <a href="https://ref2.iik.ntnu.no/">ref2.iik.ntnu.no</a>.</p>
#         <br>
#         <br>
#         <br>
# 	    <p>Sincerely,</p>
#         <p></p>
#         <p>NTNU Reflection</p>
#         <br>
#         <br>
# 	    <p>This is an automated email notification, contact your lecturer if you are experiencing any issues.</p>


#         """

#     message = MessageSchema(
#         subject=f"Invitation to join {course_id}",
#         recipients=email.dict().get("email"),
#         body=html,
#         subtype=MessageType.html)

#     fm = FastMail(email_config)
#     await fm.send_message(message)
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})

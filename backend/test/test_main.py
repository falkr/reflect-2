import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db, is_logged_in  # Adjust the import path as necessary
from app import crud  # Adjust the import path as necessary
from fastapi import Request

# Setup for the test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

users = {
    "test": {"uid": "test", "email": "test@example.com"},
    "admin": {"uid": "admin", "email": "test_admin@example.com"},
}


@app.get("/test/set-test-user")
def set_test_user(request: Request, uid: str, email: str):
    """
    Sets the test user session data with dynamic values.

    Args:
        request (Request): The FastAPI request object.
        uid (str): The user ID.
        email (str): The user email.

    Returns:
        None
    """
    request.session["user"] = {
        "uid": uid,
        "mail": email,
    }


def create_user(uid: str, email: str, admin: bool = False) -> None:
    """
    Creates a user in the test database.

    Args:
        uid (str): The user ID.
        email (str): The user email.
        admin (bool, optional): Whether the user is an admin. Defaults to False.

    Returns:
        None
    """
    db = TestingSessionLocal()
    crud.create_user(db=db, uid=uid, user_email=email, admin=admin)
    db.commit()
    db.close()


def login_user(uid: str, email: str) -> None:
    """
    Logs in a user by setting the test user session data.

    Args:
        uid (str): The user ID.
        email (str): The user email.

    Returns:
        None
    """
    client.get(f"/test/set-test-user?uid={uid}&email={email}")


@pytest.mark.asyncio
def test_user_endpoint():
    """
    Test case for the user endpoint.

    This test case creates a test user, logs in the user, and then sends a GET request to the /user endpoint.
    It asserts that the response status code is 200 and checks the returned data against the expected values.
    """
    uid = users["test"]["uid"]
    test_user_email = users["test"]["email"]

    create_user(uid, test_user_email)
    login_user(uid, test_user_email)

    response = client.get("/user")
    assert response.status_code == 200
    data = response.json()

    assert data["uid"] == uid
    assert data["email"] == test_user_email
    assert data["admin"] == False
    assert data["reflections"] == []
    assert data["enrollments"] == []


@pytest.mark.asyncio
def test_admin_user():
    """
    Test case for creating and logging in an admin user.

    Steps:
    1. Create an admin user with the given uid and email.
    2. Log in the admin user.
    3. Send a GET request to "/user" endpoint.
    4. Verify that the response contains the correct user information.

    Expected behavior:
    - The user's uid, email, and admin status should match the provided values.
    """

    uid = users["admin"]["uid"]
    admin_email = users["admin"]["email"]
    create_user(uid, admin_email, True)
    login_user(uid, admin_email)

    response = client.get("/user")
    data = response.json()

    assert data["uid"] == uid
    assert data["email"] == admin_email
    assert data["admin"] == True


@pytest.mark.asyncio
def test_create_course_non_admin():
    """
    Test case for creating a course by a non-admin user.
    """
    uid = users["test"]["uid"]
    test_user_email = users["test"]["email"]
    login_user(uid, test_user_email)

    response = client.post(
        "/create_course",
        json={
            "name": "Introduction to lorem ipsum",
            "id": "TDT1000",
            "semester": "fall2023",
        },
    )

    print(response.json())

    assert response.status_code == 403


@pytest.mark.asyncio
def test_create_course_admin():
    """
    Test case for:
    - Creating a course by an admin user.
    - Enrolling as a teacher in the course.
    - Verifying that the course was created and the user was enrolled.
    """
    uid = users["admin"]["uid"]
    admin_email = users["admin"]["email"]
    login_user(uid, admin_email)

    response = client.post(
        "/create_course",
        json={
            "name": "Introduction to lorem ipsum",
            "id": "TDT1000",
            "semester": "fall2023",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/enroll",
        json={
            "course_id": "TDT1000",
            "course_semester": "fall2023",
            "role": "lecturer",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["role"] == "lecturer"
    assert data["course_id"] == "TDT1000"
    assert data["uid"] == uid

    response = client.get("/user")
    data = response.json()

    assert data["uid"] == uid
    assert data["reflections"] == []
    assert data["enrollments"] == [
        {
            "course_id": "TDT1000",
            "course_semester": "fall2023",
            "role": "lecturer",
            "uid": uid,
        }
    ]


@pytest.mark.asyncio
def test_enroll_student():
    """
    Test case for enrolling a user as a student in a course.
    """
    uid = users["test"]["uid"]
    test_user_email = users["test"]["email"]
    login_user(uid, test_user_email)

    response = client.post(
        "/enroll",
        json={
            "course_id": "TDT1000",
            "course_semester": "fall2023",
            "role": "student",
        },
    )

    assert response.status_code == 200

    response = client.get("/user")
    data = response.json()

    assert data["uid"] == uid
    assert data["reflections"] == []
    assert data["enrollments"] == [
        {
            "course_id": "TDT1000",
            "course_semester": "fall2023",
            "role": "student",
            "uid": uid,
        }
    ]


@pytest.mark.asyncio
def test_get_units():
    """
    Test case for getting the units of a course.
    """
    login_user(users["test"]["uid"], users["test"]["email"])
    response = client.get("/units?course_id=TDT1000&course_semester=fall2023")
    assert response.status_code == 200
    data = response.json()

    assert data == []


# test for create_unit
@pytest.mark.asyncio
def test_create_unit():
    """
    Test case for creating a unit in a course.
    """
    login_user(users["admin"]["uid"], users["admin"]["email"])
    response = client.post(
        "/create_unit",
        json={
            "hidden": False,
            "title": "tittel1",
            "date_available": "2022-08-23 00:00:00",
            "course_id": "TDT1000",
            "course_semester": "fall2023",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["hidden"] == False
    assert data["title"] == "tittel1"
    assert data["reflections"] == []

    response = client.get("/units?course_id=TDT1000&course_semester=fall2023")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["hidden"] == False
    assert data[0]["title"] == "tittel1"


@pytest.mark.asyncio
def test_create_reflection():
    """
    Test case for creating a reflection in a unit.
    """
    login_user(users["test"]["uid"], users["test"]["email"])
    response = client.post(
        "/reflection",
        json={
            "body": "reflections test",
            "user_id": "test",
            "unit_id": 1,
            "question_id": 1,
        },
    )
    assert response.status_code == 200

    response = client.get("/user")
    data = response.json()

    assert data["reflections"] == [
        {"body": "reflections test", "user_id": "test", "unit_id": 1, "question_id": 1}
    ]

    response = client.get("/units?course_id=TDT1000&course_semester=fall2023")
    data = response.json()

    assert data[0]["reflections"][0]["body"] == "reflections test"

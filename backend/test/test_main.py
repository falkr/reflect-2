from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.main import (
    app,
    is_admin,
)
from api import crud
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
    assert data["enrollments"][0]["role"] == "lecturer"


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
    assert data["enrollments"][0]["role"] == "student"


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
async def test_get_course():
    """
    Test case for getting a course.
    """
    login_user(users["test"]["uid"], users["test"]["email"])
    response = client.get("/course?course_id=TDT1000&course_semester=fall2023")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "TDT1000"
    assert data["semester"] == "fall2023"
    assert data["name"] == "Introduction to lorem ipsum"
    assert data["responsible"] == ""
    assert data["website"] == ""


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


@pytest.mark.asyncio
def test_analyze_feedback_invalid_data():
    """
    Test the /analyze_feedback endpoint with invalid data.
    """
    # Construct an invalid request payload
    request_payload = {
        # Missing or invalid fields here
    }

    response = client.post("/analyze_feedback", json=request_payload)

    assert response.status_code == 422


@pytest.mark.asyncio
def test_generate_report_invalid_data():
    """
    Test the /generate_report endpoint with invalid data.
    """
    # Construct an invalid request payload
    request_payload = {
        # Missing or invalid fields here
    }

    response = client.post("/generate_report", json=request_payload)

    assert response.status_code == 422


mock_db = MagicMock(spec=Session)
mock_request = MagicMock(spec=Request)


def config_side_effect(key, cast=None, default=None):
    if key == "isAdmin":
        return False
    return default


@pytest.fixture
def config_patch():
    with patch("api.main.config") as mock_config:
        mock_config.side_effect = config_side_effect
        yield mock_config


@pytest.fixture
def crud_patch():
    with patch("api.main.crud") as mock_crud:
        yield mock_crud


def session_get_side_effect(key, default=None):
    if key == "user":
        return None
    return default


def test_is_admin_with_admin_config(config_patch):
    def local_config_side_effect(key, cast=None, default=None):
        if key == "isAdmin":
            return True
        return default

    config_patch.side_effect = local_config_side_effect

    mock_request.session.get.side_effect = session_get_side_effect

    assert is_admin(mock_db, mock_request) == True


def test_is_admin_no_user_logged_in(config_patch):
    mock_request.session.get.side_effect = lambda key, default=None: default
    assert is_admin(mock_db, mock_request) == False


def test_is_admin_user_not_in_db(config_patch, crud_patch):
    config_patch.return_value = MagicMock(return_value=False)
    crud_patch.get_user.return_value = None
    mock_request.session.get.side_effect = lambda key, default=None: (
        {"uid": "testuid"} if key == "user" else default
    )
    assert is_admin(mock_db, mock_request) == False


def test_is_admin_user_not_admin(config_patch, crud_patch):
    config_patch.return_value = MagicMock(return_value=False)
    crud_patch.get_user.return_value = MagicMock(admin=False)
    mock_request.session.get.side_effect = lambda key, default=None: (
        {"uid": "testuid"} if key == "user" else default
    )
    assert is_admin(mock_db, mock_request) == False


def test_is_admin_user_is_admin(config_patch, crud_patch):
    config_patch.return_value = MagicMock(return_value=False)
    crud_patch.get_user.return_value = MagicMock(admin=True)
    mock_request.session.get.side_effect = lambda key, default=None: (
        {"uid": "testuid"} if key == "user" else default
    )
    assert is_admin(mock_db, mock_request) == True


@pytest.mark.asyncio
async def test_generate_report_non_admin_access():
    # Simulate a non-admin user session
    login_user(users["test"]["uid"], users["test"]["email"])

    # Attempt to generate a report
    response = client.post(
        "/generate_report",
        json={
            # Provide necessary request payload here
            "course_id": "TDT1000",
            "unit_id": 1,
            "course_semester": "fall2023",
        },
    )

    # Assert that access is forbidden for non-admin users
    assert response.status_code == 403


def test_save_report_admin_user():
    with patch("api.main.is_admin", return_value=True), patch(
        "api.main.crud.save_report"
    ) as mock_save_report:
        test_report_data = {
            "report_content": {"section1": {"subsection1": ["item1", "item2"]}},
            "number_of_answers": 5,
            "unit_id": 1,
            "course_id": "course123",
            "course_semester": "2023S",
        }
        expected_response_data = test_report_data.copy()
        mock_save_report.return_value = {"id": 1, **test_report_data}
        response = client.post("/save_report", json=test_report_data)
        assert response.status_code == 200
        assert response.json() == expected_response_data


def test_save_report_access_denied_for_non_admin_user():
    with patch("api.main.is_admin", return_value=False):
        test_report_data = {
            "report_content": {"section1": {"subsection1": ["item1", "item2"]}},
            "number_of_answers": 5,
            "unit_id": 1,
            "course_id": "course123",
            "course_semester": "2023S",
        }
        response = client.post("/save_report", json=test_report_data)
        assert response.status_code == 403
        assert response.json() == {"detail": "You are not an admin user"}


def test_save_report_integrity_error():
    with patch("api.main.is_admin", return_value=True), patch(
        "api.main.crud.save_report", side_effect=IntegrityError(None, None, None)
    ):
        test_report_data = {
            "report_content": {"section1": {"subsection1": ["item1", "item2"]}},
            "number_of_answers": 5,
            "unit_id": 1,
            "course_id": "course123",
            "course_semester": "2023S",
        }
        response = client.post("/save_report", json=test_report_data)
        assert response.status_code == 409
        assert "An error occurred while saving the report:" in response.json()["detail"]

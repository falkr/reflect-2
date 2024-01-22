from datetime import date
from typing import Any, List

from pydantic import BaseModel, EmailStr


class ReflectionBase(BaseModel):
    body: str
    user_id: str
    unit_id: int
    question_id: int

    class Config:
        orm_mode = True


class Reflection(ReflectionBase):
    id: int
    timestamp: date

    class Config:
        orm_mode = True


class ReflectionCreate(ReflectionBase):
    pass


class ReflectionDetail(ReflectionBase):
    id: int
    category: str
    is_interesting: bool
    is_problematic: bool
    is_sorted: bool


class UnitBase(BaseModel):
    hidden: bool
    title: str
    date_available: date
    course_id: str
    course_semester: str

    class Config:
        orm_mode = True


class UnitCreate(UnitBase):
    pass

class UnitHidden(BaseModel):
    id: int
    hidden: bool


class Unit(UnitBase):
    id: int
    reflections: list[Reflection] = []

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    id: int
    question: str
    comment: str

    class Config:
        orm_mode = True


class Question(QuestionBase):
    courses: list[Any] = []

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    id: str
    semester: str

    class Config:
        orm_mode = True


class CourseCreate(CourseBase):
    name: str


class EnrollmentBase(BaseModel):
    course_id: str
    course_semester: str
    role: str

    class Config:
        orm_mode = True


class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollUser(EnrollmentBase):
    user_email: str


class Enrollment(EnrollmentBase):
    user_email: str


class UserAdmin(BaseModel):
    admin: bool

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class InvitationBase(BaseModel):
    course_id: str
    course_semester: str
    email: str
    role: str

    class Config:
        orm_mode = True


class InvitationCreate(InvitationBase):
    pass


class Invitation(InvitationBase):
    id: int
    course_id: str
    course_semester: str
    email: str
    role: str


class User(UserBase):
    enrollments: list[Enrollment] = []
    reflections: list[ReflectionBase] = []
    admin: bool

    class Config:
        orm_mode = True


class ReportBase(BaseModel):
    report_content: list[dict] = []
    unit_id: int
    course_id: str
    course_semester: str

    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    pass


class Course(CourseBase):
    name: str
    responsible: str
    website: str
    questions: list[QuestionBase] = []
    users: list[EnrollmentBase] = []
    reports: list[ReportBase] = []

    class Config:
        orm_mode = True


class Report(BaseModel):
    id: int
    unit: Unit
    course: Course

    class Config:
        orm_mode = True


class EmailSchema(BaseModel):
    email: List[EmailStr]

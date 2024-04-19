from datetime import date
from typing import Any, Dict, List, Union

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


class UnitDelete(BaseModel):
    course_id: str
    course_semester: str


class ReportBase(BaseModel):
    report_content: Union[list[dict], dict] = {}
    number_of_answers: int
    unit_id: int
    course_id: str
    course_semester: str

    class Config:
        orm_mode = True


class Unit(UnitBase):
    id: int
    reflections: list[Reflection] = []
    reflections_since_last_report: int
    reports: List[ReportBase] = []

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


class UnitData(BaseModel):
    unit: Unit
    unit_questions: List[QuestionBase] = []

    class Config:
        orm_mode = True


class CourseBase(BaseModel):
    id: str
    semester: str

    class Config:
        orm_mode = True


class Question(BaseModel):
    question: str
    comment: str


class CourseCreate(CourseBase):
    name: str
    questions: List[Question] = []


class EnrollmentBase(BaseModel):
    course_id: str
    course_semester: str
    role: str

    class Config:
        orm_mode = True


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollUser(EnrollmentBase):
    uid: str


class Enrollment(EnrollmentBase):
    uid: str
    missingUnits: Any = []


class UserAdmin(BaseModel):
    admin: bool

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    uid: str
    email: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class InvitationBase(BaseModel):
    course_id: str
    course_semester: str
    uid: str
    role: str

    class Config:
        orm_mode = True


class InvitationCreate(InvitationBase):
    pass


class Invitation(InvitationBase):
    id: int
    course_id: str
    course_semester: str
    uid: str
    role: str


class User(UserBase):
    enrollments: list[Enrollment] = []
    reflections: list[ReflectionBase] = []
    admin: bool

    class Config:
        orm_mode = True


class AutomaticReport(BaseModel):
    unit_id: int
    course_id: str
    course_semester: str

    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    report_content: Dict[str, Dict[str, List[str]]] = {}
    pass


class AnalyzeReportCreate(ReportBase):
    report_content: Any
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


class ReflectionJSONFormat(BaseModel):
    answers: List[str]


class ReflectionJSON(BaseModel):
    api_key: str
    questions: List[str]
    student_feedback: List[ReflectionJSONFormat]
    use_cheap_model: bool

type User = {
	email: string;
	enrollments: Enrollment[];
	reflections: Reflection[];
	admin: boolean;
};

type Enrollment = {
	user_email: string;
	course_id: string;
	role: string;
};

type Course = {
	name: string;
	id: string;
	semester: string;
	responsible: string;
	website: string;
	questions: Question[];
	users: Enrollment[];
	reports: Report[];
};

type Unit = {
	id: number;
	hidden: boolean;
	seq_no: number;
	title: string;
	date_available: Date;
	course_id: string;
	course: Course;
	reflections: reflections[];
};

type Question = {
	id: number;
	question: string;
	comment: string;
	courses: Course[];
};

type Reflection = {
	id: number;
	body: string;
	timestamp: Date;
	category: string;
	is_interesting: boolean;
	is_problematic: boolean;
	is_sorted: boolean;
	user_id: number;
	user: User;
	unit_id: number;
	unit: Unit;
	question_id: number;
};

type Report = {
	report_content: report_obj[];
	unit_id: number;
	course_id: number;
};

type report_obj = {
	name: string;
	answers: string[];
}


type Invitation = {
	id: number;
	email: string;
	role: string;
	course_id: string;
	course_semester: string;
};

type answers_by_questions = {
	questionID: number;
	answers: string[];
};

type question_answers = {
	list: answers_by_questions[];
};

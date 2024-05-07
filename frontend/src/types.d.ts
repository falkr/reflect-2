type User = {
	email: string;
	uid: string;
	enrollments: Enrollment[];
	reflections: Reflection[];
	admin: boolean;
	detail?: string;
};

type ReportType =
	| {
			report_content: report_obj[];
			unit_id: number;
			course_id: number;
			course_semester: string;
			number_of_answers: number;
	  }
	| undefined;

type Enrollment = {
	uid: string;
	course_id: string;
	course_semester: string;
	role: string;
	course_name: string;
	missingUnits: Any[];
};

type Course = {
	name: string;
	id: string;
	semester: string;
	responsible: string;
	website: string;
	questions: Question[];
	users: Enrollment[];
	reports: ReportType[];
};

type Unit = {
	id: number;
	hidden: boolean;
	seq_no: number;
	title: string;
	date_available: Date;
	course_id: string;
	course_semester: string;
	course: Course;
	reflections: reflections[];
	reflections_since_last_report: number;
	unit_number: number;
	total_reflections: number;
	reports: ReportType[];
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

type report_obj = {
	name: string;
	answers: string[];
};

type Invitation = {
	id: number;
	uid: string;
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

type Data = {
	user: User;
	course: Course;
	course_name: string;
	role: string;
	units: Unit[];
};

type Response = {
	status: number;
	message: string;
};

type FormValues = {
	email: string;
	role: string[];
	title: string[];
	name: string[];
	semester: string[];
	course_id: string[];
};

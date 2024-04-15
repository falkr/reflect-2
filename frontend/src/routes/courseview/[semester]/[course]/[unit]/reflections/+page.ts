import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, parent }) => {
	const { user, course, units } = await parent();

	const parsedUser = user as User;
	const role = parsedUser.enrollments.find(
		(enrollment) => enrollment.course_id === course.id
	)?.role;

	if (role === 'student') {
		throw redirect(302, `/courseview/${params.course}`);
	}

	const unitID = parseInt(params.unit) as number;
	const unitName = units.find((unit: Unit) => unit.id == unitID)?.title;
	const answers: Reflection[] = [];

	type answers_by_questions = {
		questionID: number;
		answers: string[];
	};

	type question_answers = {
		list: answers_by_questions[];
	};

	// create an object to store the answers for each question
	const questions = course.questions;
	const reports = course.reports as ReportType[];

	const unitReportContent = reports?.filter((report: ReportType) => report?.unit_id == unitID)[0];

	//hente ut alle refleksjoner for en unit
	units.forEach((unit: Unit) => {
		if (unit.id == unitID) {
			unit.reflections.forEach((reflection: Reflection) => {
				answers.push(reflection);
			});
		}
	});

	const questionAnswers: question_answers = {
		list: []
	};

	answers.forEach((reflection) => {
		//så lager objekter
		const answerByQuestion: answers_by_questions = {
			questionID: reflection.question_id,
			answers: [reflection.body]
		};

		//Hvis listen inneholder det objekter med samme question id som den vi er på
		if (
			questionAnswers.list.filter((item) => item.questionID === answerByQuestion.questionID)
				.length > 0
		) {
			questionAnswers.list.filter((item) => item.answers.push(answerByQuestion.answers[0]));
		} else {
			questionAnswers.list.push(answerByQuestion);
		}
	});

	return {
		course: course as Course,
		unit_id: unitID,
		user: user as User,
		answers: answers,
		questions: questions,
		units: units,
		unitReportContent: unitReportContent as ReportType,
		unitName: unitName
	};
};

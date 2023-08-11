import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, parent }) => {
	const { user, course } = await parent();

	const parsedUser = user as unknown as User;
	const parsedCourse = course as unknown as Course;
	let role = parsedUser.enrollments.find((enrollment) => enrollment.course_id === course.id)?.role;

	if (role === 'student') {
		throw redirect(302, `/app/courseview/${params.course}`);
	}

	const unitID = params.unit as unknown as number;
	const unitName = parsedCourse.units.find((unit) => unit.id == unitID)?.title;
	const answers: Reflection[] = [];

	type answers_by_questions = {
		questionID: number;
		answers: string[];
	};

	type question_answers = {
		list: answers_by_questions[];
	};

	// create an object to store the answers for each question
	const units: Unit[] = course.units;
	const questions = course.questions;
	const reports = course.reports as unknown as Report[];
	const users = course.users;

	const unitReportContent = reports.filter((report) => report.unit_id == unitID)[0];

	//hente ut alle refleksjoner for en unit
	units.forEach((unit) => {
		if (unit.id == unitID) {
			unit.reflections.forEach((reflection) => {
				answers.push(reflection);
			});
		}
	});

	let questionAnswers: question_answers = {
		list: []
	};

	answers.forEach((reflection) => {
		//så lager objekter
		const answerByQuestion: answers_by_questions = {
			questionID: reflection.question_id,
			answers: [reflection.body]
		};

		//Hvis listen inneholder det objekter med samme question id som den vi er på
		if (questionAnswers.list.filter((item) => item.questionID === answerByQuestion.questionID).length > 0) {
			questionAnswers.list.filter((item) => item.answers.push(answerByQuestion.answers[0]));
		} else {
			questionAnswers.list.push(answerByQuestion);
		}
	});

	return {
		course: course as unknown as Course,
		unit_id: unitID,
		user: user as unknown as User,
		answers: answers,
		questions: questions,
		units: units,
		unitReportContent: unitReportContent,
		unitName: unitName
	};
};

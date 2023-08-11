import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from '../../$types';

export const load: PageServerLoad = async ({ params, parent }) => {
	const { user, course } = await parent();
	const parsedUser = user as unknown as User;
	let role = parsedUser.enrollments.find((enrollment) => enrollment.course_id === course.id)?.role;

	if (role === 'student') {
		throw redirect(302, `/app/courseview/${params.course}`);
	}

	const unitID = params.report as unknown as number;
	const reports = course.reports as unknown as Report[];

	const unitReportContent = reports.filter((report) => report.unit_id == unitID)[0];

	return {
		course: course as unknown as Course,
		unit_id: unitID,
		user: user as unknown as User,
		unitReportContent: unitReportContent
	};
};

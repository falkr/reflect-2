import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, parent }) => {
	const { user, course } = await parent();
	const parsedUser = user as User;
	const role = parsedUser.enrollments.find(
		(enrollment) => enrollment.course_id === course.id
	)?.role;

	if (role === 'student') {
		throw redirect(302, `/app/courseview/${params.course}`);
	}

	const unitID = Number(params.report);
	const reports = course.reports;

	const unitReportContent = reports.find((report: ReportType) => report.unit_id === unitID);

	return {
		course: course as Course,
		unit_id: unitID,
		user: user as User,
		unitReportContent: unitReportContent as ReportType
	};
};

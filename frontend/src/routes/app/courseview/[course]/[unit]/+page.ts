import { error, redirect } from '@sveltejs/kit';
import { PUBLIC_API_URL } from '$env/static/public';

export const load = async ({ params, parent, depends }) => {
	const { course, user, units } = await parent();
	let course_type = course as Course;

	//check if unit exists in course, if not redirect to courseview
	if (units.filter((unit) => unit.id == parseInt(params.unit)).length > 0 === false) {
		//redirects the user to the courseview page
		throw redirect(302, `/app/courseview/${params.course}`);
	}

	//If the user have reflected or not
	let reflected: boolean =
		user.reflections.filter((reflection) => reflection.unit_id == parseInt(params.unit)).length > 0;

	//date today
	let today = new Date();

	//date of unit
	let unitDate = units.filter((unit) => unit.id == parseInt(params.unit))[0].date_available;

	let date = new Date(unitDate);

	//if date is expired or not
	let available = today > date;

	return {
		user: user as unknown as User,
		course: course as unknown as Course,
		unit_id: params.unit as unknown as number,
		reflected: reflected,
		available: available,
		units: units as unknown as Unit[]
	};
};

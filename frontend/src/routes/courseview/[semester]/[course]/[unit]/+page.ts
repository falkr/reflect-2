import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { PUBLIC_API_URL } from '$env/static/public';

export const load: PageLoad = async ({ params, parent }) => {
	const { course, user, units } = await parent();

	//check if unit exists in course, if not redirect to courseview
	const unitId = params.unit ? parseInt(params.unit, 10) : null;
	if (unitId === null || !units.some((unit: Unit) => unit.id === unitId)) {
		throw redirect(302, `/courseview/${params.course}`);
	}

	//If the user have reflected or not
	const reflectionUnitId = params.unit ? parseInt(params.unit, 10) : null;
	const reflected = user.reflections.some(
		(reflection: Reflection) => reflection.unit_id === reflectionUnitId
	);

	// Date today
	const today = new Date();

	// Date of unit
	const unit = units.find((unit: Unit) => unit.id === unitId);
	const unitDate = unit ? unit.date_available : null;

	// Check that unitDate is not null before converting to Date object
	const date = unitDate ? new Date(unitDate) : null;

	// If date is expired or not
	const available = date ? today > date : false;

	let unitData;
	try {
		const response = await fetch(
			`${PUBLIC_API_URL}/unit_data?course_id=${course.id}&course_semester=${course.semester}&unit_id=${unitId}`,
			{
				credentials: 'include'
			}
		);
		if (!response.ok) {
			throw new Error('Failed to fetch unit data');
		}
		unitData = await response.json();
	} catch (error) {
		console.error('Error fetching unit data:', error);
	}

	return {
		user: user as User,
		course: course as Course,
		unit_id: unitId as number,
		reflected: reflected,
		available: available,
		unit: unitData,
		units: units as Unit[]
	};
};

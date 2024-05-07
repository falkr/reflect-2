import { error } from '@sveltejs/kit';
import { PUBLIC_API_URL } from '$env/static/public';
import type { Load } from '@sveltejs/kit';

/**
 * Loads data necessary for rendering a course overview page in a SvelteKit application.
 * This includes fetching user details, course details, and units associated with the course.
 * @param parent - A function to invoke the parent load function, which generally handles user authentication.
 * @param params - Parameters of the current route, expected to contain `course` and `semester` identifiers.
 * @param fetch - A function to make authenticated requests from the server-side. It’s similar to the global fetch but can handle cookies and other credentials.
 * @param depends - Used to declare dependencies for this load call which invalidates the data when the specified key changes.
 *
 * @returns {Promise<Object>} - A promise that resolves to an object containing user, course, course_name, role, and units. This data shapes the initial state of the page.
 *
 * @throws {Error} - Throws an HTTP 404 error if the course or its units are not found.
 * @throws {Error} - Throws an HTTP 401 error if the user is not enrolled in the course.
 */
export const load: Load = async ({ parent, params, fetch, depends }) => {
	//depends this load function for updating site on unit creation

	//fetch from parent
	const { user } = await parent();

	//fetch course
	const response = await fetch(
		`${PUBLIC_API_URL}/course?course_id=${params.course}&course_semester=${params.semester}`,
		{
			credentials: 'include'
		}
	);

	//if course not found, throw error
	if (response.status === 404) {
		throw error(404, 'Course not found');
	}

	//parse course
	const course = (await response.json()) as Course;

	//fetch units
	const unit_res = await fetch(
		`${PUBLIC_API_URL}/units?course_id=${params.course}&course_semester=${params.semester}`,
		{
			credentials: 'include'
		}
	);

	//if course not found, throw error
	if (unit_res.status === 404) {
		throw error(404, 'Course for units not found');
	}

	//parse units
	const units = (await unit_res.json()) as Unit[];

	//parse user
	const user_parsed = user as User;
	//get role of user in enrolled course
	const role = user_parsed.enrollments.find(
		(enrollment) => enrollment.course_id === course.id
	)?.role;

	//if role is undefined (meaning youre not enrolled), throw error
	if (role === undefined) {
		throw error(401, 'Not enrolled and authorized for the Course');
	}

	depends('app:courseOverview');
	return { user: user as User, course, course_name: params.course, role, units };
};

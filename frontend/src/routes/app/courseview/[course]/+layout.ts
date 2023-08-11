import { error, redirect } from '@sveltejs/kit';
import { PUBLIC_API_URL } from '$env/static/public';

//fetches course
export const load = async ({ parent, params, fetch, depends }) => {
	//depends this load function for updating site on unit creation
	
	//fetch from parent
	const { user } = await parent();
	
	//fetch course
	const response = await fetch(`${PUBLIC_API_URL}/course?course_id=${params.course}`, {
		credentials: 'include'
	});
	
	
	//if course not found, throw error
	if (response.status === 404) {
		throw error(404, 'Course not found');
	}
	
	//parse course
	const course = (await response.json()) as unknown as Course;
	
	//parse user
	let user_parsed = user as unknown as User;
	//get role of user in enrolled course
	let role = user_parsed.enrollments.find((enrollment) => enrollment.course_id === course.id)?.role;
	
	//if role is undefined (meaning youre not enrolled), throw error
	if (role === undefined) {
		throw error(401, 'Not enrolled and authorized for the Course');
	}
	
	depends('app:courseOverview');
	return { user: user as unknown as User, course, course_name: params.course, role };
};

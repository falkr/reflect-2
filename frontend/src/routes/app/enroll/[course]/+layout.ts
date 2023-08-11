import { error, redirect } from '@sveltejs/kit';
import { goto } from '$app/navigation';
import { PUBLIC_API_URL, PUBLIC_CURRENT_SEMESTER } from '$env/static/public';

//fetches course
export const load = async ({ parent, params, fetch, depends }) => {
	//depends this load function for updating site on unit creation

	//fetch from parent
	const { user } = await parent();

	const response = await fetch(`${PUBLIC_API_URL}/enroll`, {
		method: 'POST',
		credentials: 'include',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			course_id: params.course,
			course_semester: PUBLIC_CURRENT_SEMESTER,
			role: 'student'
		})
	});
	console.log(response.body);

	if (response.ok) {
		goto(`/app/courseview/${params.course}`);
	} else {
		throw error(401, 'User could not be registered for this course');
	}
};

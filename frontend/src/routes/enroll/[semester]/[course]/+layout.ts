import { error } from '@sveltejs/kit';
import { goto } from '$app/navigation';
import { PUBLIC_API_URL } from '$env/static/public';
import type { Load } from '@sveltejs/kit';

//fetches course
export const load: Load = async ({ params, fetch }) => {
	//depends this load function for updating site on unit creation

	const response = await fetch(`${PUBLIC_API_URL}/enroll`, {
		method: 'POST',
		credentials: 'include',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			course_id: params.course,
			course_semester: params.semester,
			role: 'student'
		})
	});

	if (response.ok || response.status === 409) {
		goto(`/courseview/${params.course}`);
	} else {
		throw error(401, 'User could not be registered for this course');
	}
};

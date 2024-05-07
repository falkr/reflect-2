import { error } from '@sveltejs/kit';
import { goto } from '$app/navigation';
import { PUBLIC_API_URL } from '$env/static/public';
import type { Load } from '@sveltejs/kit';

/**
 * Attempts to enroll a user into a specified course by making a POST request to the backend.
 * This load function is triggered when navigating to a specific route, intended to enroll the user.
 *
 * @param {Object} params - Contains the parameters from the URL which are necessary for the API request, such as `course` and `semester`.
 * @param {Function} fetch - A function provided by SvelteKit for making server-side requests. It is configured to handle sessions and authentication.
 *
 * @throws {Error} - Throws a redirect error if the response is not OK (excluding status 409 which indicates duplicate enrollment).
 * If the user is not authorized or the registration fails for other reasons, it throws a 401 error with a message.
 *
 * @returns {void} - This function does not return a value but performs navigation using `goto` or throws an error based on the API response.
 */
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

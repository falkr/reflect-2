import { PUBLIC_API_URL } from '$env/static/public';
import type { PageLoad } from './$types';

/**
 * Fetches the current user's details from the backend using a predefined API endpoint.
 * This load function is specifically intended for use in a SvelteKit application where it is called
 * server-side during page rendering to ensure user data is available before the page is fully loaded.
 *
 * @param {Function} fetch - A SvelteKit-provided fetch function, configured to handle credentials and session management, used to make server-side requests.
 *
 * @returns {Promise<Object>} - A promise that resolves to an object containing the user's data. This object is then available to the page as a prop.
 */
export const load: PageLoad = async ({ fetch }) => {
	const user_url = `${PUBLIC_API_URL}/user`;
	const response = await fetch(user_url, { credentials: 'include' });

	const user = (await response.json()) as User;
	return { user };
};

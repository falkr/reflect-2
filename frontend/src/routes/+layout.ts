export const ssr = false;
import { get } from 'svelte/store';
import { goto } from '$app/navigation';
import { logged_in } from '$lib/stores.js';
import { PUBLIC_API_URL } from '$env/static/public';
import type { Load } from '@sveltejs/kit';
import toast from 'svelte-french-toast';

/**
 * Load function for a SvelteKit application that ensures the user is authenticated,
 * redirects users to the appropriate route post-login, and fetches user data. This function
 * runs on every page and is integral to handling user sessions and routing based on authentication status.
 *
 * @param {Function} fetch - A SvelteKit-provided fetch function, configured to handle credentials, used for server-side requests.
 * @param {Object} url - Contains the current URL object of the request.
 * @param {Function} depends - Used to declare dependencies for this load call which invalidates the data when the specified key changes.
 *
 * @returns {Promise<Object>|void} - Returns a promise resolving to an object containing the user's data if authenticated,
 * or performs redirection if the user is not authenticated or on fetching error.
 *
 * @throws {Error} - Outputs error to console and sets user authentication status to false in case of fetching errors. Redirects to home if needed.
 */
export const load: Load = async ({ fetch, url, depends }) => {
	depends('app:layoutUser');

	if (!get(logged_in)) {
		if (url.pathname !== '/') {
			goto('/');
		}
	} else {
		if (sessionStorage.getItem('savedRoute')) {
			goto(`${sessionStorage.getItem('savedRoute')}`);
			sessionStorage.removeItem('savedRoute');
		}
	}
	try {
		const user_url = `${PUBLIC_API_URL}/user`;

		const response = await fetch(user_url, { credentials: 'include' });

		if (response.status !== 200) {
			logged_in.set(false);
			if (url.pathname !== '/') {
				sessionStorage.setItem('savedRoute', window.location.pathname);
			}
			if (url.pathname !== '/') {
				goto('/');
			}
		}

		const user = (await response.json()) as User;

		return { user: user };
	} catch (error) {
		console.log('-------------- Error connecting to server. Contact support. --------------');
		toast.error('Error connecting to server. Contact lecturer.');
		console.log(error);

		logged_in.set(false);
		if (url.pathname !== '/') {
			sessionStorage.setItem('savedRoute', window.location.pathname);
		}
		if (url.pathname !== '/') {
			goto('/');
		}
		return {};
	}
};

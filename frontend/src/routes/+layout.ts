export const ssr = false;
import { get } from 'svelte/store';
import { goto } from '$app/navigation';
import { logged_in } from '$lib/stores.js';
import { PUBLIC_API_URL } from '$env/static/public';
import type { Load } from '@sveltejs/kit';
import toast from 'svelte-french-toast';

// load function that runs on every page, fetching user
// also handles redirecting to correct route after login if specific url was accessed before login
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
		toast.error('Error connecting to server. Contact support.');
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

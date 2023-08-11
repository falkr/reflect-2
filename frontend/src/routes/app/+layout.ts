import { get } from 'svelte/store';
import { goto } from '$app/navigation';
import { logged_in } from '$lib/stores.js';
import { PUBLIC_API_URL } from '$env/static/public';

//load function that runs on every page, fetching user
export const load = async ({ fetch, depends }) => {

	depends('app:layoutUser');
	
	if (!get(logged_in)) {
		goto('/');
	}
	const user_url = `${PUBLIC_API_URL}/user`;
	const response = await fetch(user_url, { credentials: 'include' });

	if (response.status == 401 || response.status == 404) {
		logged_in.set(false);
		goto('/');
	}

	const user = (await response.json()) as unknown as User;

	return { user: user };
};

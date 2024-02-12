import { PUBLIC_API_URL } from '$env/static/public';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const user_url = `${PUBLIC_API_URL}/user`;
	const response = await fetch(user_url, { credentials: 'include' });

	const user = (await response.json()) as User;
	return { user };
};

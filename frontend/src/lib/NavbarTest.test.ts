/**
 * @jest-environment jsdom
 */

import { render } from '@testing-library/svelte';
import Navbar from './Navbar.svelte';

const user: User = {
	email: 'ntnureflection@ntnu.no',
	enrollments: [{ user_email: 'ntnureflection@ntnu.no', course_id: 'TDT4100', role: 'lecturer' }],
	reflections: []
};

test('should render overview button', () => {
	const results = render(Navbar, { props: { user } });
	expect(() => results.getByLabelText('Overview')).not.toThrow();
});

test('should render logout button', () => {
	const results = render(Navbar, { props: { user } });
	expect(() => results.getByLabelText('Log out')).not.toThrow();
});

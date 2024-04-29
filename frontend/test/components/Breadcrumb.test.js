/* eslint-disable no-undef */
import { render, screen } from '@testing-library/svelte';
import Breadcrumb from '../../src/lib/components/Breadcrumb.svelte';

describe('BreadcrumbComponent', () => {
	test('renders the home breadcrumb and additional breadcrumb items', () => {
		const breadcrumbItems = [
			{ href: '/course-1', label: 'Course 1' },
			{ href: '/course-2', label: 'Course 2' }
		];

		render(Breadcrumb, { breadcrumbItems });

		//Check for  home-breadcrumb
		expect(screen.getByText('Courses')).toBeInTheDocument();

		//Check for additional-breadcrumbs
		expect(screen.getByText('Course 1')).toBeInTheDocument();
		expect(screen.getByText('Course 2')).toBeInTheDocument();

		//Check for correct href attributes
		expect(screen.getByText('Course 1').closest('a')).toHaveAttribute('href', '/course-1');
		expect(screen.getByText('Course 2').closest('a')).toHaveAttribute('href', '/course-2');
	});
});

/* eslint-disable no-undef */
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import CourseCards from '../../src/lib/components/CourseCards.svelte';
import { goto } from '$app/navigation';

describe('CourseCards component', () => {
	//Confirms that several course cards are rendered correctly
	it('renders course cards correctly', async () => {
		const { getByText } = render(CourseCards, {
			props: {
				courses: [
					{ course_id: '1', course_semester: 'fall2021', name: 'Course 1', missingUnits: [''] },
					{ course_id: '2', course_semester: 'spring2022', name: 'Course 2', missingUnits: [''] }
				],
				role: 'Student'
			}
		});

		await waitFor(() => {
			expect(getByText('Fall 2021')).toBeInTheDocument();
			expect(getByText('Spring 2022')).toBeInTheDocument();
		});
	});

	//Confirms that the role badge is set and rendered correctly
	it('renders role badge correctly', async () => {
		const { getByText } = render(CourseCards, {
			props: {
				courses: [
					{ course_id: '1', course_semester: 'fall2021', name: 'Course 1', missingUnits: [''] }
				],
				role: 'Lecturer'
			}
		});
		await waitFor(() => expect(getByText('Lecturer')).toBeInTheDocument());
	});

	//Confirms that the course cards are clickable and navigate to the course view
	it('navigates to course view on card click', async () => {
		const { getByText } = render(CourseCards, {
			props: {
				courses: [
					{ course_id: '1', course_semester: 'fall2021', name: 'Course 1', missingUnits: [''] }
				],
				role: 'Student'
			}
		});

		const card = await waitFor(() => getByText('Fall 2021'));
		await fireEvent.click(card);
		expect(goto).toHaveBeenCalledWith('/courseview/fall2021/1');
	});
});

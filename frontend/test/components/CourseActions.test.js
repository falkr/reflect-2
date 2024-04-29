/* eslint-disable no-undef */
import CourseActions from '../../src/lib/components/CourseActions.svelte';
import { render, fireEvent } from '@testing-library/svelte';
import { mockData } from '../../__mocks__/Data';

describe('CourseActions component', () => {
	const courseData = mockData[0].course;

	//Start tests with role as student
	let data = {
		course: {
			courseData
		},
		role: 'student'
	};

	//Correctly render unroll course button only for students
	it('renders correct button text based on role', () => {
		const { getByText } = render(CourseActions, { data });
		expect(getByText('Unenroll from course')).toBeInTheDocument();
	});

	//Correctly render invite users button only for lecturers
	it('renders Invite users button for lecturer role', () => {
		//Set role to lecturer
		data.role = 'lecturer';
		const { getByText } = render(CourseActions, { data });
		expect(getByText('Invite users')).toBeInTheDocument();
	});

	//Correctly render delete course button only for lecturers, and displays correct confirmation modal
	it('renders correct delete button and modal for lecturer role', async () => {
		//Set role to lecturer
		data.role = 'lecturer';
		const { getAllByText } = render(CourseActions, { data });
		await fireEvent.click(getAllByText('Delete course')[0]);
		expect(getAllByText('Are you sure you want to delete this course?')[0]).toBeInTheDocument();
	});
});

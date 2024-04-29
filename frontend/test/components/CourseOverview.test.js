/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import CourseOverview from '../../src/lib/components/CourseOverview.svelte';
import { mockData } from '../../__mocks__/Data';

describe('CourseOverview component', () => {
	//Correct rendering of CourseOverview as a student
	it('renders CourseOverviewStudent when role is student', () => {
		const { getByText } = render(CourseOverview, {
			props: {
				data: mockData[0],
				role: 'student',
				units: []
			}
		});

		//Unroll is only rendered for students
		expect(getByText('Unenroll from course')).to.exist;
	});

	//Correct rendering of CourseOverview as a lecturer
	it('renders CourseOverviewLecturer when role is lecturer', () => {
		const { getByText } = render(CourseOverview, {
			props: {
				data: mockData[1],
				role: 'lecturer',
				units: []
			}
		});

		//Create new unit is only rendered for lecturers
		expect(getByText('Create new unit')).to.exist;
	});
});

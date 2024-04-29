/* eslint-disable no-undef */
import CourseOverviewLecturer from '../../src/lib/components/CourseOverviewLecturer.svelte';
import { render, fireEvent } from '@testing-library/svelte';
import { mockData } from '../../__mocks__/Data';
import { goto } from '$app/navigation';

describe('CourseOverviewLecturer component', () => {
	//Correct rendering of create new unit button with correct onClick event
	it('renders "Create new unit" button and fires click event', async () => {
		const { getByText } = render(CourseOverviewLecturer, {
			props: {
				data: mockData[0],
				units: []
			}
		});

		const button = getByText('Create new unit');
		expect(button).to.exist;

		await fireEvent.click(button);

		//Correct routing to create unit page
		expect(goto).toHaveBeenCalledWith(
			`/courseview/${mockData[0].course.semester}/${mockData[0].course.id}/create`,
			{
				replaceState: false
			}
		);
	});

	//Correct rendering of page when no units exists yet
	it('renders "No units exists for this course yet" when no units exist for the course', () => {
		const { getByText } = render(CourseOverviewLecturer, {
			props: {
				data: mockData[0],
				units: []
			}
		});

		//Text rendered when no units exist for the course
		expect(getByText('No units exists for this course yet')).to.exist;
	});

	//Correct rendering of several units on page
	it('renders UnitCardLecturer for each unit and fires click events', async () => {
		const { getByText } = render(CourseOverviewLecturer, {
			props: {
				data: mockData[0],
				units: mockData[0].units
			}
		});

		//Checks that all units are rendered
		await Promise.all(
			mockData[0].units.map(async (unit) => {
				const unitCard = getByText(unit.title);
				expect(unitCard).to.exist;
			})
		);
	});
});

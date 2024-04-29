/* eslint-disable no-undef */
import CourseOverviewStudent from '../../src/lib/components/CourseOverviewStudent.svelte';
import { render, fireEvent } from '@testing-library/svelte';
import { mockData } from '../../__mocks__/Data';

describe('CourseOverviewStudent component', () => {
	//Correctly renders helper text
	it('renders "No units available yet for this course" when no units exist', () => {
		const { getByText } = render(CourseOverviewStudent, {
			props: {
				data: mockData[0],
				units: []
			}
		});

		expect(getByText('No units available yet for this course')).to.exist;
	});

	//Correctly renders UnitCardStudent for each available unit, only initially showing available units
	it('renders UnitCardStudent for each available unit', () => {
		const { getByText } = render(CourseOverviewStudent, {
			props: {
				data: mockData[0],
				units: mockData[0].units
			}
		});

		//Filters out units that are unavailable or have already been reflected on, and checks rendering
		mockData[0].units.forEach((unit) => {
			if (
				unit.date_available.toString() < new Date().toISOString().split('T')[0] &&
				!mockData[0].user.reflections.some((reflection) => reflection.unit_id === unit.id)
			) {
				expect(getByText(unit.title)).to.exist;
			}
		});
	});

	//Correctly renders show/hide button, and updates accordingly based on click event
	it('renders "Hide finished and unavailable units" button and fires click event', async () => {
		const { getByText } = render(CourseOverviewStudent, {
			props: {
				data: mockData[0],
				units: mockData[0].units
			}
		});

		const button = getByText('Show finished and unavailable units');
		expect(button).to.exist;

		await fireEvent.click(button);
		//Button text changes after click, tested by checking for the new text
		expect(getByText('Hide finished and unavailable units')).to.exist;
		//Button text changes back after another click event
		await fireEvent.click(button);
		expect(getByText('Show finished and unavailable units')).to.exist;
	});
});

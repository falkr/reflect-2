/* eslint-disable no-undef */
import { render, screen } from '@testing-library/svelte';
import UnitOverview from '../../src/lib/components/UnitOverview.svelte';
import { mockData, mockLecturerUser } from '../../__mocks__/Data';

describe('UnitOverview', () => {
	test('A student user renders the student view', () => {
		render(UnitOverview, { data: mockData[0], unitName: 'test', unit_number: 1 });
	});

	test('A lecturer user renders the lecturer view', () => {
		const lecturerData = {
			user: mockLecturerUser,
			course: mockData[1].course,
			unit: {
				unit: mockData[1]
			},
			role: 'lecturer'
		};

		render(UnitOverview, { data: lecturerData, unitName: 'test', unit_number: 1 });

		// Text which only shows up for the lecturer
		expect(screen.queryAllByText(/The name of the unit, visible to the students./i)).not.toBeNull();
	});

	test('A future unit cannot be reflected on', () => {
		const alteredData = mockData[0];
		alteredData.unit.unit.date_available = '3000-04-12';
		render(UnitOverview, { data: alteredData, unitName: 'test', unit_number: 1 });
		// Text which only shows up when a unit is in the future
		expect(screen.queryByText(/This unit is not ready for reflection./i)).not.toBeNull();
	});
});

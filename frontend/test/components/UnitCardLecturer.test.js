/* eslint-disable no-undef */
import { render, screen } from '@testing-library/svelte';
import UnitCardLecturer from '../../src/lib/components/UnitCardLecturer.svelte';
import { mockUnits } from '../../__mocks__/Data';

describe('UnitCardLecturer', () => {
	test('Test the "ready"-state of the card', () => {
		render(UnitCardLecturer, { unitData: mockUnits[0], unitTag: 'ready' });

		expect(screen.queryByText('Open unit')).not.toBeNull();
		expect(screen.queryByText('Unit 1 - 23.08.2022')).not.toBeNull();
		// expect(screen.queryByText('View report (0 reflections)')).not.toBeNull();
	});

	test('Test the "notAvailable"-state of the card', () => {
		render(UnitCardLecturer, { unitData: mockUnits[0], unitTag: 'notAvailable' });

		expect(screen.queryByText('Edit unit')).not.toBeNull();
		expect(screen.queryByText('Unit 1 - 23.08.2022')).not.toBeNull();
		expect(screen.queryByText('View report (0 reflections)')).not.toBeNull();
	});
});

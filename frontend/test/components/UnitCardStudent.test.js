/* eslint-disable no-undef */
import { render, screen } from '@testing-library/svelte';
import UnitCardStudent from '../../src/lib/components/UnitCardStudent.svelte';
import { mockData, mockUnits } from '../../__mocks__/Data';

describe('UnitCardStudent', () => {
	test('Test the "available"-state of the card', () => {
		render(UnitCardStudent, { data: mockData[0], unitData: mockUnits[0], status: 'available' });

		expect(screen.queryByText('State Machines')).not.toBeNull();
		expect(screen.queryByText('Unit 1 - 23.08.2022')).not.toBeNull();
		expect(screen.queryByText('Start reflection')).not.toBeNull();
		expect(screen.queryByText('Decline unit')).not.toBeNull();
	});

	test('Test the "submitted"-state of the card', () => {
		render(UnitCardStudent, { data: mockData[0], unitData: mockUnits[0], status: 'submitted' });

		expect(screen.queryByText('State Machines')).not.toBeNull();
		expect(screen.queryByText('Unit 1 - 23.08.2022')).not.toBeNull();
		expect(screen.queryByText('Reflection submitted')).not.toBeNull();
	});

	test('Test the "declined"-state of the card', () => {
		render(UnitCardStudent, { data: mockData[0], unitData: mockUnits[0], status: 'declined' });

		expect(screen.queryByText('State Machines')).not.toBeNull();
		expect(screen.queryByText('Unit 1 - 23.08.2022')).not.toBeNull();
		expect(screen.queryByText('Declined')).not.toBeNull();
	});
});

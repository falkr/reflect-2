/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import UnitOverview from '../../src/lib/components/UnitOverview.svelte';
import { mockData } from '../../__mocks__/Data';

test('renders UnitOverview component', () => {
	render(UnitOverview, { data: mockData[0] });
});

/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import Page from '../../src/routes/+error.svelte';
import { mockData } from '../../__mocks__/Data.js';

describe('Error', () => {
	test('Test the "ready"-state of the card', () => {
		render(Page, { data: mockData[0] });
	});
});

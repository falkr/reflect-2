/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import Page from '../../src/routes/courseview/[semester]/+page.svelte';
import { mockData } from '../../__mocks__/Data.js';

describe('Courseview semester', () => {
	test('Test the "ready"-state of the card', () => {
		render(Page, { data: mockData[0] });
	});
});

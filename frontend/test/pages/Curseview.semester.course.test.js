/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import Page from '../../src/routes/courseview/[semester]/[course]/+page.svelte';
import { load } from '../../src/routes/courseview/[semester]/[course]/+layout.ts';
import { mockData } from '../../__mocks__/Data.js';

describe('Courseview semester course', () => {
	test('Test the "ready"-state of the card', () => {
		render(Page, { data: mockData[0] });
	});
});

describe('load function for courseview', () => {
	test('throws error if parent gives indexOf error', async () => {
		global.fetch = vi.fn(() => Promise.resolve({ status: 404 }));
		global.parent = vi.fn(() => {
			return { user: mockData[0].user };
		});
		const params = { course: 'CS999', semester: 'Fall2023' };
		await expect(load({ parent: global.parent, params, fetch: global.fetch })).rejects.toThrow();
	});
});

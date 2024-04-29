/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import Page from '../../src/routes/login/+page.svelte';
import { mockData } from '../../__mocks__/Data';
import { load } from '../../src/routes/login/+page.ts';
import { vi } from 'vitest';

describe('Login', () => {
	test('Test the "ready"-state of the card', () => {
		render(Page, { data: mockData[0] });
	});
});

describe('load function in +page.ts', () => {
	test('should load user data correctly', async () => {
		global.fetch = vi.fn(() =>
			Promise.resolve({
				json: () => Promise.resolve({ id: '123', name: 'Test User' })
			})
		);
		const PUBLIC_API_URL = 'https://example.com/api';
		const result = await load({
			fetch: global.fetch,
			params: {},
			url: new URL(PUBLIC_API_URL)
		});

		expect(result).toEqual({ user: { id: '123', name: 'Test User' } });
		global.fetch.mockRestore();
	});
});

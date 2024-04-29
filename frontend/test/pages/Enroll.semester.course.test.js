/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import Page from '../../src/routes/enroll/[semester]/[course]/+page.svelte';
import { load } from '../../src/routes/enroll/[semester]/[course]/+layout.ts';
import { mockData } from '../../__mocks__/Data.js';
import { PUBLIC_API_URL } from '$env/static/public';
import * as navigation from '$app/navigation';

describe('Enroll', () => {
	test('Test the "ready"-state of the card', () => {
		render(Page, { data: mockData[0] });
	});

	describe('Layout load function', () => {
		beforeEach(() => {
			global.fetch = vi.fn(() =>
				Promise.resolve({
					ok: true,
					status: 200,
					json: () => Promise.resolve({})
				})
			);
		});

		afterEach(() => {
			vi.clearAllMocks();
		});

		test('should navigate to courseview on successful enrollment', async () => {
			const params = { course: 'testCourse', semester: '2023' };
			await load({ params, fetch: global.fetch });

			expect(global.fetch).toHaveBeenCalledWith(`${PUBLIC_API_URL}/enroll`, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					course_id: params.course,
					course_semester: params.semester,
					role: 'student'
				})
			});

			expect(navigation.goto).toHaveBeenCalledWith(`/courseview/${params.course}`);
		});
	});
});

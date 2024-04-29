/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import Page from '../../src/routes/courseview/[semester]/[course]/[unit]/+page.svelte';
import { load } from '../../src/routes/courseview/[semester]/[course]/[unit]/+page.ts';
import { mockData } from '../../__mocks__/Data.js';

describe('Courseview semester course unit', () => {
	test('Test the "ready"-state of the card', () => {
		render(Page, { data: mockData[0] });
	});
});

describe('load function tests', () => {
	test('should check if user has reflected on the unit', async () => {
		const mockParent = vi.fn().mockResolvedValue({
			course: { id: 1, semester: 'Fall' },
			user: { reflections: [{ unit_id: 2 }] }, // User has reflected on unit 2
			units: [{ id: 2, date_available: '2023-01-01' }]
		});
		const params = { course: 'Math', unit: '2' };
		const result = await load({ params, parent: mockParent });
		expect(result.reflected).toBeTruthy();
	});

	test('should check if the unit is available based on date', async () => {
		const futureDate = new Date();
		futureDate.setDate(futureDate.getDate() + 1); // Date in the future
		const mockParent = vi.fn().mockResolvedValue({
			course: { id: 1, semester: 'Fall' },
			user: { reflections: [] },
			units: [{ id: 2, date_available: futureDate.toISOString() }]
		});
		const params = { course: 'Math', unit: '2' };
		const result = await load({ params, parent: mockParent });
		expect(result.available).toBeFalsy();
	});

	test('should fetch unit data successfully', async () => {
		global.fetch = vi.fn(() =>
			Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ content: 'Unit content' })
			})
		);
		const mockParent = vi.fn().mockResolvedValue({
			course: { id: 1, semester: 'Fall' },
			user: { reflections: [] },
			units: [{ id: 2, date_available: '2023-01-01' }]
		});
		const params = { course: 'Math', unit: '2' };
		const result = await load({ params, parent: mockParent });
		expect(result.unit).toEqual({ content: 'Unit content' });
	});

	test('should handle fetch unit data failure', async () => {
		console.error = vi.fn(); // Mock console.error to avoid actual console error logs
		global.fetch = vi.fn(() => Promise.reject(new Error('Failed to fetch')));
		const mockParent = vi.fn().mockResolvedValue({
			course: { id: 1, semester: 'Fall' },
			user: { reflections: [] },
			units: [{ id: 2, date_available: '2023-01-01' }]
		});
		const params = { course: 'Math', unit: '2' };
		await expect(load({ params, parent: mockParent })).resolves.toHaveProperty('unit', undefined);
		expect(console.error).toHaveBeenCalledWith(
			'Error fetching unit data:',
			new Error('Failed to fetch')
		);
	});
});

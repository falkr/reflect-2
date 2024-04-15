import { render } from '@testing-library/svelte';
import { default as Page } from './+page.svelte';

describe('Overview page', () => {
	it('renders without errors', () => {
		const { container } = render(Page);
		expect(container.firstChild).not.toBeNull();
	});
});

test('Should render Create course button', () => {
	const results = render(Page);
	expect(() => results.getByLabelText('Create course')).not.toThrow();
});

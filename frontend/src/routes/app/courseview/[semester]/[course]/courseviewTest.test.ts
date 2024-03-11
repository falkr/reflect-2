import { render } from '@testing-library/svelte';
import { default as courseViewPage } from '../[course]/+page.svelte';

describe('Courseview page', () => {
	it('renders without errors', () => {
		const { container } = render(courseViewPage);
		expect(container.firstChild).not.toBeNull();
	});
});

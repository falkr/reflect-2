/* eslint-disable no-undef */
import { render } from '@testing-library/svelte';
import ReflectionsBadge from '../../src/lib/components/ReflectionsBadge.svelte';

describe('ReflectionsBadge component', () => {
	//Basic rendering with first time generating available
	it('renders "Ready for report generation" when totalReflections equals reflectionsSinceLastReport and totalReflections is greater than 0', () => {
		const { getByText } = render(ReflectionsBadge, {
			props: {
				reflectionsSinceLastReport: 5,
				totalReflections: 5,
				unitTag: 'available'
			}
		});

		expect(getByText('Ready for report generation')).toBeInTheDocument();
	});

	//Correctly renders the number of reflections since last report
	it('renders "X reflections since last report" when reflectionsSinceLastReport is greater than 0', () => {
		const { getByText } = render(ReflectionsBadge, {
			props: {
				reflectionsSinceLastReport: 3,
				totalReflections: 5,
				unitTag: 'available'
			}
		});

		expect(getByText('+3 reflections since last report')).toBeInTheDocument();
	});

	//Correctly renders that the report is not available, based on lack of reclections
	it('renders "Not available yet" when unitTag is "notAvailable"', () => {
		const { getByText } = render(ReflectionsBadge, {
			props: {
				reflectionsSinceLastReport: 0,
				totalReflections: 0,
				unitTag: 'notAvailable'
			}
		});

		expect(getByText('Not available yet')).toBeInTheDocument();
	});
});

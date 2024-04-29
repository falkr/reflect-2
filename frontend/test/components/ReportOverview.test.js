/* eslint-disable no-undef */
import { render, fireEvent } from '@testing-library/svelte';
import ReportOverview from '../../src/lib/components/ReportOverview.svelte';
import { mockData } from '../../__mocks__/Data';

describe('ReportOverview component', () => {
	const mockUnit = mockData[0].unit;
	const mockCourse = mockData[0].course;
	let data = {
		mockUnit,
		mockCourse
	};

	//Correct rendering of generate report button
	it('renders "Generate new report" button', () => {
		const { getByText } = render(ReportOverview, { props: { data, numberOfReflectionsInUnit: 5 } });
		expect(getByText('Generate new report')).toBeInTheDocument();
	});

	//Correct rendering of download report button
	it('renders "Download report" button', () => {
		const { getByText } = render(ReportOverview, { props: { data, numberOfReflectionsInUnit: 5 } });
		expect(getByText('Download report')).toBeInTheDocument();
	});

	//Correct rendering of helper text when there are reflections for the unit
	it('renders "You have no reflections for this unit." when numberOfReflectionsInUnit is 0', () => {
		const { getByText } = render(ReportOverview, { props: { data, numberOfReflectionsInUnit: 0 } });
		expect(getByText('You have no reflections for this unit.')).toBeInTheDocument();
	});

	//Correct rendering of generation helper/loading text
	it('renders "Generating report..." after clicking generate report button', async () => {
		const { getByText } = render(ReportOverview, { props: { data, numberOfReflectionsInUnit: 5 } });
		const generateButton = getByText('Generate new report');
		await fireEvent.click(generateButton);
		expect(getByText('Generating...')).toBeInTheDocument();
	});
});

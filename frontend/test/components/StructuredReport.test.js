/* eslint-disable no-undef */
import { render, screen, cleanup } from '@testing-library/svelte';
import StructuredReport from '../../src/lib/components/StructuredReport.svelte';
import { mockCourse } from '../../__mocks__/Data';

describe('StructuredReport component', () => {
	test('structuredReport is rendered', () => {
		const reportData = mockCourse.reports[0];
		render(StructuredReport, { reportData: reportData, unitName: 'testunit' });

		expect(
			screen.getByText(
				/Please note, this report was generated using AI and may contain errors or inaccuracies./i
			)
		).toBeInTheDocument();
	});
	test('The report data is displayed', () => {
		const reportData = mockCourse.reports[0];
		reportData.report_content = [
			{
				question_id: 1,
				question: 'Teaching',
				answer: 'This is a test answer'
			},
			{
				question_id: 2,
				question: 'Difficult',
				answer: 'another answer'
			},
			{
				question_id: 1,
				question: 'Teaching',
				answer: 'This is another test answer'
			},
			{
				question_id: 2,
				question: 'Difficult',
				answer: 'another test answer'
			}
		];

		reportData.number_of_answers = 2;

		render(StructuredReport, { reportData: reportData, unitName: 'testunit' });
		expect(screen.getByText(/testunit/i)).toBeInTheDocument();
	});
	test('The report data is displayed', async () => {
		const reportData = mockCourse.reports[0];
		reportData.report_content = [
			{
				question_id: 1,
				question: 'Teaching',
				answer: 'This is a test answer'
			},
			{
				question_id: 2,
				question: 'Difficult',
				answer: 'another answer'
			},
			{
				question_id: 1,
				question: 'Teaching',
				answer: 'This is another test answer'
			},
			{
				question_id: 2,
				question: 'Difficult',
				answer: 'another test answer'
			}
		];

		reportData.number_of_answers = 2;

		render(StructuredReport, { reportData: reportData, unitName: 'testunit' });
		expect(screen.getByText(/testunit/i)).toBeInTheDocument();

		let testIfQuestionIsDisplayed = screen.queryByText(/2/i);
		expect(testIfQuestionIsDisplayed).not.toBeNull();

		reportData.report_content = [
			{
				question_id: 1,
				question: 'Teaching',
				answer: 'This is a test answer'
			},
			{
				question_id: 2,
				question: 'Difficult',
				answer: 'another answer'
			}
		];
		reportData.number_of_answers = 1;
		cleanup();

		render(StructuredReport, { reportData: reportData, unitName: 'testunit' });

		reportData.report_content = [
			{
				question_id: 1,
				question: 'Teaching',
				answer: 'This is a test answer'
			},
			{
				question_id: 2,
				question: 'Difficult',
				answer: 'another answer'
			}
		];
		reportData.number_of_answers = 1;
		render(StructuredReport, { reportData: reportData, unitName: 'testunit' });

		let testIfQuestionIsNotDisplayed = screen.queryByText(/2/i);
		expect(testIfQuestionIsNotDisplayed).toBeNull();
	});
});

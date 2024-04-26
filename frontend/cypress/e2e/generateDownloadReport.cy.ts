const reflections = [
	{
		userId: 'user1',
		unitId: 4,
		answers: [
			'I really grasped the concepts of recursion, because the examples were very clear.',
			'I struggled with understanding memoization, as it was not covered in depth.'
		]
	},
	{
		userId: 'user2',
		unitId: 4,
		answers: [
			'Graph algorithms were my best learning success because I enjoyed visualizing the problems.',
			'I found dynamic programming to be complex due to its optimal substructure.'
		]
	},
	{
		userId: 'user3',
		unitId: 4,
		answers: [
			'Successfully implemented merge sort, which was very satisfying.',
			'Struggled with tree rotations, as the diagrams were confusing.'
		]
	},
	{
		userId: 'user4',
		unitId: 4,
		answers: [
			'Mastering SQL joins was a breakthrough because of the practical exercises.',
			'The concept of database normalization is still unclear to me, need more examples.'
		]
	},
	{
		userId: 'user5',
		unitId: 4,
		answers: [
			'Understanding REST APIs was rewarding as I could see immediate results in my projects.',
			'Asynchronous programming remains a challenge; callback functions are hard to manage.'
		]
	}
];

const questionIds = [1, 2];

describe('Check functionality for generating report and then downlaod it', () => {
	beforeEach(() => {
		// Clear all cookies initially to ensure a clean state
		const sessionCookie = Cypress.env('SESSION_COOKIE');
		cy.clearCookies();

		// Set the 'session' cookie
		cy.setCookie('session', sessionCookie).then(() => {
			cy.getCookie('session').should('have.property', 'value', sessionCookie);
		});

		cy.visit('http://127.0.0.1:5173/overview');
		cy.wait(500);
		cy.reload();
	});

	it('Create course, then create and edit unit, submit reflections and then generate report', () => {
		// Create new course
		cy.get('#createCourseButton').click();
		cy.get('#courseNameInput').type('Test Course');
		cy.get('#courseIdInput').type('TDT1234');
		cy.get('#selectSemester').select('Spring 2025');
		cy.get('#createCourseSubmit').click();

		// Create new unit
		cy.get('#TDT1234').click();
		cy.get('#createUnitButton').click();
		cy.get('#unitNameCreate').type('Test Unit');
		cy.get('#unitDateCreate').type('2023-12-12');
		cy.get('#createUnitSubmitButton').click();

		// Check that report is not generated
		cy.get('#viewReportButton').click();
		cy.get('#generateReportButton').should('be.disabled');
		cy.contains('You have no reflections for this unit.').should('be.visible');

		// Send 5 reflections for the unit
		reflections.forEach((reflection) => {
			reflection.answers.forEach((answer, index) => {
				cy.request({
					method: 'POST',
					url: 'http://127.0.0.1:8000/reflection', // Ensure HTTP protocol is specified
					body: {
						body: answer,
						user_id: reflection.userId,
						unit_id: reflection.unitId,
						question_id: questionIds[index]
					},
					headers: {
						'Content-Type': 'application/json'
					}
				}).then((response) => {
					expect(response.status).to.eq(200); // or other appropriate success status
					cy.log('Reflection submitted successfully:', response.body);
				});
			});
		});

		// Check that the reflections are submitted and generate report
		cy.reload();
		cy.contains('No report is generated for this unit yet.').should('be.visible');
		cy.contains('+5 reflections since last report').should('be.visible');
		cy.get('#generateReportButton').should('be.enabled');
		cy.get('#downloadReportButton').should('be.disabled');
		cy.get('#generateReportButton').click();
		cy.contains('Generating report...').should('be.visible');

		// Check that the report is generated
		cy.wait(10000);
		cy.contains('Report for unit 4 - Test Unit').should('be.visible');
		cy.contains('Summary').should('be.visible');
		cy.contains(
			'Please note, this report was generated using AI and may contain errors or inaccuracies.'
		).should('be.visible');
		cy.contains('What was your least understood concept in this unit? Why?').should('be.visible');
		cy.contains('What was your best learning success in this unit? Why?').should('be.visible');
		cy.get('#categoryAccordion').should('be.visible');
		cy.get('#downloadReportButton').should('be.enabled');

		// Download the report
		cy.get('#downloadReportButton').click();
		cy.contains('Downloading report...').should('be.visible');

		// Delete course after test to clean up
		cy.get('#TDT1234-breadcrumb').click();
		cy.get('#deleteCourseButton').click();
		cy.get('#deleteCourseModalButton').click();
		cy.contains('Course successfully deleted!').should('be.visible');
	});
});

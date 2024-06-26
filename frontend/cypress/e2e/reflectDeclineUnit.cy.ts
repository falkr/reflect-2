import loginUser from './loginUser';

describe('Check overview student page and reflect/decline on unit', () => {
	beforeEach(() => {
		loginUser();
	});

	it('Submit and decline reflection, and check that they are not available anymore', () => {
		// Check if the navbar breadcrumb and course is visible
		cy.get('#navbar').should('be.visible');
		cy.contains('Courses').should('be.visible');
		cy.get('#TDT4100').should('be.visible');
		cy.get('#studentBadge').should('be.visible');

		// Refelct on unit
		cy.get('#TDT4100').click();
		cy.get('#reflectUnit1Button').click();
		cy.get('#question1').type(
			'I really liked the part about scrum, which I understood better after the lecture'
		);
		cy.get('#question2').type(
			'I would like more in depth theory about the different agile methods such as kanban and waterfall'
		);
		cy.get('#submitReflectionButton').click();
		cy.contains('Reflection submitted').should('be.visible');

		// Decline unit
		cy.get('#declineUnit2Button').click();

		// Clean up - delete reflection
		const userName = Cypress.env('FEIDE_USERNAME');
		cy.request({
			method: 'DELETE',
			url: `127.0.0.1:8000/delete_reflection`,
			body: {
				user_id: userName,
				unit_id: 1
			}
		}).then((response) => {
			expect(response.status).to.eq(200);
		});

		cy.request({
			method: 'DELETE',
			url: `127.0.0.1:8000/delete_reflection`,
			body: {
				user_id: userName,
				unit_id: 2
			}
		}).then((response) => {
			expect(response.status).to.eq(200);
		});
	});
});

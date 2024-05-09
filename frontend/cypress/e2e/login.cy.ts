import loginUser from './loginUser';

describe('login with feide check', () => {
	it('logs in with credentials from cypress.json.env', () => {
		loginUser();

		// Check that user is succcessfully logged in
		cy.get('#navbar').should('be.visible');
		cy.contains('Courses').should('be.visible');
		cy.get('#TDT4100').should('be.visible');
		cy.get('#studentBadge').should('be.visible');
	});
});

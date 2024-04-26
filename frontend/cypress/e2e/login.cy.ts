describe('login with feide check', () => {
	it('logs in with credentials from cypress.json.env', () => {
		cy.visit('http://127.0.0.1:5173/');
		cy.get('#loginFeideButton').click();

		Cypress.on('uncaught:exception', () => {
			return false;
		});

		// Interactions on auth.dataporten.no
		cy.origin('https://auth.dataporten.no', () => {
			cy.get('#org_selector_filter').type('NTNU{enter}{enter}');
			cy.get('#selectorg_button').click();
		});

		// Interactions on idp.feide.no
		cy.origin('https://idp.feide.no', () => {
			// Continue the authentication process
			cy.get('#username').type(Cypress.env('FEIDE_USERNAME'));
			cy.get('#password').type(Cypress.env('FEIDE_PASSWORD'), { log: false });
			cy.get('body').then((body) => {
				if (body.find('button:contains("Logg inn")').length > 0) {
					cy.get('button').contains('Logg inn').click();
				} else {
					cy.get('button').contains('Log in').click();
				}
			});
		});

		// Check that user is succcessfully logged in
		cy.get('#navbar').should('be.visible');
		cy.contains('Courses').should('be.visible');
		cy.get('#TDT4100').should('be.visible');
		cy.get('#studentBadge').should('be.visible');
	});
});

export default function loginUser() {
	// Check if the session cookie is present
	cy.getCookies().then((cookies) => {
		const sessionCookie = cookies.find((cookie) => cookie.name === 'session');

		if (sessionCookie && sessionCookie.value) {
			// If session cookie is present, use it to set the cookie and visit the main page
			cy.setCookie('session', sessionCookie.value);
			cy.visit('http://127.0.0.1:5173/overview');
		} else {
			// If no session cookie, perform the login process
			cy.wait(2000);
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

			// After login, save the session cookie
			cy.getCookie('yourSessionCookieName').then((cookie) => {
				if (cookie && cookie.value) {
					cy.setCookie('yourSessionCookieName', cookie.value);
				}
			});
		}
	});
}

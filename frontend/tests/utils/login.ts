import type { Page } from '@playwright/test';

// This function is made to navigate through the Feide login before all tests
// Not currently in use

async function login(page: Page, username: string, password: string): Promise<void> {
	await page.goto('http://localhost:5173/');
	await page.getByRole('button', { name: 'Login via Feide' }).click();
	await page.getByPlaceholder('Søk eller velg fra listen').click();
	await page.getByPlaceholder('Søk eller velg fra listen').fill('NTNU');
	await page.locator('div').filter({ hasText: 'NTNU' }).click();
	await page.getByRole('button', { name: 'Continue' }).click();
	await page.getByLabel('Brukernavn').fill('jorjo');
	await page.getByLabel('Passord', { exact: true }).click();
	await page.getByLabel('Passord', { exact: true }).fill('r4Uyp6nu%%');
	await page.getByRole('button', { name: 'Logg inn', exact: true }).click();
	// Fill in username and password
	await page.locator('id=username').fill(username);
	await page.locator('id=password').fill(password);
	await page.locator('id=feide:login').click();
}

export default login;

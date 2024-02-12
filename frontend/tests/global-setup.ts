import { chromium } from '@playwright/test';
import * as dotenv from 'dotenv';
dotenv.config();

const username = process.env.FEIDE_USERNAME ?? '';
const password = process.env.FEIDE_PASSWORD ?? '';

async function globalSetup(): Promise<void> {
	// TODO: Remove headless after this has been tested
	const browser = await chromium.launch();
	const page = await browser.newPage();

	await page.goto('http://localhost:5173/');
	await page.getByRole('button', { name: 'Login via Feide' }).click();
	// Fill in organization
	await page.locator('id=org_selector_filter').fill('NTNU');
	await page.keyboard.press('Enter');
	await page.keyboard.press('Enter');
	await page.locator('id=selectorg_button').click();

	await page.getByLabel('Brukernavn').fill(username);
	await page.locator('id=password').fill(password);
	await page.getByRole('button', { name: 'Logg inn', exact: true }).click();

	await page.waitForURL('https://ref2.iik.ntnu.no/**');
	await browser.close();
}

export default globalSetup;

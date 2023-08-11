import { chromium, expect, test } from '@playwright/test';

test('Navigate to course overview', async ({ page }) => {
	await page.goto('/overview');
	const locator1 = await page.locator('text=Course overview');
	await expect(locator1).toBeVisible();
});

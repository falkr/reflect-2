import { defineConfig } from 'cypress';

export default defineConfig({
	e2e: {
		setupNodeEvents(on, config) {
			// eslint-disable-next-line @typescript-eslint/no-unused-vars
			on;
			// eslint-disable-next-line @typescript-eslint/no-unused-vars
			config;
		}
	}
});

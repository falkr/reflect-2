import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['static/**/*.{test,spec}.{js,ts}']
	},
	build: {
		outDir: 'dist' // Specify the output directory
	}
});

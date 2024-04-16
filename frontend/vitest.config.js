import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
	plugins: [svelte()],
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./test/setupTests.js'],
		transformMode: {
			web: [/.[tj]sx?$/, /.svelte$/]
		}
	}
});

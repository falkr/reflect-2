import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

export default defineConfig({
	plugins: [svelte()],
	resolve: {
		alias: {
			$lib: resolve(__dirname, './src/lib'),
			$app: resolve(__dirname, './__mocks__/app'),
			$env: resolve(__dirname, './__mocks__/env')
		}
	},
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./test/setupTests.js'],
		transformMode: {
			web: [/.[tj]sx?$/, /.svelte$/]
		}
	}
});

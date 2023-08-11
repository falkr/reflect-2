module.exports = {
	transform: {
		'^.+\\.svelte$': ['svelte-jester', { preprocess: './svelte.config.test.cjs' }],
		'^.+\\.ts$': 'ts-jest',
		'^.+\\.js$': 'ts-jest'
	},
	moduleFileExtensions: ['js', 'ts', 'svelte'],
	moduleNameMapper: {
		'/^\\$app(.*)$/': ['<rootDir>/.svelte-kit/build/runtime/$1']
	},
	resolver: undefined,
	setupFilesAfterEnv: ['<rootDir>/jest-setup.ts'],
	collectCoverageFrom: ['src/**/*.{ts,tsx,svelte,js,jsx}']
};

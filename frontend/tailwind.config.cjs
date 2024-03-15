/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		'./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'
	],
	theme: {
		colors: {
			teal: {
				1: '#fafefd',
				2: '#f1fcfa',
				3: '#e7f9f5',
				4: '#d9f3ee',
				5: '#c7ebe5',
				6: '#afdfd7',
				7: '#8dcec3',
				8: '#53b9ab',
				9: '#12a594',
				10: '#0e9888',
				11: '#067a6f',
				12: '#046d62',
			}
		},
		fontFamily: {
			mono: ['SFMono-Regular']
		},
		fontSize: {
			sm: '0.8rem',
			xl: '1.5rem',
			base: '1.0rem'
		},
		extend: {
			button: {
				backgroundColor: '#3e5e7a', // another color
				borderColor: '#3e5e7a'
			}
		}
	},
	plugins: [require('flowbite/plugin')]
};

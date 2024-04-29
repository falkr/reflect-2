/* eslint-disable no-undef */
import postcssConfig from '../../postcss.config.cjs';

describe('PostCSS Configuration', () => {
	it('object empty', () => {
		expect(postcssConfig.plugins.tailwindcss).toBeDefined();
		expect(postcssConfig.plugins.autoprefixer).toBeDefined();
	});
});

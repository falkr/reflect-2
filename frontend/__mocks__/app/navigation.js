import { vi } from 'vitest';

const goto = vi.fn();
const invalidate = vi.fn();
const invalidateAll = vi.fn();

module.exports = {
	goto,
	invalidate,
	invalidateAll
};

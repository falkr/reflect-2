import { writable } from 'svelte/store';

let page = writable({ params: { unit: 'Unit 1' } });

module.exports = {
	page
};

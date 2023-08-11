import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export const logged_in = writable<string|boolean>(browser && (localStorage.getItem('logged_in') || false));
logged_in.subscribe((val) => browser && (localStorage.logged_in = val));

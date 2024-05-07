<script>
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import { logged_in } from '$lib/stores';
	import { Button, DarkMode } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

	/**
	 * Redirects the user to the login page.
	 */
	export function handleLogin() {
		location.href = `${PUBLIC_API_URL}/login`;
	}

	onMount(() => {
		if (get(logged_in)) {
			goto('/overview');
		}
	});
</script>

<main
	class="dark:bg-gray-900 flex flex-col items-center gap-16 sm:gap-20 justify-center min-h-screen"
>
	<div class="fixed right-4 top-4"><DarkMode class="text-blue-700 dark:text-yellow-200" /></div>
	<img
		src="/logo-horizontal-light.svg"
		alt="Reflection Tool Logo"
		class="block dark:hidden h-8 sm:h-12"
	/>
	<img
		src="/papers-illustration-light.svg"
		alt="Reflection Illustration"
		class="block dark:hidden h-20 sm:h-36"
	/>
	<img
		src="/logo-horizontal-dark.svg"
		alt="Reflection Tool Logo"
		class="hidden dark:block h-8 sm:h-12"
	/>
	<img
		src="/papers-illustration-dark.svg"
		alt="Reflection Illustration"
		class="hidden dark:block h-20 sm:h-36"
	/>
	<Button
		class="bg-teal-11 hover:bg-teal-9 dark:bg-blue-700 dark:hover:bg-blue-600"
		size="lg"
		id="loginFeideButton"
		on:click={handleLogin}
	>
		<img src="/feide-white.svg" class="w-5 h-5 me-2" alt="Reflection Icon Logo" />
		Continue with Feide
	</Button>
</main>

<script>
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import { logged_in } from '$lib/stores';
	import { Button } from 'flowbite-svelte';

	export function handleLogin() {
		location.href = `${PUBLIC_API_URL}/login`;
	}

	if (logged_in) {
		goto('/app/overview');
	} else {
		goto('/');
	}
</script>

<main class="flex flex-col items-center gap-20 justify-center min-h-screen">
    <img src="/logo-horizontal.svg" alt="Reflection Tool Logo" class="h-14" />
    <img src="/papers-illustration.svg" alt="Reflection Illustration" class="h-40" />
    <Button class="bg-teal-11 hover:bg-teal-12" size="lg" on:click={handleLogin}>
        Log in with Feide
    </Button>
</main>
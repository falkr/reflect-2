<script lang="ts">
	import './app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	import { Toaster } from 'svelte-french-toast';
	export let data: Data;
</script>

<Navbar user={data.user} />
<Toaster />

<slot />

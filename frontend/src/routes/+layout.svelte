<script lang="ts">
	import './app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	export let data: Data;
</script>

<Navbar user={data.user} />

<slot />

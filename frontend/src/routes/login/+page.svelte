<script>
	import { goto } from '$app/navigation';
	import { logged_in } from '$lib/stores';
	export let data;
	if (data.user) {
		goto('/app/overview');
		logged_in.set(true);
	} else {
		logged_in.set(false);
		goto('/');
	}
</script>

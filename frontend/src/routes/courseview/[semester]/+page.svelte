<script>
	import { goto } from '$app/navigation';
	export let data;

	//If user is logged in , go back to overview
	if (data.user) {
		goto('/overview');

		//else go to landing page
	} else {
		goto('/');
	}
</script>

<script lang="ts">
	import { page } from '$app/stores';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
</script>

<Breadcrumb
	breadcrumbItems={[
		{
			label: 'Unknown page'
		}
	]}
/>

<div class="flex items-center justify-center">
	<div class="justify-cente flex h-[300px] flex-col text-center">
		<p class="text-xl text-red-400">{$page.status}</p>
		<p class="text-xl text-red-400">{$page.error?.message}</p>
	</div>
</div>

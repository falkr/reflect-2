<script lang="ts">
	import { page } from '$app/stores';
</script>

<!-- Used for displaying errors. -->
<div class="flex items-center justify-center">
	<div class="justify-cente flex h-[300px] flex-col text-center">
		<p class="text-xl text-red-600">{$page.status}</p>
		<p class="text-xl text-red-600">{$page.error?.message}</p>
	</div>
</div>

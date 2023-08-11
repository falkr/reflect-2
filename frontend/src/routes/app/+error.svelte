<script lang="ts">
	import { page } from '$app/stores';
</script>

<!-- Used for displaying errors. -->
<div class="flex items-center justify-center">
	<div class="text-center h-[300px] flex flex-col justify-cente">
		<p class="text-red-600 text-xl">{$page.status}</p>
		<p class="text-red-600 text-xl">{$page.error?.message}</p>
	</div>
</div>

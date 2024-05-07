<script>
	import { Breadcrumb, BreadcrumbItem } from 'flowbite-svelte';
	export let breadcrumbItems = [];
</script>

<!-- Breadcrumb component with a list of breadcrumb items.-->
<div class="mx-5 md:mx-auto md:w-4/5">
	<Breadcrumb class="my-5 sm:my-8 w-max h-10" aria-label="Reflection tool breadcrumb" solid>
		<BreadcrumbItem href="/overview" home
			><span class="hidden sm:block">Courses</span></BreadcrumbItem
		>
		{#each breadcrumbItems as { href, label }}
			<BreadcrumbItem id={`${label}-breadcrumb`} {href}>{label}</BreadcrumbItem>
		{/each}
	</Breadcrumb>
</div>

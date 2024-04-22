<script lang="ts">
	import { page } from '$app/stores';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import ReportOverview from '$lib/components/ReportOverview.svelte';
	import { goto } from '$app/navigation';
	export let data: Data;

	const unitId = $page.params.unit as string;
	const matchingUnit = data.units.find((unit) => unit.id === parseInt(unitId.slice(4)));

	// Reactively check the user's role
	$: if (data && data.role !== 'lecturer') {
		goto('/'); // Navigate to a safe default route or the homepage
	}
</script>

<Breadcrumb
	breadcrumbItems={[
		{
			href: '/courseview/' + data.course.semester + '/' + data.course.id,
			label: data.course_name
		},
		{
			label: `Unit ${unitId.slice(4)} - Report`
		}
	]}
/>

{#if data}
	{#if data.role === 'lecturer'}
		<ReportOverview {data} numberOfReflectionsInUnit={matchingUnit?.total_reflections ?? 0} />
	{/if}
{:else}
	<h1 class="text-gray-500 dark:text-white mt-2">No report is generated for this unit yet.</h1>
{/if}

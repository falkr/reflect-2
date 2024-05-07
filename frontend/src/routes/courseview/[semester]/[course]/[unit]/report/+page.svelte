<script lang="ts">
	import { page } from '$app/stores';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import ReportOverview from '$lib/components/ReportOverview.svelte';
	import { goto } from '$app/navigation';
	export let data: Data;

	const semester = $page.params.semester as string;
	const courseId = $page.params.course as string;
	const matchingUnits = data.units.filter(
		(unit) => unit.course_id === courseId && unit.course_semester === semester
	);

	/**
	 * Sort the units by date available in ascending order.
	 * @return {number} - The comparison result.
	 */
	matchingUnits.sort((a, b) => {
		if (a.date_available < b.date_available) {
			return -1;
		}
		if (a.date_available > b.date_available) {
			return 1;
		}
		return 0;
	});

	const unitId = $page.params.unit as string;
	const matchingUnitIndex =
		matchingUnits.findIndex((unit) => unit.id === parseInt(unitId.slice(4))) + 1;
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
			label: `Unit ${matchingUnitIndex} - Report`
		}
	]}
/>

<!-- If the data is available, display the report overview -->
{#if data}
	{#if data.role === 'lecturer'}
		<ReportOverview
			{data}
			unit_number={matchingUnitIndex}
			numberOfReflectionsInUnit={matchingUnit?.total_reflections ?? 0}
		/>
	{/if}
{:else}
	<h1 class="text-gray-500 dark:text-white mt-2">No report is generated for this unit yet.</h1>
{/if}

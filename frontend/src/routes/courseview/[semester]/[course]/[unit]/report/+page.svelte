<script lang="ts">
	import { page } from '$app/stores';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import ReportOverview from '$lib/components/ReportOverview.svelte';
	export let data: Data;

	const unitId = $page.params.unit as string;

	let uniqueUserIds = new Set();

	if (data && data.units) {
		const matchingUnit = data.units.find((unit) => unit.id === parseInt(unitId.slice(4)));
		if (matchingUnit && matchingUnit.reflections) {
			matchingUnit.reflections.forEach((reflection) => {
				uniqueUserIds.add(reflection.user_id);
			});
		}
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
	<ReportOverview {data} numberOfReflectionsInUnit={uniqueUserIds.size} />
{:else}
	<p>Loading...</p>
{/if}

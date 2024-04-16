<script lang="ts">
	import type { PageData } from './$types';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import UnitOverview from '$lib/components/UnitOverview.svelte';

	export let data: PageData;

	let unitName = data.units.find((unit) => unit.id == data.unit_id)?.title;
	let unit_number: number = data.units.findIndex((unit) => unit.id === data.unit_id) + 1;
</script>

<Breadcrumb
	breadcrumbItems={[
		{
			href: '/courseview/' + data.course.semester + '/' + data.course.id,
			label: data.course.id
		},
		{
			label: 'Unit ' + unit_number + ' - ' + unitName
		}
	]}
/>

<UnitOverview {data} {unitName} {unit_number} />

<script lang="ts">

	import UnitOverview from '$lib/components/UnitOverview.svelte';
	export let data;
	export let units: Unit[];
	$: units = data.units;

	console.log(units);

</script>

<UnitOverview data={data} units={units} role={"student"} />
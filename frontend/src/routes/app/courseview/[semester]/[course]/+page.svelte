<script lang="ts">
	import UnitOverview from '$lib/components/UnitOverview.svelte';
	export let data: Data;
	export let units: Unit[];
	$: units = data.units;
</script>

<UnitOverview {data} {units} role={data.role} />

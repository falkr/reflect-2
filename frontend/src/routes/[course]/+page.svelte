<script lang="ts">
	import UnitOverview from '$lib/components/CourseOverview.svelte';
	export let data: Data;
	export let units: Unit[];
	$: units = data.units;
</script>

<UnitOverview {data} {units} role={'student'} />

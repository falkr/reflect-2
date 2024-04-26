<script lang="ts">
	import CourseOverviewStudent from './CourseOverviewStudent.svelte';
	import CourseOverviewLecturer from './CourseOverviewLecturer.svelte';

	export let data: Data;
	export let role: string;
	export let units: Unit[];
	$: units = data.units;

	let unitCounter = 1;

	units.sort((a, b) => {
		if (a.date_available < b.date_available) {
			return -1;
		}
		if (a.date_available > b.date_available) {
			return 1;
		}
		return 0;
	});

	units.forEach((unit) => {
		unit.unit_number = unitCounter;
		unitCounter++;
	});
</script>

<main class="flex-shrink-0">
	{#if data.role === 'lecturer'}
		<CourseOverviewLecturer {data} {units} />
	{:else}
		<CourseOverviewStudent {data} {units} />
	{/if}
</main>

<!-- on:click={() => goto(`${data.course_name}/`)} -->
<style>
	:root {
		--date-picker-background: #f6f7f8;
		--date-picker-foreground: #10302b;
	}
</style>

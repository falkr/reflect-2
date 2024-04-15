<script lang="ts">
	import CourseOverviewStudent from './CourseOverviewStudent.svelte';
	import CourseOverviewLecturer from './CourseOverviewLecturer.svelte';

	export let data: Data;
	export let role: string;
	export let units: Unit[];
	$: units = data.units;

	let showError = false;

	let showSuccess = false;

	let counter = 6;
	let toastBody = '';

	function triggerToast(body: string, type: string) {
		if (type == 'success') {
			showSuccess = true;
		} else {
			showError = true;
		}
		counter = 6;
		toastBody = body;
		timeout();
	}

	function timeout(): number {
		if (--counter > 0) return window.setTimeout(timeout, 1000);
		showError = false;
		showSuccess = false;
		return counter;
	}
</script>

<main class="flex-shrink-0">
	{#if data.role === 'lecturer'}
		<CourseOverviewLecturer {data} {units} />
	{:else}
		<CourseOverviewStudent {data} {units} />
	{/if} -
</main>

<!-- on:click={() => goto(`${data.course_name}/`)} -->
<style>
	:root {
		--date-picker-background: #f6f7f8;
		--date-picker-foreground: #10302b;
	}
</style>

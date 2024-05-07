<script lang="ts">
	import UnitCardLecturer from './UnitCardLecturer.svelte';
	import { Button } from 'flowbite-svelte';
	import { goto } from '$app/navigation';
	import CourseActions from './CourseActions.svelte';

	export let units: Unit[];
	export let data: Data;

	let date = new Date();
	let stringDate = date.toISOString().split('T')[0];
</script>

<!-- The CourseOverviewLecturer component displays the units cards of a course for a lecturer. -->
<div class="mt-16 w-full flex flex-col items-center mb-16">
	<div class="flex sm:flex-row flex-col justify-between w-11/12 sm:w-4/5">
		<div class="flex gap-4">
			<CourseActions {data} />
		</div>
		<Button
			on:click={() =>
				goto(`/courseview/${data.course.semester}/${data.course.id}/create`, {
					replaceState: false
				})}
			id="createUnitButton"
			class="text-white w-1/2 mt-4 sm:mt-0 sm:w-44 bg-teal-13 hover:bg-teal-10 focus:ring-4 focus:outline-none focus:ring-teal-300 font-medium rounded-lg text-sm py-2.5 text-center inline-flex items-center dark:bg-blue-700 dark:hover:bg-blue-600 dark:focus:ring-blue-800"
		>
			Create new unit
			<svg
				class="ml-2 w-5 h-5 text-white dark:text-white"
				aria-hidden="true"
				xmlns="http://www.w3.org/2000/svg"
				width="20"
				height="20"
				fill="none"
				viewBox="0 0 24 24"
			>
				<path
					stroke="currentColor"
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M5 12h14m-7 7V5"
				/>
			</svg>
		</Button>
	</div>
	<div class="w-11/12 sm:w-4/5 pt-2">
		{#if units.length === 0}
			<h1 class="text-gray-500 dark:text-white mt-10">No units exists for this course yet</h1>
		{:else}
			{#each [...units].reverse() as unit}
				{#if unit.date_available.toString() <= stringDate}
					<UnitCardLecturer unitData={unit} unitTag="ready" />
				{/if}
			{/each}

			{#if units.some((unit) => new Date(unit.date_available) > new Date(stringDate))}
				<h1 class="mt-16 text-xl font-semibold dark:text-white">Upcoming units</h1>
				{#each units as unit}
					{#if unit.date_available.toString() > stringDate}
						<UnitCardLecturer unitData={unit} unitTag="notAvailable" />
					{/if}
				{/each}
			{/if}
		{/if}
	</div>
</div>

<script lang="ts">
	import CourseActions from './CourseActions.svelte';
	import UnitCardStudent from './UnitCardStudent.svelte';
	import { Button } from 'flowbite-svelte';
	export let units: Unit[];
	export let data: Data;

	let date = new Date();
	let stringDate = date.toISOString().split('T')[0];

	let unitsIsHidden = true;
	let unitsButtonText = 'Show finished and unavailable units';

	/**
	 * Hides the finished and unavailable units when the button is clicked.
	 */
	function hideUnits() {
		if (unitsIsHidden) {
			unitsButtonText = 'Hide finished and unavailable units';
		} else {
			unitsButtonText = 'Show finished and unavailable units';
		}
		unitsIsHidden = !unitsIsHidden;
	}

	/**
	 * Checks if the reflection for a unit has been submitted.
	 * @param unit_id - The unit id to check for.
	 * @returns True if the reflection has been submitted, false otherwise.
	 */
	function checkReflectionSubmitted(unit_id: number) {
		return data.user.reflections.some((reflection) => reflection.unit_id === unit_id);
	}
</script>

<!-- The CourseOverviewStudent component displays the units cards of a course for a student. -->
<div class="relative flex-col md:mx-24 mx-10">
	<div class="flex justify-end mb-2">
		<CourseActions {data} />
	</div>
	{#if units.length === 0}
		<h1 class="text-gray-500 dark:text-white">No units available yet for this course</h1>
	{:else}
		<!-- Optional
		<h1 class="text-gray-500 dark:text-white">
			Click on an available unit to start your reflection
		</h1> -->
		<div class="w-full pt-2 flex flex-wrap justify-start gap-6">
			{#each [...units].reverse() as unit}
				{#if unit.date_available.toString() <= stringDate && !checkReflectionSubmitted(unit.id)}
					<UnitCardStudent unitData={unit} status="available" {data} />
				{/if}
			{/each}
		</div>
		<div class="w-full flex justify-center pt-8">
			<Button on:click={hideUnits} color="alternative">
				{unitsButtonText}
			</Button>
		</div>
		{#if !unitsIsHidden}
			<div class="w-full pt-12 flex flex-wrap justify-start gap-6">
				{#each units as unit}
					{#if data.user.reflections.some((reflection) => reflection.unit_id === unit.id && reflection.body.trim() === '')}
						<UnitCardStudent unitData={unit} {data} status="declined" />
					{:else if data.user.reflections.map((reflection) => reflection.unit_id).includes(unit.id)}
						<UnitCardStudent unitData={unit} {data} status="submitted" />
					{:else if unit.date_available.toString() > stringDate}
						<UnitCardStudent unitData={unit} {data} status="unavailable" />
					{/if}
				{/each}
			</div>
		{/if}
	{/if}
</div>

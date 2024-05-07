<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Card, ButtonGroup } from 'flowbite-svelte';
	import { FileLinesSolid } from 'flowbite-svelte-icons';
	import ReflectionsBadge from './ReflectionsBadge.svelte';

	export let unitData: Unit;
	export let unitTag: string;

	let totalReflections = unitData.total_reflections;
	let reflectionsSinceLastReport = unitData.reflections_since_last_report;

	/**
	 * Reformat the date from ISO format to a human-readable format.
	 * @param isoDateString - The date in ISO format.
	 * @returns The date in the format 'dd.mm.yyyy'.
	 */
	function reformatDate(isoDateString: Date): string {
		const [year, month, day] = isoDateString.toString().split('-');
		return `${day}.${month}.${year}`;
	}

	/**
	 * Redirects the user to the unit page.
	 */
	function redirectToUnit() {
		goto(`${window.location.pathname}/${unitData.id}`, { replaceState: false });
	}

	/**
	 * Redirects the user to the report page.
	 */
	function redirectToReport() {
		goto(`${window.location.pathname}/unit${unitData.id}/report`, { replaceState: false });
	}
</script>

<!-- The UnitCardLecturer component displays a card with information about a unit for a lecturer. -->
<Card class="max-w-full mt-6 dark:bg-gray-800 sm:p-4 sm:pl-5">
	<div class="flex justify-between">
		<div class="flex flex-col md:flex-row md:items-center">
			<h2 class="text-xl text-gray-900 dark:text-white font-semibold mr-4">{unitData.title}</h2>
			<ReflectionsBadge {reflectionsSinceLastReport} {totalReflections} {unitTag} />
		</div>
		<ButtonGroup>
			{#if unitTag === 'ready'}
				<Button id="openUnitButton" class="w-22 h-10" on:click={redirectToUnit}>Open unit</Button>
			{:else}
				<Button id="editUnitButton" class="w-22 h-10" on:click={redirectToUnit}>Edit unit</Button>
			{/if}
		</ButtonGroup>
	</div>
	<p class="text-black dark:text-gray-300">
		Unit {unitData.unit_number} - {reformatDate(unitData.date_available)}
	</p>
	<div>
		<ButtonGroup class="mt-3">
			{#if unitTag === 'ready'}
				<Button
					id="viewReportButton"
					class="focus:dark:outline-none dark:outline-none dark:bg-gray-800 dark:text-white"
					on:click={redirectToReport}
				>
					<FileLinesSolid class="w-4 h-4 mr-2" />
					View report ({totalReflections}
					{totalReflections === 1 ? 'reflection' : 'reflections'})
				</Button>
			{:else}
				<Button
					class="focus:dark:outline-none dark:outline-none dark:bg-gray-800 dark:text-white"
					disabled
				>
					<FileLinesSolid class="w-4 h-4 mr-2" />
					View report (0 reflections)
				</Button>
			{/if}
		</ButtonGroup>
	</div>
</Card>

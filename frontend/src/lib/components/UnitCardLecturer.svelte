<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Card, ButtonGroup, Badge } from 'flowbite-svelte';
	import { FileLinesSolid } from 'flowbite-svelte-icons';

	export let unitData: Unit;
	export let unitTag: string;

	let tagString: string;
	let tagColor:
		| 'none'
		| 'red'
		| 'yellow'
		| 'green'
		| 'indigo'
		| 'purple'
		| 'pink'
		| 'blue'
		| 'dark'
		| 'primary';

	let uniqueUserIds = new Set();
	unitData.reflections.forEach((reflection) => {
		uniqueUserIds.add(reflection.user_id);
	});

	let totalReflections = uniqueUserIds.size;
	let reportIsGenerated = true; // TODO
	let reflectionsSinceGeneratedReport = 10; // TODO

	if (unitTag === 'ready' && reportIsGenerated && reflectionsSinceGeneratedReport > 0) {
		tagString = `+${reflectionsSinceGeneratedReport} reflections since last report`;
		tagColor = 'yellow';
	} else if (unitTag === 'ready') {
		tagString = 'Ready for report generating';
		tagColor = 'green';
	} else {
		tagString = 'Not available yet';
		tagColor = 'red';
	}

	function reformatDate(isoDateString: Date): string {
		const [year, month, day] = isoDateString.toString().split('-');
		return `${day}.${month}.${year}`;
	}

	function redirectToUnit() {
		goto(`${window.location.pathname}/${unitData.id}`, { replaceState: false });
	}

	function redirectToReport() {
		goto(`${window.location.pathname}/unit${unitData.id}/report`, { replaceState: false });
	}
</script>

<Card class="max-w-full mt-6 dark:bg-gray-800 sm:p-4 sm:pl-5">
	<div class="flex justify-between">
		<div class="flex flex-col md:flex-row md:items-center">
			<h2 class="text-xl text-gray-900 dark:text-white font-semibold mr-4">{unitData.title}</h2>
			<!-- <Badge large color={tagColor} class="rounded-lg h-6 my-1 md:m-0">{tagString}</Badge> -->
		</div>
		<ButtonGroup>
			{#if unitTag === 'ready'}
				<Button class="w-22 h-10" on:click={redirectToUnit}>Open unit</Button>
			{:else}
				<Button class="w-22 h-10" on:click={redirectToUnit}>Edit unit</Button>
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

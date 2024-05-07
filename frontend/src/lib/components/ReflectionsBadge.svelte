<script lang="ts">
	import { Badge } from 'flowbite-svelte';

	export let reflectionsSinceLastReport: number;
	export let totalReflections: number;
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

	if (totalReflections === reflectionsSinceLastReport && totalReflections > 0) {
		tagString = 'Ready for report generating';
		tagColor = 'green';
	} else if (reflectionsSinceLastReport > 0) {
		tagString = `+${reflectionsSinceLastReport} reflections since last report`;
		tagColor = 'yellow';
	} else if (unitTag === 'notAvailable') {
		tagString = 'Not available yet';
		tagColor = 'red';
	}
</script>

<!-- The ReflectionsBadge component displays a badge with a tag string and color based on the number of reflections since the last report. -->
{#if reflectionsSinceLastReport !== 0 || unitTag === 'notAvailable'}
	<Badge large color={tagColor} class="rounded-lg h-6 my-1 md:m-0">{tagString}</Badge>
{/if}

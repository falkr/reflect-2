<script lang="ts">
	import { goto } from '$app/navigation';
	export let courses: Enrollment[];
	export let role: string;
	import { Card, Button, Badge } from 'flowbite-svelte';

	/**
	 * Formats the semester string to a more readable format.
	 * @param semester - The semester string to format.
	 * @returns The formatted semester string.
	 */
	const formatSemester = (semester: string): string => {
		const season = semester.slice(0, -4);
		const year = semester.slice(-4);
		return `${season.charAt(0).toUpperCase() + season.slice(1)} ${year}`;
	};
</script>

<!-- Display the course cards for the user -->
{#each courses as course}
	<Card
		on:click={() => goto(`/courseview/${course.course_semester}/${course.course_id}`)}
		class="m-auto cursor-pointer hover:bg-teal-2 dark:bg-gray-800 dark:hover:bg-gray-700 relative"
		id={course.course_id}
	>
		<h5
			style="font-size: 1.25rem;"
			class="mb-1 select-none text-4xl font-bold tracking-tight text-gray-900 dark:text-white text-ellipsis overflow-hidden whitespace-nowrap"
		>
			{course.course_id} - {course.course_name}
		</h5>
		<p
			class="mb-3 select-none font-normal text-gray-700 dark:text-gray-300 leading-tight"
			id="courseSemesterText"
		>
			{formatSemester(course.course_semester)}
		</p>
		<div class="flex flex-row justify-between items-end">
			<Button class="w-fit select-none bg-teal-13 dark:bg-blue-700">Open</Button>
			{#if role == 'Lecturer'}
				<Badge large color="yellow" class="ml-2 select-none" id="lecturerBadge">Lecturer</Badge>
			{:else}
				<Badge large color="green" class="ml-2 select-none" id="studentBadge">Student</Badge>
			{/if}
		</div>
		{#if course.missingUnits.length > 0}
			<p
				class="absolute top-[-10px] right-[-5px] rounded-full w-auto min-w-6 h-6 bg-red-500 text-white text-xs font-bold text-center px-2"
			>
				{course.missingUnits.length}
			</p>
		{/if}
	</Card>
{/each}

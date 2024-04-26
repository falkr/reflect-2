<script lang="ts">
	import { goto } from '$app/navigation';
	export let courses: Enrollment[];
	export let role: string;
	import { Card, Button, Badge } from 'flowbite-svelte';
	import { PUBLIC_API_URL } from '$env/static/public';

	let coursesWithNames: (Enrollment & { name: string })[] = [];

	//Update courseWithNames when a new course is created
	$: {
		(async () => {
			coursesWithNames = await Promise.all(
				courses.map(async (course) => {
					const name = await getCourseName(course.course_id, course.course_semester);
					return { ...course, name };
				})
			);
		})();
	}

	//Fetch to get course names
	async function getCourseName(courseId: string, courseSemester: string): Promise<string> {
		const response = await fetch(
			`${PUBLIC_API_URL}/course?course_id=${courseId}&course_semester=${courseSemester}`,
			{
				method: 'GET',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				}
			}
		);
		const res = await response.json();
		return res.name;
	}

	const formatSemester = (semester: string): string => {
		const season = semester.slice(0, -4);
		const year = semester.slice(-4);
		return `${season.charAt(0).toUpperCase() + season.slice(1)} ${year}`;
	};
</script>

{#each coursesWithNames as course}
	<Card
		on:click={() => goto(`/courseview/${course.course_semester}/${course.course_id}`)}
		class="m-auto cursor-pointer hover:bg-teal-2 dark:bg-gray-800 dark:hover:bg-gray-700"
		id={course.course_id}
	>
		<h5
			style="font-size: 1.25rem;"
			class="mb-1 select-none text-4xl font-bold tracking-tight text-gray-900 dark:text-white text-ellipsis overflow-hidden whitespace-nowrap"
		>
			{course.course_id} - {course.name}
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
	</Card>
{/each}

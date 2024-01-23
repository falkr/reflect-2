<script lang="ts">
	import { goto } from '$app/navigation';
	export let courses: Enrollment[];
	export let role: string;
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';
</script>

<div class="w-1/2 overflow-x-auto shadow-md sm:rounded-lg">
	<Table>
		<TableHead>
			<TableHeadCell class="bg-teal-8 text-center text-base text-teal-2">{role}</TableHeadCell>
		</TableHead>
		<TableBody tableBodyClass="divide-y">
			{#each courses as course}
				<TableBodyRow class="border-b bg-white dark:border-gray-700 dark:bg-teal-12">
					<TableBodyCell
						class="cursor-pointer py-3 pl-4 text-center hover:bg-teal-1"
						on:click={() => goto(`/app/courseview/${course.course_semester}/${course.course_id}`)}
					>
						<p class="text-base">({course.course_semester}) {course.course_id}</p></TableBodyCell
					>
				</TableBodyRow>
			{/each}
		</TableBody>
	</Table>
</div>

{#if role == 'Lecturer'}
	<div class="w-1/2 overflow-x-auto shadow-md sm:rounded-lg">
		<Table>
			<TableHead>
				<TableHeadCell class="bg-teal-8 text-center text-base text-teal-2"
					>Student Preview (as Lecturer)</TableHeadCell
				>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each courses as course}
					<TableBodyRow class="border-b bg-white dark:border-gray-700 dark:bg-teal-12">
						<TableBodyCell
							class="cursor-pointer py-3 pl-4 text-center hover:bg-teal-1"
							on:click={() =>
								goto(`/app/coursepreview/${course.course_semester}/${course.course_id}`)}
						>
							<p class="text-base">({course.course_semester}) {course.course_id}</p></TableBodyCell
						>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
{/if}

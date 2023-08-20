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

<div class="w-1/3 overflow-x-auto shadow-md sm:rounded-lg">
	<Table>
		<TableHead>
			<TableHeadCell class="text-teal-2 bg-teal-8 text-center text-base">{role}</TableHeadCell>
		</TableHead>
		<TableBody tableBodyClass="divide-y">
			{#each courses as course}
				<TableBodyRow class="dark:bg-teal-12 border-b bg-white dark:border-gray-700">
					<TableBodyCell
						class="hover:bg-teal-1 cursor-pointer py-3 pl-4 text-center"
						on:click={() => goto(`/app/courseview/${course.course_id}`)}
					>
						<p class="text-base">{course.course_id}</p></TableBodyCell
					>
				</TableBodyRow>
			{/each}
		</TableBody>
	</Table>
</div>

{#if role == "Lecturer"}
	<div class="w-1/3 overflow-x-auto shadow-md sm:rounded-lg">
		<Table>
			<TableHead>
				<TableHeadCell class="text-teal-2 bg-teal-8 text-center text-base">Student Preview (as Lecturer)</TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each courses as course}
					<TableBodyRow class="dark:bg-teal-12 border-b bg-white dark:border-gray-700">
						<TableBodyCell
							class="hover:bg-teal-1 cursor-pointer py-3 pl-4 text-center"
							on:click={() => goto(`/app/coursepreview/${course.course_id}`)}
						>
							<p class="text-base">{course.course_id}</p></TableBodyCell
						>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
{/if}

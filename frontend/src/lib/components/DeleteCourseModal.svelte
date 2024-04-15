<script lang="ts">
	import { Button, Modal, ButtonGroup } from 'flowbite-svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import toast, { Toaster } from 'svelte-french-toast';
	export let data: Data;
	let showModal = false;

	async function actionCourse() {
		if (data.role === 'student') {
			const response = await fetch(`${PUBLIC_API_URL}/unroll_course`, {
				method: 'DELETE',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					course_id: data.course.id,
					course_semester: data.course.semester,
					role: data.role
				})
			});
			if (response.ok) {
				showModal = false;
				goto('/overview');
			} else {
				toast.error('Failed to unroll from course');
			}
		} else {
			const response = await fetch(`${PUBLIC_API_URL}/delete_course`, {
				method: 'DELETE',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					id: data.course.id,
					semester: data.course.semester
				})
			});
			if (response.ok) {
				showModal = false;
				goto('/overview');
			} else {
				toast.error('Failed to delete course');
			}
		}
	}
</script>

<div class="relative flex-col]">
	<ButtonGroup>
		<Button on:click={() => (showModal = true)}
			>{data.role === 'student' ? 'Unroll course' : 'Delete course'}</Button
		>
	</ButtonGroup>

	<Modal bind:open={showModal} size="xs" autoclose={false} class="w-full">
		<form class="flex flex-col space-y-3">
			<h3 class=" text-xl font-normal text-gray-900 dark:text-white mx-auto">
				{data.role === 'student' ? 'Unroll course' : 'Delete course'}
			</h3>
			<p class="text-sm text-gray-500 mx-auto">
				Are you sure you want to {data.role === 'student' ? 'unroll from' : 'delete'} this course?
			</p>
			<Button
				on:click={actionCourse}
				class="w-full1 bg-red-700 hover:bg-red-600 dark:bg-red-700 dark:hover:bg-red-600"
				>{data.role === 'student' ? 'Unroll course' : 'Delete course'}</Button
			>
		</form>
	</Modal>
</div>

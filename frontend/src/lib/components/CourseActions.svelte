<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import toast from 'svelte-french-toast';
	import { Button, Modal, ButtonGroup, Input, Helper } from 'flowbite-svelte';

	export let data: Data;
	const base_url = window.location.origin;
	const placeholderStr = `${base_url}/enroll/${data.course.semester}/${data.course.id}`;
	let showCreateUnitModal = false;
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
				toast.success('Unrolled from course successfully!', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
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
				toast.success('Course successfully deleted!', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			} else {
				toast.error('Failed to delete course');
			}
		}
	}

	function copyPlaceholderToClipboard() {
		const inputElement = document.getElementById('enrollLinkStudent') as HTMLInputElement;
		const placeholderValue = inputElement.placeholder;

		if (navigator.clipboard && placeholderValue) {
			navigator.clipboard
				.writeText(placeholderValue)
				.then(() => {
					toast.success('Link copied to clipboard', {
						iconTheme: {
							primary: '#36786F',
							secondary: '#FFFFFF'
						}
					});
				})
				.catch((err) => {
					toast.error('Failed to copy link to clipboard');
				});
		}
	}

	async function createUserInvitation(role: string) {
		const course_id = data.course.id;
		const uids = document.getElementById('enrollLecturer') as HTMLInputElement;
		let uid_list = uids.value.split(' ');

		for (let uid of uid_list) {
			const response = await fetch(`${PUBLIC_API_URL}/create_invitation`, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					uid: uid,
					course_id: course_id,
					course_semester: data.course.semester,
					role: role
				})
			});
			const status = response.status;

			if (status === 200) {
				toast.success('Invitation sent successfully', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			} else {
				toast.error('Failed to send invitation');
				return;
			}
		}
	}
</script>

<ButtonGroup>
	{#if data.role === 'lecturer'}
		<Button on:click={() => (showCreateUnitModal = true)} id="inviteUsersButton"
			>Invite users</Button
		>
	{/if}
	<Button on:click={() => (showModal = true)} id="deleteCourseButton"
		>{data.role === 'student' ? 'Unroll course' : 'Delete course'}</Button
	>
</ButtonGroup>

<!--Delete/Unroll course modal-->
<Modal bind:open={showModal} size="xs" autoclose={false} class="w-full" id="deleteCourseModal">
	<form class="flex flex-col space-y-3">
		<h3 class=" text-xl font-normal text-gray-900 dark:text-white mx-auto">
			{data.role === 'student' ? 'Unroll course' : 'Delete course'}
		</h3>
		<p class="text-sm text-gray-500 mx-auto">
			Are you sure you want to {data.role === 'student' ? 'unroll from' : 'delete'} this course?
		</p>
		<Button
			on:click={actionCourse}
			id="deleteCourseModalButton"
			class="w-full1 bg-red-700 hover:bg-red-600 dark:bg-red-700 dark:hover:bg-red-600"
			>{data.role === 'student' ? 'Unroll course' : 'Delete course'}</Button
		>
	</form>
</Modal>

<!--Invite users modal-->
<Modal
	bind:open={showCreateUnitModal}
	size="xs"
	autoclose={false}
	class="w-full"
	id="inviteUsersModal"
>
	<form class="flex flex-col space-y-3">
		<h3 class=" text-xl font-normal text-gray-900 dark:text-white mx-auto">Invite Students</h3>
		<Helper class="text-sm text-gray-500 mx-auto">Invite students by copying this link</Helper>
		<Input
			type="text"
			name="enrollLinkStudent"
			id="enrollLinkStudent"
			placeholder={placeholderStr}
			value={placeholderStr}
			readOnly
		/>
		<Button
			on:click={copyPlaceholderToClipboard}
			class="w-full1 bg-teal-13 hover:bg-teal-8 dark:bg-blue-700 dark:hover:bg-blue-600"
			>Copy link</Button
		>
		<h3 class="pt-4 mt-10 text-xl font-normal text-gray-900 dark:text-white mx-auto">
			Invite Lecturers (FEIDE username)
		</h3>
		<Helper class="text-sm text-gray-500 mx-auto"
			>To invite multiple lecturers, insert space-separated usernames</Helper
		>
		<Input type="text" name="enrollLecturer" id="enrollLecturer" placeholder={`Username`} />
		<Button
			on:click={() => createUserInvitation('lecturer')}
			id="enrollLecturerButton"
			class="w-full1 bg-teal-13 hover:bg-teal-8 dark:bg-blue-700 dark:hover:bg-blue-600"
			>Send Invitation</Button
		>
	</form>
</Modal>

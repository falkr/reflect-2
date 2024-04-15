<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Button, Modal, ButtonGroup, Input, Helper } from 'flowbite-svelte';
	import toast, { Toaster } from 'svelte-french-toast';
	export let data: Data;
	const base_url = window.location.origin;
	const placeholderStr = `${base_url}/enroll/${data.course.semester}/${data.course.id}`;
	let showCreateUnitModal = false;

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

<Toaster />
<ButtonGroup>
	<Button on:click={() => (showCreateUnitModal = true)}>Invite users</Button>
</ButtonGroup>
<!--Invite users modal-->
<Modal bind:open={showCreateUnitModal} size="xs" autoclose={false} class="w-full">
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
			class="w-full1 bg-teal-13 hover:bg-teal-8 dark:bg-blue-700 dark:hover:bg-blue-600"
			>Send Invitation</Button
		>
	</form>
</Modal>

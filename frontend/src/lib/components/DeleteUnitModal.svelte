<script lang="ts">
	import { Button, Modal, ButtonGroup, Heading } from 'flowbite-svelte';
	import toast from 'svelte-french-toast';
	import { TrashBinOutline } from 'flowbite-svelte-icons';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { invalidate } from '$app/navigation';

	export let data: any;
	let showDeleteUnitModal = false;

	/**
	 * Deletes the unit from the course by making an API call to the backend server.
	 * The function sends a DELETE request to the server with the unit id, course id, and course semester.
	 * Upon successful deletion, it redirects to the previous page and shows a success toast.
	 * On failure, it displays an error toast.
	 * @return {Promise<{result: any, status: number}>} - The result of the API call and the HTTP status.
	 */
	async function deleteUnit() {
		const response = await fetch(`${PUBLIC_API_URL}/delete_unit/${data.unit_id}`, {
			method: 'DELETE',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				course_id: data.course.id,
				course_semester: data.course.semester
			})
		});
		const status = response.status;
		const result = await response.json();
		if (status == 200) {
			toast.success('Unit deleted successfully', {
				iconTheme: {
					primary: '#36786F',
					secondary: '#FFFFFF'
				}
			});
			window.history.back();
		} else {
			toast.error('Failed to delete unit', {
				iconTheme: {
					primary: '#FF0000',
					secondary: '#FFFFFF'
				}
			});
		}
		showDeleteUnitModal = false;
		invalidate('app:courseOverview');
		return { result, status };
	}
</script>

<!--Delete unit button-->
<ButtonGroup>
	<Button id="deleteUnitButton" class="w-32" on:click={() => (showDeleteUnitModal = true)}>
		Delete unit
		<TrashBinOutline class="w-4 h-4 ml-2" />
	</Button>
</ButtonGroup>
<!--Delete unit modal-->
<Modal
	bind:open={showDeleteUnitModal}
	size="xs"
	autoclose={false}
	class="w-full"
	id="deleteUnitModal"
>
	<div class="p-2">
		<Heading tag="h3" class="text-xl">Delete unit</Heading>
		<p class="mt-2">
			Are you sure you want to delete this unit? All the unit data will be deleted permanently.
		</p>
		<div class="mt-6 w-full flex space-x-2 justify-center">
			<Button id="deleteUnitConfirmButton" on:click={deleteUnit} class="w-36 bg-red-500 text-white">
				Delete unit
				<TrashBinOutline class="w-4 h-4 ml-2" />
			</Button>
			<Button on:click={() => (showDeleteUnitModal = false)} class="w-32 bg-gray-200 text-gray-800">
				Cancel
			</Button>
		</div>
	</div>
</Modal>

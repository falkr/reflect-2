<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import {
		Navbar,
		NavBrand,
		Button,
		DarkMode,
		Dropdown,
		DropdownItem,
		Modal
	} from 'flowbite-svelte';
	import { ArrowRightToBracketSolid } from 'flowbite-svelte-icons';
	import { logged_in } from '../stores';
	import { MailIcon } from 'svelte-feather-icons';
	import { onMount } from 'svelte';
	import { goto, invalidate } from '$app/navigation';

	export let user: User;

	let activeInvitation: Invitation;
	let invitations: Invitation[] = [];

	let dropdownOpen = false;
	let answerInvitationModal = false;

	/**
	 * Fetches the invitations for the user from the backend server.
	 * The function sends a GET request to the server to fetch the invitations.
	 * Upon successful response, it stores the invitations in the invitations array.
	 * @returns The invitations array.
	 */
	async function getInvitations() {
		const response = await fetch(`${PUBLIC_API_URL}/get_invitations`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const js = await response.json();
		invitations = js;
		return { js };
	}

	onMount(getInvitations);

	/**
	 * Handles the click event on the invitation notification.
	 * The function sets the active invitation to the clicked invitation and opens the answer invitation modal.
	 * @param invitation - The invitation object that was clicked.
	 */
	function handleInviteClick(invitation: Invitation) {
		activeInvitation = invitation;
		answerInvitationModal = true;
	}

	/**
	 * Enrolls the user to the course from the invitation.
	 * The function sends a POST request to the server to enroll the user to the course.
	 * Upon successful enrollment, it redirects to the overview page.
	 * @returns The response from the server.
	 */
	async function enrollUser() {
		const course_id = activeInvitation.course_id;
		const course_semester = activeInvitation.course_semester;
		const uid = activeInvitation.uid;
		const role = activeInvitation.role;

		const response = await fetch(`${PUBLIC_API_URL}/enroll`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				uid: uid,
				course_id: course_id,
				course_semester: course_semester,
				role: role
			})
		});
		const js = await response.json();
		goto('/overview');
		return { js };
	}

	/**
	 * Accepts the invitation and enrolls the user to the course.
	 * The function calls the enrollUser function to enroll the user to the course and then deletes the invitation.
	 */
	function acceptInvitation() {
		enrollUser();
		deleteInvitation();
	}

	/**
	 * Deletes the invitation from the backend server.
	 * The function sends a DELETE request to the server to delete the invitation.
	 * Upon successful deletion, it invalidates the layout user store and removes the invitation from the invitations array.
	 * @returns The response from the server.
	 */
	async function deleteInvitation() {
		const invitation_id = activeInvitation.id;
		const response = await fetch(`${PUBLIC_API_URL}/delete_invitation/${invitation_id}`, {
			method: 'DELETE',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const js = await response.json();
		invalidate('app:layoutUser');
		invitations = invitations.filter((invitation) => invitation.id !== activeInvitation.id);
		return { js };
	}

	/**
	 * Logs out the user from the application.
	 * The function sets the logged_in store to false and redirects to the logout endpoint.
	 */
	async function handleLogOut() {
		try {
			logged_in.set(false);
			window.location.href = `${PUBLIC_API_URL}/logout`;
		} catch (error) {
			console.error('Logout failed:', error);
			// Handle error (show message, retry, etc.)
		}
	}
</script>

<!-- Navbar component -->
{#if user && user.detail !== 'You are not logged in'}
	<Navbar shadow class="p-6 sm:px-3 md:px-15 dark:bg-gray-800" id="navbar">
		<NavBrand href="/overview">
			<img
				src="/logo-horizontal-light.svg"
				alt="Reflection Tool Logo"
				class="me-3 hidden md:block dark:hidden"
			/>
			<img
				src="/logo-icon-light.svg"
				class="me-3 md:hidden dark:hidden"
				alt="Reflection Icon Logo"
			/>
			<img
				src="/logo-horizontal-dark.svg"
				alt="Reflection Tool Logo"
				class="me-3 hidden dark:md:block"
			/>
			<img
				src="/logo-icon-dark.svg"
				class="me-3 hidden dark:max-md:block"
				alt="Reflection Icon Logo"
			/>
		</NavBrand>
		<div class="flex items-center gap-2 sm:gap-5">
			<span class="hidden sm:inline">Logged in as {user.uid}</span>
			<DarkMode class="align-bottom text-gray-700 dark:text-yellow-200" />
			<div class="relative" id="mailIconDiv">
				{#if invitations.length > 0}
					<div
						id="invitationCountNotification"
						class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 hover:cursor-default focus:outline-none"
					>
						<span class="select-none text-[12px] font-bold text-white focus:outline-none"
							>{invitations.length}</span
						>
					</div>
				{/if}
				<MailIcon
					class="hover:cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg w-10 h-10 text-gray-700 p-2.5 focus:outline-none dark:text-white "
					on:click={() => {
						dropdownOpen = !dropdownOpen;
					}}
				/>
				<Dropdown open={dropdownOpen} class="w-max" id="invitationDropdown">
					{#if invitations.length > 0}
						{#each invitations as invitation}
							<DropdownItem
								class="hover:cursor-pointer focus:outline-none"
								on:click={() => {
									handleInviteClick(invitation);
								}}
							>
								You have been invited to course {invitation.course_id} as: {invitation.role}
							</DropdownItem>
						{/each}
					{:else}
						<DropdownItem>You have no new notifications</DropdownItem>
					{/if}
				</Dropdown>
				<Modal
					bind:open={answerInvitationModal}
					size="xs"
					autoclose={false}
					class="w-full"
					id="answerInvitationModal"
				>
					<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Course invitation</h3>
					<p>
						Are you sure you want to join the course {activeInvitation.course_id} as {activeInvitation.role}?
					</p>
					<Button
						type="submit"
						class="w-full1 bg-teal-13 hover:bg-teal-10 dark:bg-blue-700 dark:hover:bg-blue-600"
						on:click={() => {
							acceptInvitation();
							answerInvitationModal = false;
						}}>Accept</Button
					>

					<Button
						type="submit"
						id="declineInvitationButton"
						class="w-full1 bg-red-500 hover:bg-red-400 "
						on:click={() => {
							deleteInvitation();
							answerInvitationModal = false;
						}}>Decline</Button
					>
				</Modal>
			</div>
			<Button on:click={handleLogOut} color="alternative" class="ml-4">
				Log out
				<ArrowRightToBracketSolid class="w-3.5 h-3.5 ms-2" />
			</Button>
		</div>
	</Navbar>
{/if}

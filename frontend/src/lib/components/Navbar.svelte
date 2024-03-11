<script lang="ts">
	import { goto, invalidate } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Navbar, NavBrand, Dropdown, DropdownItem, Button, Modal } from 'flowbite-svelte';
	import { logged_in } from '../stores';
	import { MailIcon } from 'svelte-feather-icons';
	import { onMount } from 'svelte';
	export let user: User;
	let activeInvitation: Invitation;
	let invitations: Invitation[] = [];

	//handles the form bein submitted
	function handleLogOut() {
		logged_in.set(false);
		location.href = `${PUBLIC_API_URL}/logout`;
	}

	function handleOverview() {
		goto('/app/overview');
	}

	let dropdownOpen = false;

	let answerInvitationModal = false;

	/*function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		const formData = new FormData(e.target as HTMLFormElement);

		answerInvitationModal = false;
	}*/

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

	function handleInviteClick(invitation: Invitation) {
		activeInvitation = invitation;
		answerInvitationModal = true;
	}

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
		goto('/app/overview');
		return { js };
	}

	function acceptInvitation() {
		enrollUser();
		deleteInvitation();
	}

	// function for deleting invitation, using DELETE method
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
</script>

<Navbar
	class="bg-teal-12 text-teal-12 mx-auto flex  h-28 max-w-full items-center justify-between md:max-w-full"
>
	<div class="flex">
		<NavBrand href="/app/overview" class="flex self-center">
			<div class="ml-5 flex md:ml-10">
				<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="230 135 500 285" width="60">
					<defs />
					<g
						id="Canvas_1"
						fill="none"
						stroke="none"
						fill-opacity="1"
						stroke-opacity="1"
						stroke-dasharray="none"
					>
						<title>Canvas 1</title>
						<g id="Canvas_1_Layer_2">
							<title>Layer 2</title>
							<g id="Line_2">
								<path
									d="M 240 341 C 266.664 350.6657 293.336 370.16665 320 370 C 346.664 369.83335 373.336 340 400 340 C 426.664 340 453.336 370 480 370 C 506.664 370 533.336 340 560 340 C 586.664 340 613.336 370 640 370 C 666.664 370 693.336 349.999 720 340"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="19"
								/>
							</g>
							<g id="Line_7">
								<path
									d="M 240 381 C 266.664 390.6657 293.336 410.16665 320 410 C 346.664 409.83335 373.336 380 400 380 C 426.664 380 453.336 410 480 410 C 506.664 410 533.336 380 560 380 C 586.664 380 613.336 410 640 410 C 666.664 410 693.336 389.999 720 380"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="19"
								/>
							</g>
							<g id="Line_14">
								<line
									x1="617.5"
									y1="286.5"
									x2="688.5"
									y2="244.5"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="18"
								/>
							</g>
							<g id="Line_17">
								<line
									x1="535.5"
									y1="218.5"
									x2="560.5"
									y2="146.5"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="18"
								/>
							</g>
							<g id="Line_18">
								<line
									x1="428"
									y1="218.5"
									x2="403"
									y2="144.5"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="18"
								/>
							</g>
							<g id="Line_19">
								<line
									x1="342.5"
									y1="286.5"
									x2="276.5"
									y2="244.5"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="18"
								/>
							</g>
							<g id="Line_20">
								<path
									d="M 360 350.5 C 366.5 307.5 407 250.5 480 250 C 553 249.5 589.5 306.5 600 350.5"
									stroke="#e7f9f5"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="18"
								/>
							</g>
						</g>
					</g>
				</svg>
			</div>
			<span
				class="ml-8 hidden self-center whitespace-nowrap text-[20px] font-bold text-teal-3 dark:text-white sm:block md:text-[25px]"
			>
				NTNU_reflection
			</span>
		</NavBrand>
	</div>

	<div class="mr-5 flex items-center">
		<span class="mr-5 hidden text-[20px] italic text-teal-3 md:block">{user.uid}</span>

		<button class="mr-5 text-[16px] text-teal-3 md:text-[20px]" on:click={handleOverview}
			>Overview</button
		>

		<button
			type="submit"
			class=" mr-5 text-[16px] text-teal-3 md:text-[20px]"
			on:click={handleLogOut}>Log out</button
		>
		<div class="relative mt-0.5">
			{#if invitations.length > 0}
				<div
					class="absolute -top-1 -right-1 flex h-3 w-3 items-center justify-center rounded-full bg-red-500 hover:cursor-default focus:outline-none"
				>
					<span class="text-xs font-bold text-white focus:outline-none">{invitations.length}</span>
				</div>
			{/if}
			<MailIcon
				class="text-teal-3  hover:cursor-pointer  focus:outline-none dark:text-white"
				on:click={() => {
					dropdownOpen = !dropdownOpen;
				}}
			/>
			<Dropdown open={dropdownOpen}>
				{#if invitations.length > 0}
					{#each invitations as invitation}
						<DropdownItem
							class="hover:cursor-pointer focus:outline-none"
							on:click={() => {
								handleInviteClick(invitation);
							}}
						>
							You have been invited to course: {invitation.course_id} as: {invitation.role}
						</DropdownItem>
					{/each}
				{:else}
					<DropdownItem>You have no new notifications</DropdownItem>
				{/if}
			</Dropdown>
			<Modal bind:open={answerInvitationModal} size="xs" autoclose={false} class="w-full">
				<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Course invitation</h3>
				<p>
					Are you sure you want to join the course {activeInvitation.course_id} as {activeInvitation.role}?
				</p>
				<Button
					type="submit"
					class="w-full1 bg-teal-9 hover:bg-teal-8"
					on:click={() => {
						acceptInvitation();
						answerInvitationModal = false;
					}}>Accept</Button
				>

				<Button
					type="submit"
					class="w-full1 bg-teal-9 hover:bg-teal-8"
					on:click={() => {
						deleteInvitation();
						answerInvitationModal = false;
					}}>Decline</Button
				>
			</Modal>
		</div>
	</div>
</Navbar>

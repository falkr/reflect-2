<script lang="ts">
	import { goto, invalidate, invalidateAll } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public';
	import {
		AccordionItem,
		Accordion,
		Button,
		Label,
		Input,
		Modal,
		Select,
		Toast
	} from 'flowbite-svelte';
	import { createForm } from 'felte';
	import {
		validateEmailAddresses,
		validateInviteRole,
		// validateUnitSeqNumber,
		validateUnitTitle
	} from '$lib/validation';
	import { DateInput } from 'date-picker-svelte';
	import { AlertCircleIcon, CheckCircleIcon } from 'svelte-feather-icons';
	import { slide } from 'svelte/transition';

	export let data: Data;
	export let role: string;
	export let units: Unit[];
	$: units = data.units;

	let selectedInviteRole: string;

	let roles = [
		{ value: 'student', name: 'Student' },
		{ value: 'lecturer', name: 'Lecturer' },
		{ value: 'teaching assistant', name: 'Teaching Assistant' }
	];

	//dates for datePicker
	let date = new Date();
	let minDate = new Date();
	let maxDate = new Date(new Date().setFullYear(new Date().getFullYear() + 2));
	let stringDate = date.toISOString().split('T')[0];

	const teaching_assistants = data.course.users.filter(
		(enrollment) => enrollment.role === 'teaching assistant'
	);
	const students = data.course.users.filter((enrollment) => enrollment.role === 'student');

	let unitModal = false;
	let emailModal = false;

	let showError = false;

	let showSuccess = false;

	let counter = 6;
	let toastBody = '';

	async function _sendMail(form: FormData) {
		// post request to
		//const course_ID = data.course.id;

		let email_addresses = form.get('email');
		// To send emails, the email addresses has to include "@stud.ntnu.no" and not only "@ntnu.no"

		let email = '';
		if (email_addresses instanceof File) {
			// Handle file input
			email = email_addresses.name;
		} else if (typeof email_addresses === 'string') {
			// Handle regular string input
			email = email_addresses;
		}

		let emails_list = email.split(' ');
		let invitation_ids: number[] = [];
		let response;

		// Create row in invitation table
		for (let i = 0; i < emails_list.length; i++) {
			response = await createUserInvitation(emails_list[i], selectedInviteRole);
			if (response.status == 200) {
				invitation_ids.push(response.result.id);
			} else {
				// If one POST request fails, delete all the invitations that were created
				for (let i = 0; i < invitation_ids.length; i++) {
					deleteInvitation(invitation_ids[i]);
				}
				return response;
			}
		}
		return response;
		// Because of trouble with the server, we are not sending emails for now
		// TODO: Contact IT Drift to enable sending of emails

		// const response = await fetch(`${PUBLIC_API_URL}/invitation_email/${course_ID}`, {
		// 	method: 'POST',
		// 	credentials: 'include',
		// 	headers: {
		// 		'Content-Type': 'application/json'
		// 	},
		// 	body: JSON.stringify({
		// 		email: emails_list
		// 	})
		// });
		// const js = await response.json();
		// return { js };
	}

	async function createUserInvitation(email: string, role: string) {
		const course_id = data.course.id;

		const response = await fetch(`${PUBLIC_API_URL}/create_invitation`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				email: email,
				course_id: course_id,
				course_semester: data.course.semester,
				role: role
			})
		});
		const status = response.status;
		const result = await response.json();
		return { result, status };
	}

	//function for creating unit
	async function createUnit(form: FormData) {
		const title = form.get('title');
		// const date_available = form.get('date_available');
		// const seq_no = form.get('seq_no');

		const response = await fetch(`${PUBLIC_API_URL}/create_unit`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				title: title,
				date_available: date.toISOString().split('T')[0],
				course_id: data.course.id,
				course_semester: data.course.semester,
				hidden: false
			})
		});
		const status = response.status;
		const result = await response.json();
		invalidate('app:courseOverview');
		return { result, status };
	}

	//Form for creating unit
	const { form, errors, isSubmitting } = createForm({
		//on submit, create a course
		onSubmit: async (values, { form }) => {
			const formData = new FormData(form as HTMLFormElement);
			return createUnit(formData);
		},
		onSuccess(response) {
			const castedResponse = response as Response;
			if (castedResponse.status == 200) {
				unitModal = false;
				triggerToast('Unit successfully created!', 'success');
			}
			if (castedResponse.status == 409) {
				unitModal = true;
				triggerToast('Could not create unit', 'error');
			}
		},

		//validates the form on submitting
		validate: (values) => {
			const errors: Partial<FormValues> = {};
			if ($isSubmitting) {
				const titleErrors = validateUnitTitle(values.title);
				if (titleErrors) {
					errors.title = Array.isArray(titleErrors) ? titleErrors : [titleErrors];
				}
			}
		}
	});

	//form for inviting students
	const {
		form: inviteForm,
		errors: inviteErrors,
		isSubmitting: inviteFormIsSubmitting
	} = createForm({
		//on submit, create a course
		onSubmit: async (values, { form }) => {
			const formData = new FormData(form as HTMLFormElement);
			return _sendMail(formData);
		},
		onSuccess(response) {
			const castedResponse = response as Response;
			if (castedResponse.status == 200) {
				emailModal = false;
				triggerToast('Invitations has been sent!', 'success');
			}
			if (castedResponse.status == 409) {
				emailModal = true;
				triggerToast('Could not create invitation', 'error');
			}
		},

		//validates the form on submitting
		validate: (values) => {
			const errors: Partial<FormValues> = {};
			if ($inviteFormIsSubmitting) {
				errors.email = validateEmailAddresses(values.email);
				errors.role = validateInviteRole(values.role);
				return errors;
			}
		}
	});

	// function for deleting invitation, using DELETE method
	async function deleteInvitation(invitation_id: number) {
		const response = await fetch(`${PUBLIC_API_URL}/delete_invitation/${invitation_id}`, {
			method: 'DELETE',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		await response.json();
	}

	function getUnitName(number: number) {
		return units.find((unit) => unit.id == number)?.title;
	}

	function triggerToast(body: string, type: string) {
		if (type == 'success') {
			showSuccess = true;
		} else {
			showError = true;
		}
		counter = 6;
		toastBody = body;
		timeout();
	}

	function timeout(): number {
		if (--counter > 0) return window.setTimeout(timeout, 1000);
		showError = false;
		showSuccess = false;
		return counter;
	}

	async function update_hidden(unit_id: number, hidden: boolean) {
		const response = await fetch(`${PUBLIC_API_URL}/update_hidden_unit`, {
			method: 'PATCH',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				id: unit_id,
				hidden: hidden
			})
		});
		await response.json();
		invalidateAll();
	}
</script>

<main class="flex-shrink-0">
	<div class="relative">
		<div class="flex items-center justify-center pl-4 pr-4 pt-10">
			<div class="header mt-5 flex flex-col border-b-2 border-teal-12 pb-3">
				<h3 class="headline flex text-left text-xl font-bold text-teal-12">
					{data.course.id}
					<p class="ml-3 mr-3">-</p>
					<p class="text-xl font-medium text-teal-12" style="word-break: break-word">
						{data.course.name}
					</p>
				</h3>
			</div>
			<Button
				on:click={() => goto(`/app/overview/`)}
				class=" absolute left-0 top-0 mt-2 w-52 hover:text-teal-8"
				outline
				color="alternative"
				><svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="2"
					stroke="currentColor"
					class="h-4 w-4"
				>
					<path
						stroke-linecap="inherit"
						stroke-linejoin="inherit"
						d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3"
					/>
				</svg>
				<p class="ml-2 text-left">Back to overview</p>
			</Button>
		</div>
		<div class="flex flex-col md:gap-y-4">
			{#if role === 'lecturer'}
				<div class="buttonContainer flex justify-center pt-10">
					<Button
						on:click={() => (unitModal = true)}
						class="w-[190px] rounded-full border-teal-8 bg-teal-8 hover:border-teal-7 hover:bg-teal-7"
						size="xl"
					>
						+ Create new unit
					</Button>
					<div class="w-2" />
					<Button
						on:click={() => (emailModal = true)}
						class="w-[190px] rounded-full border-teal-8 bg-teal-8 hover:border-teal-7 hover:bg-teal-7 "
						size="xl"
					>
						+ Invite
					</Button>
				</div>
			{/if}

			<!-- <NewCourseModal {isOpen} {toggleIsOpen} /> -->
			<Modal bind:open={unitModal} size="xs" autoclose={false} class="w-full">
				<form class="flex flex-col space-y-6" use:form>
					<h3 class="p-0 text-xl font-medium text-teal-12 dark:text-white">Create unit</h3>
					<Label class="space-y-2">
						<span>Unit name</span>
						<Input type="text" name="title" placeholder="title" required />
					</Label>

					<small>
						{#if $errors.title}
							{#each $errors.title as error}
								<p class="text-red-500">{error}</p>
							{/each}
						{/if}
					</small>

					<Label class="space-y-0">
						<span>Date available from</span>
					</Label>

					<DateInput
						bind:value={date}
						max={maxDate}
						min={minDate}
						format="yyyy-MM-dd"
						closeOnSelection={true}
					/>
					<Button
						type="submit"
						data-modal-target="unitModal"
						data-modal-toggle="unitModal"
						class="w-full1 bg-teal-9 hover:bg-teal-8">Submit</Button
					>
				</form>
			</Modal>

			<Modal bind:open={emailModal} size="xs" autoclose={false} class="w-full">
				<form class="flex flex-col space-y-6" use:inviteForm>
					<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Invite Users</h3>
					<Label class="space-y-2">
						<span><b>Email</b></span>
						<p>To invite multiple users, insert space-separated email addresses</p>
						<Input type="text" name="email" placeholder="example@ntnu.no" required />
						<Input type="hidden" name="user" value={data.user.email} />
					</Label>
					<small>
						{#if $inviteErrors.email}
							{#each $inviteErrors.email as error}
								<p class="text-red-500">{error}</p>
							{/each}
						{/if}
					</small>
					<Label class="space-y-2">
						<span><b>Role</b></span>
						<Select
							class="mt-2"
							items={roles}
							required
							name="role"
							bind:value={selectedInviteRole}
						/>
					</Label>
					<small>
						{#if $inviteErrors.role}
							{#each $inviteErrors.role as error}
								<p class="text-red-500">{error}</p>
							{/each}
						{/if}
					</small>
					<Button
						type="submit"
						data-modal-target="emailModal"
						data-modal-toggle="emailModal"
						class="w-full1 bg-teal-9 hover:bg-teal-8">Submit</Button
					>
				</form>
			</Modal>

			<section class="flex items-center justify-center pt-12">
				<Accordion
					class="b-teal-12 mt-16 w-[300px] border-2 border-teal-12 bg-teal-1 md:mt-2 md:w-2/3"
					activeClass="bg-teal-1 dark:bg-fifthly text-fifthly-600 dark:text-white"
					inactiveClass="bg-white text-gray-500 dark:text-gray-400 hover:bg-fifthly-100 dark:hover:bg-fifthly-800"
				>
					{#if role === 'lecturer'}
						<AccordionItem class="border-b-2 border-teal-12">
							<span slot="header" class="text-[18px] font-semibold text-teal-12">View Reports</span>
							<p class="">
								{#each data.course.reports as report}
									<!-- svelte-ignore a11y-click-events-have-key-events -->
									<li
										class="w-50 border-stone-300 container mt-3 flex h-16 list-none justify-between rounded border-[1px] border-solid border-teal-12 bg-teal-1 p-2 hover:bg-teal-4"
										on:click={() => goto(`${data.course_name}/reports/${report.unit_id}`)}
									>
										<p class="mt-3 font-semibold text-teal-12">
											Report for unit "{getUnitName(report.unit_id)}"
										</p>
									</li>
								{/each}
							</p>
						</AccordionItem>
					{/if}
					<AccordionItem open class="border-b-2 border-teal-12">
						<span slot="header" class="text-[18px] font-semibold text-teal-12">View units</span>
						<p class="">
							{#each units as unit}
								<!-- svelte-ignore a11y-click-events-have-key-events -->
								{#if role === 'student' && !unit.hidden}
									<li
										class="w-50 border-stone-300 container mt-3 flex h-24 list-none justify-between rounded border-[1px] border-solid border-teal-12 bg-teal-1 p-2 hover:bg-teal-4"
										on:click={() => goto(`${data.course_name}/${unit.id}`)}
									>
										<p class="mt-3 font-semibold text-teal-12">{unit.title}</p>

										<div class="justify-end self-center">
											{#if data.user.reflections
												.map((reflection) => reflection.unit_id)
												.includes(unit.id)}
												<div class=" flex justify-end rounded border-teal-12">
													<span class=" font-semibold text-[#32431b]">Answered</span>
												</div>
											{:else}
												<div class=" flex justify-end rounded">
													<span class=" font-semibold text-[#902c2c]">Unanswered</span>
												</div>
											{/if}
											{#if unit.date_available.toString() > stringDate}
												<span>Availble from: {unit.date_available}</span>
											{:else}
												<span>Available</span>
											{/if}
										</div>
									</li>
								{:else if role === 'lecturer' || role === 'teaching assistant'}
									{#if !unit.hidden}
										<li
											class="w-50 border-stone-300 container mt-3 flex h-24 list-none justify-between rounded border-[1px] border-solid border-teal-12 bg-teal-1 p-2 hover:bg-teal-4"
											on:click={() => goto(`${data.course_name}/${unit.id}/reflections`)}
										>
											<p class="mt-3 font-semibold text-teal-12">{unit.title}</p>

											<div class="self-center text-right">
												{#if role === 'lecturer' || role === 'teaching assistant'}
													<div class="">Response count: {unit.reflections.length / 2}</div>
												{/if}
												{#if unit.date_available.toString() > stringDate}
													<span class="text-sm italic">Available from: {unit.date_available}</span>
												{:else}
													<span class="text-sm italic">Available</span>
												{/if}
											</div>
										</li>
										<Button
											on:click={() => update_hidden(unit.id, true)}
											class="h-[40px] w-[90px] rounded-full bg-orange-600 hover:bg-orange-700"
										>
											- Hide unit
										</Button>
									{:else}
										<li
											class="w-50 border-stone-300 container mt-3 flex h-24 list-none justify-between rounded border-[1px] border-solid border-teal-12 bg-teal-1 p-2 hover:bg-teal-4"
											on:click={() => goto(`${data.course_name}/${unit.id}/reflections`)}
										>
											<p class="mt-3 font-semibold text-teal-12">{'[HIDDEN] ' + unit.title}</p>

											<div class="self-center text-right">
												{#if role === 'lecturer' || role === 'teaching assistant'}
													<div class="">Response count: {unit.reflections.length / 2}</div>
												{/if}
												{#if unit.date_available.toString() > stringDate}
													<span class="text-sm italic">Available from: {unit.date_available}</span>
												{:else}
													<span class="text-sm italic">Available</span>
												{/if}
											</div>
										</li>
										<Button
											on:click={() => update_hidden(unit.id, false)}
											class="h-[40px] w-[90px] rounded-full bg-teal-7 hover:bg-teal-8 "
											size="sm"
										>
											+ Show unit
										</Button>
									{/if}
								{/if}
							{/each}
						</p>
					</AccordionItem>

					{#if role === 'lecturer' || role === 'teaching assistant'}
						<AccordionItem class="border-b-2 border-teal-12">
							<span slot="header" class="text-[18px] font-semibold text-teal-12"
								>Teaching assistant</span
							>
							<p class="">
								{#each teaching_assistants as ta}
									<li class="mt-3 font-bold text-teal-12">
										{ta.uid}
									</li>
								{/each}
							</p>
						</AccordionItem>
						<AccordionItem class="border-b-2 border-teal-3">
							<span slot="header" class="text-[18px] font-semibold text-teal-12">Students</span>
							<p class="mt-3 font-bold text-teal-12">
								{#each students as student}
									<li class=" list-none p-2">{student.uid}</li>
								{/each}
							</p>
						</AccordionItem>
					{/if}
				</Accordion>
			</section>
		</div>
		<div class="z-50">
			<Toast
				position="bottom-right"
				transition={slide}
				bind:open={showSuccess}
				divClass="w-full max-w-sm p-5"
			>
				<svelte:fragment slot="icon">
					<CheckCircleIcon />
				</svelte:fragment>
				<div class="text-[1.5em]">{toastBody}</div>
			</Toast>

			<Toast position="bottom-right" transition={slide} bind:open={showError}>
				<svelte:fragment slot="icon">
					<AlertCircleIcon />
				</svelte:fragment>
				<div class="text-[1.5em]">{toastBody}</div>
			</Toast>
		</div>
	</div>
</main>

<!-- on:click={() => goto(`${data.course_name}/`)} -->
<style>
	:root {
		--date-picker-background: #f6f7f8;
		--date-picker-foreground: #10302b;
	}
</style>

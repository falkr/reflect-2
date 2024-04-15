<script lang="ts">
	import type { PageData } from './$types';
	import { Input, Label, Helper, Textarea, Heading, P, Button } from 'flowbite-svelte';
	import { CloseOutline, FileCirclePlusSolid, PapperPlaneSolid } from 'flowbite-svelte-icons';
	import { validateUnitTitle } from '$lib/validation';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import { Toaster, toast } from 'svelte-french-toast';
	import { onMount } from 'svelte';
	import { goto, invalidate } from '$app/navigation';
	import { browser } from '$app/environment';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { createForm } from 'felte';
	import DeleteUnitModal from '$lib/components/DeleteUnitModal.svelte';

	export let data: PageData;

	let unitName = data.units.find((unit) => unit.id == data.unit_id)?.title;
	let availableDate = data.unit.unit.date_available;
	let unit_number: number = data.units.findIndex((unit) => unit.id === data.unit_id) + 1;
	let isUnitOngoing: boolean = false;
	let isUserLecturer: boolean = false;
	let decline: boolean = false;
	let answers: string[] = [];

	async function editUnit(form: FormData) {
		const response = await fetch(`${PUBLIC_API_URL}/update_unit/${data.unit_id}`, {
			method: 'PATCH',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				title: unitName,
				date_available: availableDate,
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

	//Form for edit unit
	const { form, errors, isSubmitting } = createForm({
		//on submit, create a course
		onSubmit: async (values, { form }) => {
			const formData = new FormData(form as HTMLFormElement);
			return editUnit(formData);
		},
		onSuccess(response) {
			const castedResponse = response as Response;
			if (castedResponse.status == 200) {
				window.history.back();
				toast.success('Unit updated successfully', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			}
			if (castedResponse.status == 409) {
				toast.error('An error occurred while updating the unit');
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

	onMount(() => {
		const availableDate = new Date(data.unit.unit.date_available);
		const today = new Date();
		isUnitOngoing = availableDate <= today;
		isUserLecturer = data.role === 'lecturer'; //Sets the value to true if the user is a lecturer
		decline = false;
	});

	//Return the reflection by question
	function getReflectionByQuestion() {
		let answerString = answers.shift();
		if (answerString == undefined) {
			return '';
		}
		return answerString;
	}

	function handleDecline() {
		decline = true;
	}

	//Submit or decline based on button pressed
	function handleSubmit(e: SubmitEvent) {
		const formData = new FormData(e.target as HTMLFormElement);
		if (decline === false) {
			createReflection(formData);
		} else {
			declineReflection(formData);
		}
	}

	//Submitting a reflection
	async function createReflection(form: FormData) {
		let questions = form.getAll('question_id');
		let answers = form.getAll('answer');

		//Parse question_id to numbers
		let questions_num = questions.map(function (item) {
			return parseInt(item.toString());
		});

		let promises = [];

		for (let index = 0; index < questions.length; index++) {
			//Sends #question_id reflections to backend
			promises.push(
				fetch(`${PUBLIC_API_URL}/reflection`, {
					method: 'POST',
					credentials: 'include',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						body: answers[index],
						user_id: data.user.uid,
						unit_id: data.unit_id,
						question_id: questions_num[index]
					})
				})
			);
		}

		Promise.all(promises)
			.then(() => {
				if (browser) {
					invalidate('app:layoutUser').then(() => {
						goto(`/courseview/${data.course.semester}/${data.course.id}`);
					});
				}
			})
			.then(() => {
				toast.success('Reflection submitted', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			});
	}

	//Declining a reflection
	async function declineReflection(form: FormData) {
		let questions = form.getAll('question_id');

		//Parse question_id to numbers
		let questions_num = questions.map(function (item) {
			return parseInt(item.toString());
		});

		let promises = [];

		for (let index = 0; index < questions.length; index++) {
			//Sends #question_id reflections to backend
			promises.push(
				fetch(`${PUBLIC_API_URL}/reflection`, {
					method: 'POST',
					credentials: 'include',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						body: '',
						user_id: data.user.uid,
						unit_id: data.unit_id,
						question_id: questions_num[index]
					})
				})
			);
		}

		Promise.all(promises)
			.then(() => {
				if (browser) {
					invalidate('app:layoutUser').then(() => {
						goto(`/courseview/${data.course.semester}/${data.course.id}`);
					});
				}
			})
			.then(() => {
				toast.success('Unit declined', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			});
	}
</script>

<Breadcrumb
	breadcrumbItems={[
		{
			href: '/courseview/' + data.course.semester + '/' + data.course.id,
			label: data.course.id
		},
		{
			label: 'Unit ' + unit_number + ' - ' + unitName
		}
	]}
/>

<div class="mx-5 md:w-4/5 md:mx-auto mb-12 text-gray-900 dark:text-white flex">
	<Heading tag="h1" class="mt-2 text-xl"
		>{'Unit ' + unit_number + ' - ' + data.units.find((unit) => unit.id == data.unit_id)?.title}
	</Heading>
	{#if isUserLecturer}
		<DeleteUnitModal {data} />
	{/if}
</div>

{#if !isUserLecturer}
	<div>
		<form class="mx-5 md:w-4/5 md:mx-auto" on:submit={handleSubmit}>
			<div class="flex-col md:flex-row gap-4 md:gap-8 w-full">
				<p class="text-black dark:text-gray-300">
					Write your reflection for this unit. Make sure not to include any sensitive or private
					information.
				</p>
				<Heading
					tag="h5"
					style="font-size: 1.5rem;"
					class="mt-2 text-xl text-gray-900 dark:text-white"
				>
					Questions
				</Heading>

				{#each data.course.questions as questionType}
					<div class="my-4">
						<Label for="question" class="text-sm block font-medium text-gray-900 dark:text-white"
							>{questionType.comment}</Label
						>
					</div>
					{#if data.reflected || !data.available}
						<Textarea
							id="question"
							name="answer"
							rows="4"
							placeholder="Write your thoughts here..."
							value={getReflectionByQuestion()}
							disabled={data.reflected || !data.available}
							style="resize: none"
							class="mb-4"
						/>
					{:else}
						<Textarea
							id="question"
							name="answer"
							rows="4"
							placeholder="Write your thoughts here..."
							style="resize: none"
							class="mb-4"
						/>
					{/if}

					<input name="question_id" bind:value={questionType.id} class="hidden" />
				{/each}

				{#if data.reflected}
					<div class="flex max-w-2xl flex-col">
						{#if data.available}
							<Heading tag="h1" class="mt-2">You have already reflected on this unit.</Heading>
						{:else}
							<Heading tag="h1" class="my-4">This unit is not ready for reflection.</Heading>
						{/if}
					</div>
				{:else if !data.reflected && !data.available}
					<div class="flex max-w-2xl">
						<Heading tag="h1" class="my-4">This unit is not ready for reflection.</Heading>
					</div>
				{:else}
					<div class="flex">
						<Button
							class="mr-8 mt-4 bg-teal-13 hover:bg-teal-10 dark:bg-blue-700 dark:hover:bg-blue-600 text-white"
							label="Submit"
							type="submit"
						>
							<PapperPlaneSolid class="w-3.5 h-3.5 mr-2" />
							Submit Reflection
						</Button>

						<Button
							color="alternative"
							class="box-border border-red-700 border-2 py-2 px-4 mt-4 text-red-700 dark:text-white dark:border-red-700 dark:hover:bg-red-700 dark:hover:border-red-700"
							type="submit"
							on:click={handleDecline}
						>
							<CloseOutline class="text-red-700 dark:text-white mr-2"></CloseOutline>
							Decline unit
						</Button>
					</div>
				{/if}
			</div>
		</form>
	</div>
{:else}
	<form class="mx-5 md:w-4/5 md:mx-auto" use:form>
		{#if isUnitOngoing}
			<P class="mb-4" size="sm"
				>This unit is already ongoing, so you cannot edit any of the values.</P
			>
		{/if}
		<div class="flex flex-col md:flex-row gap-4 md:gap-8 w-full mb-8">
			<div class="sm:w-96 w-80">
				<Label for="first_name" class="mb-2">Unit name</Label>
				<Input
					type="text"
					id="first_name"
					bind:value={unitName}
					placeholder="Introduction and team setup"
					disabled={isUnitOngoing}
				/>
				<Helper class="text-sm mt-1">The name of the unit, visible to the students.</Helper>
			</div>
			<div class="sm:w-96 w-80">
				<Label for="last_name" class="mb-2">Unit available from</Label>
				<Input
					type="date"
					id="last_name"
					bind:value={availableDate}
					placeholder={new Date()}
					disabled={isUnitOngoing}
				/>
				<Helper class="text-sm mt-1">
					The date the student should be able to submit their reflections on this unit.
				</Helper>
			</div>
		</div>

		<Heading tag="h5">Questions</Heading>
		<div class="flex flex-col gap-4 mt-4">
			{#if !isUnitOngoing}
				<Helper class="text-sm mt-1">The questions cannot be changed.</Helper>
			{/if}
			<Textarea
				class="resize-none md:w-1/2 w-3/4"
				placeholder="What was your best learning success in this unit? Why?"
				disabled
			/>
			<Textarea
				class="resize-none md:w-1/2 w-3/4"
				placeholder="What was your least understood concept in this unit? Why?"
				disabled
			/>
			{#if !isUnitOngoing}
				<div class="mt-6">
					<Button type="submit" size="md" class="w-36 bg-teal-13 text-white">
						Update unit
						<FileCirclePlusSolid class="w-4 h-4 ml-2" />
					</Button>
					<Button
						on:click={() =>
							goto(`${/courseview/ + data.course.semester + '/' + data.course.id}`, {
								replaceState: false
							})}
						size="md"
						class="w-24 ml-2 bg-gray-200 text-gray-900"
					>
						Cancel
					</Button>
				</div>
			{/if}
		</div>
	</form>
{/if}

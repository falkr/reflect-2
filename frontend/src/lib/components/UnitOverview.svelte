<script lang="ts">
	import { Input, Label, Helper, Textarea, Heading, P, Button } from 'flowbite-svelte';
	import { CloseOutline, FileCirclePlusSolid, PapperPlaneSolid } from 'flowbite-svelte-icons';
	import { validateUnitTitle } from '$lib/validation';
	import { toast } from 'svelte-french-toast';
	import { onMount } from 'svelte';
	import { goto, invalidate } from '$app/navigation';
	import { browser } from '$app/environment';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { createForm } from 'felte';
	import DeleteUnitModal from '$lib/components/DeleteUnitModal.svelte';

	export let data: any;
	export let unitName: string | undefined;
	export let unit_number: number;

	let availableDate = data.unit.unit.date_available;
	let isUnitOngoing: boolean = false;
	let isUserLecturer: boolean = data.role === 'lecturer';
	let decline: boolean = false;
	let answers: string[] = [];

	/**
	 * Edits the unit by making an API call to the backend server.
	 * The function sends a PATCH request to the server with the unit id, course id, course semester, title, date available, and hidden status.
	 * Upon successful update, it invalidates the course overview store and shows a success toast.
	 * On failure, it displays an error toast.
	 * @param form - The form data containing the unit title and date available.
	 */
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

	/**
	 * Configuration and hooks for the form used to edit a unit.
	 * This includes the submission process, success handling, error handling, and validation logic.
	 * Utilizes the Felte library to manage form state and behavior.
	 * @type {ReturnType<typeof createForm>} - Returns the form instance created by Felte, including properties for managing form state and handling submissions.
	 */
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
		decline = false;
	});

	/**
	 * Gets the reflection for the current question.
	 * The function shifts the first element from the answers array and returns it.
	 * If the answers array is empty, it returns an empty string.
	 * @returns The reflection for the current question.
	 */
	function getReflectionByQuestion() {
		let answerString = answers.shift();
		if (answerString == undefined) {
			return '';
		}
		return answerString;
	}

	/**
	 * Handles the decline button click event.
	 * Sets the decline variable to true.
	 */
	function handleDecline() {
		decline = true;
	}

	/**
	 * Handles the form submission event.
	 * The function creates a FormData object from the form data and calls the createReflection or declineReflection function based on the decline variable.
	 * @param e - The form submission event.
	 */
	function handleSubmit(e: SubmitEvent) {
		const formData = new FormData(e.target as HTMLFormElement);
		if (decline === false) {
			createReflection(formData);
		} else {
			declineReflection(formData);
		}
	}

	/**
	 * Creates a reflection for the unit.
	 * The function sends a POST request to the server with the user id, unit id, question id, and reflection body.
	 * Upon successful submission, it invalidates the layoutUser store and redirects to the course view page.
	 * On failure, it displays an error toast.
	 * @param form - The form data containing the reflection answers.
	 */
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

	/**
	 * Declines the unit by sending an empty reflection to the backend.
	 * The function sends a POST request to the server with the user id, unit id, and question id.
	 * Upon successful submission, it invalidates the layoutUser store and redirects to the course view page.
	 * On failure, it displays an error toast.
	 * @param form - The form data containing the question ids.
	 */
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

<!-- Delete unit modal component only showed to lecturers -->
<div class="mx-5 md:w-4/5 md:mx-auto mb-6 text-gray-900 dark:text-white flex">
	<Heading tag="h1" class="mt-2 text-xl">{'Unit ' + unit_number + ' - ' + unitName}</Heading>
	{#if isUserLecturer}
		<DeleteUnitModal {data} />
	{/if}
</div>

<!-- Reflection form shown for students when clicking on reflecct button -->
{#if !isUserLecturer}
	<div>
		<form class="mx-5 md:w-4/5 md:mx-auto" on:submit={handleSubmit}>
			<div class="flex-col md:flex-row gap-4 md:gap-8 w-full pb-8">
				<Heading
					tag="h5"
					style="font-size: 1.5rem;"
					class="mt-2 text-xl text-gray-900 dark:text-white"
				>
					Questions
				</Heading>

				{#each data.course.questions as questionType, index}
					<div class="my-4">
						<Label for="question" class="text-sm block font-medium text-gray-900 dark:text-white"
							>{questionType.comment}</Label
						>
					</div>
					<Textarea
						id={`question${index + 1}`}
						name="answer"
						rows="4"
						placeholder="Write your thoughts here..."
						value={getReflectionByQuestion()}
						disabled={data.reflected || !data.available}
						style="resize: none"
						class="mb-4"
					/>

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
							id="submitReflectionButton"
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
					<p class="pt-8 text-sm text-gray-400">
						Please note: Do not enter sensitive information, such as names of individuals. Your
						responses will be used to generate a report for the lecturer. Reflection Tool uses an AI
						service outside of NTNU to generate an aggregated report, but without the AI service
						knowing your identity. The lecturer will see an aggregated report from the entire class
						and all the responses, but will not know who wrote what.
					</p>
				{/if}
			</div>
		</form>
	</div>
	<!-- Edit/view unit form shown for lecturers when clicking on edit/view unit button -->
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
					id="editUnitName"
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
					id="editUnitDate"
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
					<Button
						id="editUnitSubmitButton"
						type="submit"
						size="md"
						class="w-36 bg-teal-13 text-white"
					>
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

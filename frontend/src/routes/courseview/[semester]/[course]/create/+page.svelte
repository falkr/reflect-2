<script lang="ts">
	import type { PageData } from './$types';
	import { invalidate } from '$app/navigation';
	import { validateUnitTitle } from '$lib/validation';
	import { Input, Label, Helper, Textarea, Heading, P, Button } from 'flowbite-svelte';
	import { FileCirclePlusSolid } from 'flowbite-svelte-icons';
	import { createForm } from 'felte';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import toast from 'svelte-french-toast';
	import { PUBLIC_API_URL } from '$env/static/public';
	export let data: PageData;

	let unitName = '';
	let availableDate = '';

	/**
	 * Asynchronously creates a new unit within a course using data submitted via the form.
	 * This function constructs a POST request with the new unit's details and handles the response.
	 * If successful, the course overview cache is invalidated to reflect the new unit.
	 *
	 * @param {FormData} form - The FormData object containing details of the new unit to be created.
	 * @returns {Promise<{result: any, status: number}>} - The JSON result of the API call and the HTTP status code.
	 */
	async function createUnit(form: FormData) {
		if (!unitName || !availableDate) {
			toast.error('Please fill in all fields');
			return;
		}

		const response = await fetch(`${PUBLIC_API_URL}/create_unit`, {
			method: 'POST',
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
	 * Configuration and hooks for the form used to create a new unit. This includes the submission
	 * process, success handling, error handling, and validation logic.
	 * Utilizes the Felte library to manage form state and behavior.
	 *
	 * @type {ReturnType<typeof createForm>} - Returns the form instance created by Felte, including properties for managing form state and handling submissions.
	 */
	const { form, errors, isSubmitting } = createForm({
		//on submit, create a course
		onSubmit: async (values, { form }) => {
			const formData = new FormData(form as HTMLFormElement);
			return createUnit(formData);
		},
		onSuccess(response) {
			const castedResponse = response as Response;
			if (castedResponse.status == 200) {
				window.history.back();
				toast.success('Unit created successfully', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			}
			if (castedResponse.status == 409) {
				toast.error('An error occurred while creating the unit');
			}
		},

		//validates the form on submitting
		validate: (values) => {
			const errors: Partial<FormValues> = {};
			if ($isSubmitting) {
				const titleErrors = validateUnitTitle(values.title);
				if (titleErrors) {
					console.log('------ errrrooo');

					errors.title = Array.isArray(titleErrors) ? titleErrors : [titleErrors];
				}
			}
		}
	});
</script>

<Breadcrumb
	breadcrumbItems={[
		{
			href: '/courseview/' + data.course.semester + '/' + data.course.id,
			label: data.course.id
		},
		{
			label: 'New unit'
		}
	]}
/>
<!--  Form for creating a new unit within a course. -->
<form class="mx-5 md:w-4/5 md:mx-auto" use:form>
	<div class="flex flex-col md:flex-row gap-4 md:gap-8 w-full mb-8">
		<div class="sm:w-96 w-80">
			<Label for="first_name" class="mb-2">Unit name</Label>
			<Input
				bind:value={unitName}
				type="text"
				id="unitNameCreate"
				name="first_name"
				placeholder="Unit name"
				required
			/>
			<Helper class="text-sm mt-1">The name of the unit, visible to the students.</Helper>
		</div>
		<div class="sm:w-96 w-80">
			<Label for="last_name" class="mb-2">Unit available from</Label>
			<Input
				bind:value={availableDate}
				type="date"
				id="unitDateCreate"
				name="last_name"
				placeholder={new Date()}
				required
			/>
			<Helper class="text-sm mt-1">
				The date the student should be able to submit their reflections on this unit.
			</Helper>
		</div>
	</div>

	<Heading tag="h5">Questions</Heading>
	<div class="flex flex-col gap-4 mt-4">
		<Helper class="text-sm mt-1">The questions cannot be changed.</Helper>
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
		<div class="mt-6">
			<Button
				type="submit"
				id="createUnitSubmitButton"
				size="md"
				class="w-36 bg-teal-13 hover:bg-teal-10 dark:bg-blue-700 dark:hover:bg-blue-600 text-white"
			>
				Create unit
				<FileCirclePlusSolid class="w-4 h-4 ml-2" />
			</Button>
			<Button
				on:click={() => window.history.back()}
				size="md"
				class="w-24 ml-2 bg-gray-200 text-gray-900 hover:bg-gray-100"
			>
				Cancel
			</Button>
		</div>
	</div>
</form>

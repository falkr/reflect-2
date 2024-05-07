<script lang="ts">
	import { invalidate } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Button, Modal, Label, Input, Select } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { createForm } from 'felte';
	import { validateCourseId, validateCourseName, validateCourseSemester } from '$lib/validation';
	import { toast } from 'svelte-french-toast';
	import CourseCards from '$lib/components/CourseCards.svelte';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	export let data: Data;

	let defaultModal = false;
	let courseToBeMade = '';
	let selected = '';
	let semesterOptions: { value: string; name: string }[] = [];

	/**
	 * Fills the semester options for the dropdown in the form. It generates semester options for the current year
	 * and the next four years, with each year having a 'Spring' and 'Fall' semester.
	 */
	function fillSemesterOptions() {
		let currentYear = new Date().getFullYear();
		for (let i = 0; i < 5; i++) {
			semesterOptions.push({
				value: 'spring' + (currentYear + i),
				name: 'Spring ' + (currentYear + i)
			});
			semesterOptions.push({
				value: 'fall' + (currentYear + i),
				name: 'Fall ' + (currentYear + i)
			});
		}
	}

	/**
	 * Executes when the component mounts. It invalidates the user layout cache and fills the semester options
	 * for the course creation form.
	 */
	onMount(async () => {
		invalidate('app:layoutUser');
		fillSemesterOptions();
	});

	//filtering the courses based on role
	$: course_student = data.user.enrollments.filter((enrollment) => enrollment.role === 'student');
	$: course_lecturer = data.user.enrollments.filter((enrollment) => enrollment.role === 'lecturer');
	$: course_ta = data.user.enrollments.filter(
		(enrollment) => enrollment.role === 'teaching assistant'
	);

	let selectedSemester: FormDataEntryValue | null;

	/**
	 * Asynchronously creates a new course with the specified details from the form submission.
	 * It constructs a POST request to the backend API and handles the response by returning
	 * the result and status of the API call.
	 *
	 * @param {FormData} form - FormData object containing the new course details.
	 * @returns {Promise<{result: any, status: number}>} - The result of the API call and the HTTP status.
	 */
	async function createCourse(form: FormData) {
		const name = form.get('name');
		const id_str = form.get('course_id')?.toString().toUpperCase() as string;
		courseToBeMade = id_str;
		selectedSemester = form.get('semester');
		const response = await fetch(`${PUBLIC_API_URL}/create_course`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				name: name,
				id: id_str,
				semester: selectedSemester
			})
		});
		const status = response.status;
		const result = await response.json();
		return { result, status };
	}

	/**
	 * Enrolls the user as a lecturer for the newly created course. This function makes a POST request
	 * to the backend API. It handles response status and displays toast messages based on the outcome.
	 */
	async function enrollUserAsLecturer() {
		const course_id = courseToBeMade;
		const role = 'lecturer';
		if (selectedSemester == null) {
			toast.error('Failed setting semester!');
			return;
		}

		const response = await fetch(`${PUBLIC_API_URL}/enroll`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				course_id: course_id,
				role: role,
				course_semester: selectedSemester
			})
		});
		const status = response.status;
		invalidate('app:layoutUser');
		if (status != 200) {
			toast.error("Couldn't enroll lecuturer!");
		} else {
			toast.success('Course successfully created!', {
				iconTheme: {
					primary: '#36786F',
					secondary: '#FFFFFF'
				}
			});
		}
	}

	/**
	 * Sets up the Felte form configuration for the create course form. This includes defining the form submission
	 * behavior, handling successful or conflicting submissions, and providing field validation.
	 *
	 * @type {ReturnType<typeof createForm>} - Returns the form instance created by Felte, including properties for managing form state and handling submissions.
	 */
	const { form, errors, isSubmitting } = createForm({
		//on submit, create a course
		onSubmit: async (values, { form }) => {
			const formData = new FormData(form as HTMLFormElement);
			return createCourse(formData);
		},
		onSuccess(response) {
			const castedResponse = response as Response;
			if (castedResponse.status == 200) {
				defaultModal = false;

				enrollUserAsLecturer();
			}
			if (castedResponse.status == 409) {
				defaultModal = true;
				toast.error("Couldn't create course, course already exists for this semester.");
			}
		},

		//validates the form on submitting
		validate: (values) => {
			const errors: Partial<FormValues> = {};
			if ($isSubmitting) {
				const nameError = validateCourseName(values.name);
				const courseIdError = validateCourseId(values.course_id);
				if (nameError) {
					errors.name = Array.isArray(nameError) ? nameError : [nameError];
				}
				if (courseIdError) {
					errors.course_id = Array.isArray(courseIdError) ? courseIdError : [courseIdError];
				}
				errors.semester = validateCourseSemester(values.semester);
				return errors;
			}
		}
	});
</script>

<Breadcrumb />
<div>
	{#if data.user.enrollments.length == 0}
		<div class="justify-center align-center self-center text-center">
			<img
				src="/walking-in-rain-illustration-light.svg"
				alt="Walking in rain illustration"
				class="h-40 w-40 md:h-80 md:w-80 align-center self-center justify-center mx-auto mb-5 dark:hidden"
			/>
			<img
				src="/walking-in-rain-illustration-dark.svg"
				alt="Walking in rain illustration"
				class="h-40 w-40 md:h-80 md:w-80 align-center self-center justify-center mx-auto mb-5 hidden dark:block"
			/>
			<p class="mt-12 text-black dark:text-gray-300">
				You are not enrolled to any course yet<br />
				{#if data.user.admin}
					(As a lecturer, create a new course by clicking the create course button)
				{:else}
					(As a student, ask your lecturer to enroll you in a course)
				{/if}
			</p>
		</div>
	{/if}
	<div
		class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 lg:w-4/5 gap-5 sm:gap-12 w-4/5 my-5 sm:mt-10 mx-auto"
	>
		{#if course_lecturer.length > 0}
			<CourseCards courses={course_lecturer} role={'Lecturer'} />
		{/if}
		{#if course_ta.length > 0}
			<CourseCards courses={course_ta} role={'Teaching Assistant'} />
		{/if}
		{#if course_student.length > 0}
			<CourseCards courses={course_student} role={'Student'} />
		{/if}
	</div>

	<!--Create course button-->
	{#if data.user.admin}
		<div class="fixed bottom-3 right-3 md:mb-8 md:mr-12 flex justify-center md:justify-end">
			<Button
				on:click={() => (defaultModal = true)}
				id="createCourseButton"
				class="text-white bg-teal-13 hover:bg-teal-9 dark:bg-blue-700 dark:hover:bg-blue-600 focus:ring-4 focus:outline-none focus:ring-teal-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-blue-800"
			>
				Create new course
				<svg
					class="ml-2 w-5 h-5 text-white dark:text-white"
					aria-hidden="true"
					xmlns="http://www.w3.org/2000/svg"
					width="20"
					height="20"
					fill="none"
					viewBox="0 0 24 24"
				>
					<path
						stroke="currentColor"
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M5 12h14m-7 7V5"
					/>
				</svg>
			</Button>
		</div>
	{/if}

	<!--Create course modal-->
	<Modal bind:open={defaultModal} size="xs" autoclose={false} class="w-full" id="createCourseModal">
		<form class="flex flex-col space-y-6" use:form>
			<h3 class="p-0 text-xl text-center mb-5 font-normal text-gray-900 dark:text-white">
				Create new course
			</h3>
			<Label class="space-y-2">
				<span>Course name</span>
				<Input
					id="courseNameInput"
					type="text"
					name="name"
					placeholder="(e.g. Object-Oriented Programming)"
					required
				/>
			</Label>
			<small>
				{#if $errors.name}
					{#each $errors.name as error}
						<p class="text-red-500">{error}</p>
					{/each}
				{/if}
			</small>
			<Label class="space-y-2">
				<span>Course ID</span>
				<Input
					id="courseIdInput"
					type="text"
					name="course_id"
					placeholder="(e.g. TDT4100)"
					required
				/>
			</Label>
			<small>
				{#if $errors.course_id}
					{#each $errors.course_id as error}
						<p class="text-red-500">{error}</p>
					{/each}
				{/if}
			</small>
			<Label class="space-y-2">
				<span>Semester</span>
				<Select
					class="mt-2"
					id="selectSemester"
					items={semesterOptions}
					bind:value={selected}
					placeholder="Select semester"
					required
					name="semester"
				/>
			</Label>
			<small>
				{#if $errors.semester}
					{#each $errors.semester as error}
						<p class="text-red-500">{error}</p>
					{/each}
				{/if}
			</small>

			<Button
				type="submit"
				id="createCourseSubmit"
				data-modal-target="defaultModal"
				data-modal-toggle="defaultModal"
				class="w-full1 bg-teal-13 hover:bg-teal-9 dark:bg-blue-700 dark:hover:bg-blue-600"
				>Create</Button
			>
		</form>
	</Modal>
</div>

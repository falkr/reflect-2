<script lang="ts">
	import { invalidate } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public';
	import CourseTable from '$lib/components/CourseTable.svelte';
	import { Button, Modal, Label, Input, Select, Toast } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { createForm } from 'felte';
	import { validateCourseId, validateCourseName, validateCourseSemester } from '$lib/validation';
	import { slide } from 'svelte/transition';
	import { AlertCircleIcon, CheckCircleIcon } from 'svelte-feather-icons';
	export let data: Data;

	let defaultModal = false;

	let courseToBeMade = '';
	//selected option in semester dropwdown
	let selected = '';
	//semester dropdown values
	let semesterOptions: { value: string; name: string }[] = [];
	//function for filling dropdown select values
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

	//onmount updates the site directly!
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

	//action for creatign a course
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

	async function enrollUserAsLecturer() {
		const course_id = courseToBeMade;
		const role = 'lecturer';
		if (selectedSemester == null) {
			triggerToast('Failed setting semester!', 'error');
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
			triggerToast("Couldn't enroll lecuturer!", 'error');
		} else {
			triggerToast('Course successfully created!', 'success');
		}
	}

	//form to use
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
				triggerToast("Couldn't create course!", 'error');
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

	let showError = false;

	let showSuccess = false;

	let counter = 6;
	let toastBody = '';

	export function triggerToast(body: string, type: string) {
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
</script>

<div class="p flex flex-col">
	<div class="flex items-center justify-center pl-4 pr-4 pt-10 pb-10">
		<div class="header flex items-center justify-center border-b-2 border-teal-12 pb-3">
			<h3 class="headline flex text-center text-xl font-bold text-teal-12">
				<p class="flex text-center text-xl font-medium text-teal-12">Course overview</p>
			</h3>
		</div>
	</div>

	{#if data.user.admin}
		<div class="buttonContainer top-64 right-10 flex justify-center md:mr-16 md:justify-end">
			<Button
				on:click={() => (defaultModal = true)}
				class="rounded-full border-teal-8 bg-teal-8 px-3 py-2 hover:border-teal-7 hover:bg-teal-7"
				size="xl"
			>
				+ Create new course
			</Button>
		</div>
	{/if}

	<div
		class="tablesContainer w-6/7 mb-8 mt-8 flex flex-col items-center justify-center gap-10 md:ml-16 md:w-3/4 md:flex-row md:items-start md:justify-start"
	>
		{#if data.user.enrollments.length == 0}
			<p class="font-large text-base text-teal-12">You are not enrolled to any course yet</p>
		{/if}
		{#if course_lecturer.length > 0}
			<CourseTable courses={course_lecturer} role={'Lecturer'} />
		{/if}
		{#if course_ta.length > 0}
			<CourseTable courses={course_ta} role={'Teaching Assistant'} />
		{/if}
		{#if course_student.length > 0}
			<CourseTable courses={course_student} role={'Student'} />
		{/if}
	</div>

	<Modal bind:open={defaultModal} size="xs" autoclose={false} class="w-full">
		<form class="flex flex-col space-y-6" use:form>
			<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Create new course</h3>
			<Label class="space-y-2">
				<span>Course name</span>
				<Input type="text" name="name" placeholder="Kompilatorteknikk" required />
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
				<Input type="text" name="course_id" placeholder="tdt4100" required />
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
					items={semesterOptions}
					bind:value={selected}
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
				data-modal-target="defaultModal"
				data-modal-toggle="defaultModal"
				class="w-full1 bg-teal-9 hover:bg-teal-8">Create new course</Button
			>
		</form>
	</Modal>

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

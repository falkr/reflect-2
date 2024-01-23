<script lang="ts">
	import { goto, invalidate } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public';
	import CourseTable from '$lib/components/CourseTable.svelte';
	import { Button, Modal, Label, Input, Select, Toast } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { createForm } from 'felte';
	import { validateCourseId, validateCourseName, validateCourseSemester } from '$lib/validation';
	import { slide } from 'svelte/transition';
	import { AlertCircleIcon, CheckCircleIcon } from 'svelte-feather-icons';

	export let data;

	let defaultModal = false;

	let courseToBeMade: string = '';
	//selected option in semester dropwdown
	let selected: string = '';
	//semester dropdown values
	let semesterOptions: string[] = [];
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

	let selectedSemester;

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
			triggerToast("Failed setting semester!", 'error');
			return 
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
		const js = await response.json();
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
			//response is not typed, hence the red line! Needs to be handled
			if (response.status == 200) {
				defaultModal = false;

				enrollUserAsLecturer();
			}
			if (response.status == 409) {
				defaultModal = true;
				triggerToast("Couldn't create course!", 'error');
			}
		},

		//validates the form on submitting
		validate: (values) => {
			const errors = {};
			if ($isSubmitting) {
				errors.name = validateCourseName(values.name);
				errors.course_id = validateCourseId(values.course_id);
				errors.semester = validateCourseSemester(values.semester);

				return errors;
			}
		}
	});

	let showError: boolean = false;

	let showSuccess: boolean = false;

	let counter: number = 6;
	let toastBody: string = '';

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
	<div class="flex justify-center items-center pl-4 pr-4 pt-10 pb-10">
		<div class="header border-teal-12 flex justify-center items-center border-b-2 pb-3 ">
			<h3 class="headline text-teal-12 flex text-center text-xl font-bold">
				<p class="text-teal-12 flex text-center text-xl font-medium">Course overview</p>
			</h3>
		</div>
	</div>

	{#if data.user.admin}
		<div class="buttonContainer top-64 right-10 flex justify-center md:mr-16 md:justify-end">
			<Button
				on:click={() => (defaultModal = true)}
				class="bg-teal-8 border-teal-8 hover:border-teal-7 hover:bg-teal-7 rounded-full px-3 py-2"
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
			<p class="text-teal-12 font-large text-base">You are not enrolled to any course yet</p>
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
			simple
			transition={slide}
			bind:open={showSuccess}
			divClass="w-full max-w-sm p-5"
		>
			<svelte:fragment slot="icon">
				<CheckCircleIcon />
			</svelte:fragment>
			<div class="text-[1.5em]">{toastBody}</div>
		</Toast>

		<Toast position="bottom-right" simple transition={slide} bind:open={showError}>
			<svelte:fragment slot="icon">
				<AlertCircleIcon />
			</svelte:fragment>
			<div class="text-[1.5em]">{toastBody}</div>
		</Toast>
	</div>
</div>

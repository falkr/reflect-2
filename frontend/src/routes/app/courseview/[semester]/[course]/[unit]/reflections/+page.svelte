<script lang="ts">
	import type { PageData } from './$types';
	import { Button, Dropdown, DropdownItem, Modal, Label, Input, Toast } from 'flowbite-svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto, invalidate } from '$app/navigation';
	import { CheckCircleIcon } from 'svelte-feather-icons';
	import { slide } from 'svelte/transition';

	export let data: PageData;
	let unitModal = false;

	// updates UI
	let key = 0;

	//dummy data used if new report
	let dummyData: report_obj[] = [
		{
			name: 'IMPORTANT FEEDBACK',
			answers: []
		},
		{
			name: 'NOT RELEVANT',
			answers: []
		}
	];

	let reportContent: report_obj[] = [];

	//fills the reportContent
	function fillReportThemes() {
		if (data.unitReportContent !== undefined) {
			if (data.unitReportContent.report_content.length == 0) {
				reportContent = dummyData;
			} else {
				reportContent = data.unitReportContent.report_content;
			}
		} else {
			reportContent = dummyData;
		}
	}
	fillReportThemes();

	//updates backend
	async function edit_created_report() {
		const course_id = data.course.id;
		const course_semester = data.course.semester;
		const unit_id = data.unit_id;
		const repContent = reportContent;

		const response = await fetch(`${PUBLIC_API_URL}/edit_created_report`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				course_id: course_id,
				course_semester: course_semester,
				unit_id: unit_id,
				report_content: repContent
			})
		});
		const js = await response.json();
		triggerToast('Report saved!', 'success');
		invalidate('app:courseOverview');
		return { js };
	}

	//adds new created theme to objects
	function handleAddCategory(e: SubmitEvent) {
		e.preventDefault();
		const formData = new FormData(e.target as HTMLFormElement);
		addCategory(formData);
		unitModal = false;
	}

	//adds theme to existing objects
	function addCategory(form: FormData) {
		reportContent = [
			...reportContent,
			{
				name: form.get('theme') as string,
				answers: []
			}
		];
	}

	//handle adding answers to list
	function addAnswerToCategory(categoryName: string, answer: string) {
		//find object list
		const category = reportContent.filter((category) => category.name === categoryName)[0];

		//if answerlist contains the answer to be added
		if (category.answers.filter((answerFromList) => answerFromList === answer).length === 0) {
			category.answers.push(answer);
		} else {
			alert(answer + 'already in list');
		}

		key = key + 1;
	}

	//handle adding answers to list
	function removeAnswerFromCategory(categoryName: string, answer: string) {
		//find object list
		const category = reportContent.filter((category) => category.name === categoryName)[0];

		//if answerlist contains the answer to be added
		if (category.answers.filter((answerFromList) => answerFromList === answer).length > 0) {
			category.answers = category.answers.filter((answerFromList) => {
				return answerFromList !== answer;
			});
		} else {
			alert(answer + 'not in list');
		}
		key = key + 1;
	}

	function removeThemeFromCategory(categoryName: string) {
		const categoryIndex = reportContent.findIndex((category) => category.name === categoryName);

		if (categoryIndex === -1) {
			alert(`${categoryName} not found in reportContent`);
			return;
		}
		reportContent.splice(categoryIndex, 1);
		key = key + 1;
	}

	//filters answers
	function filterAnswers(answer: string) {
		let existsInLists = reportContent.map(
			(content) => content.answers.includes(answer, 0) === true
		);
		let exists = existsInLists.includes(true, 0);
		return exists;
	}

	let showError = false;

	let showSuccess = false;

	let counter = 6;
	let toastBody = '';

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
</script>

{#key { key }}
	<div class="relative">
		<div class="left-0 top-0 ml-3 md:absolute">
			<Button
				on:click={() => goto(`/app/courseview/${data.course.id}`)}
				class=" hover:text-teal-8 mt-2 "
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
				<p class="ml-2">Back to courseview</p>
			</Button>
		</div>

		<span
			class="text-primary mx-8 mt-4 flex items-center justify-center text-[20px] font-bold md:text-xl"
			>Reflections on {data.course.id} for unit "{data.unitName}"</span
		>
	</div>
	{#if data.answers.length == 0}
		<div class="text-primary mx-8 mt-8 flex items-center justify-center text-lg italic">
			There are no reflections yet. When there are reflections on this unit, you will be able to
			edit the report.
		</div>
	{:else}
		<!-- mother div -->
		<div class="mt-8 p-2">
			<!-- inside div -->
			<div class="flex flex-row flex-wrap justify-between md:flex-nowrap">
				<!-- form div -->
				<div class="flex flex-col">
					<div class="text-primary text-center text-xl">Reflections from students</div>

					<form class="button-container my-2 justify-center align-middle">
						<p class=" my-4 mb-4 flex max-w-2xl flex-col gap-y-4 md:mx-8">
							{#each data.course.questions as question}
								{#if data.answers.filter((a) => a.question_id === question.id).length > 0}
									<div
										class="b flex max-h-[500px] w-full flex-col gap-y-4 overflow-auto p-2 md:w-full"
									>
										<label class="text-primary italic" for="reflection-{question.id}">
											{question.comment}
										</label>

										<div class="">
											{#each data.answers as answer}
												{#if answer.question_id === question.id}
													{#if filterAnswers(answer.body) === true}
														<div />
													{:else}
														<div
															class=" text-primary mb-4 flex w-full flex-row justify-between rounded-lg border bg-white p-4"
															id="reflection-{question.id}"
														>
															<div class="max-h-24 overflow-auto text-sm md:text-base">
																{answer.body}
															</div>
															<Button class="w-4.1 bg-teal-9 hover:bg-teal-11 ml-3 h-2.5">
																Add
															</Button>
															<Dropdown>
																{#each reportContent as report}
																	<DropdownItem
																		on:click={() => addAnswerToCategory(report.name, answer.body)}
																		>{report.name}</DropdownItem
																	>
																{/each}
															</Dropdown>
														</div>
													{/if}
												{/if}
											{/each}
										</div>
									</div>
								{/if}
							{/each}
						</p>
					</form>
				</div>

				<!-- report div -->
				<div class="flex w-full flex-col md:w-[50%]">
					<div class="text-primary text-center text-xl">Categories</div>
					<div class=" relative my-2 flex flex-row justify-between">
						<div
							class="my-4 flex w-9/12 flex-col justify-evenly gap-y-4 rounded-lg border bg-gray-100"
						>
							{#each reportContent as report}
								<div
									class=" text-primary text-transform: bg-teal-7 flex flex-row items-center justify-between rounded-lg text-lg font-bold uppercase"
								>
									<p class="ml-4 text-[12px] md:text-base">
										{report.name}
									</p>
									<Button
										class="hover:bg-teal-8 "
										outline
										color="alternative"
										on:click={() => removeThemeFromCategory(report.name)}
									>
										X
									</Button>
								</div>

								<div class="ml-2 max-h-[350px] overflow-auto">
									{#each report.answers as answer}
										<div
											class="my-2 flex w-11/12 flex-row justify-between rounded-lg border bg-white p-4"
										>
											<div class="max-h-24 overflow-auto text-sm md:text-base">
												{answer}
											</div>
											<Button
												class="bg-teal-9 hover:bg-teal-11 ml-4 h-2 w-2 "
												on:click={() => removeAnswerFromCategory(report.name, answer)}
											>
												x
											</Button>
										</div>
									{/each}
								</div>
							{/each}
						</div>
						<div class="buttonContainer flex flex-col">
							<Button
								on:click={() => edit_created_report()}
								id="download"
								type="submit"
								class="bg-teal-9 hover:bg-teal-8 ml-8 h-10 w-16 md:h-10 md:w-36">Save</Button
							>
							<Button
								id="add"
								on:click={() => (unitModal = true)}
								class="bg-teal-9 hover:bg-teal-8 ml-8 mt-[20px] h-10 w-16 md:h-10 md:w-36"
								>Add category</Button
							>
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
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<Modal bind:open={unitModal} size="xs" autoclose={false} class="w-full">
		<form class="flex flex-col space-y-6" on:submit|preventDefault={handleAddCategory}>
			<Label class="space-y-2">
				<span>Theme</span>
				<Input type="text" id="theme" name="theme" placeholder="theme" required />
			</Label>
			<Button
				type="submit"
				data-modal-target="unitModal"
				data-modal-toggle="unitModal"
				class="w-full1 bg-teal-9 hover:bg-teal-8">Add theme</Button
			>
		</form>
	</Modal>
{/key}

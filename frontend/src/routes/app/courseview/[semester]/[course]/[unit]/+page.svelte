<script lang="ts">
	import type { PageData } from './$types';
	import { Button } from 'flowbite-svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto, invalidate } from '$app/navigation';
	import { browser } from '$app/environment';
	export let data: PageData;

	//showing done reflections
	let answers: string[] = [];
	function getReflections() {
		//filter on all that belongs to this unit
		let reflections = data.user.reflections.filter(
			(reflection) => reflection.unit_id == data.unit_id
		);

		// get all the answers from the objects
		reflections.forEach((reflection) => {
			answers.push(reflection.body);
		});
	}

	getReflections();

	//list for indexes of questions.. need to render these
	let question_numbers: number[] = [];

	for (let index = 0; index < data.course.questions.length; index++) {
		question_numbers.push(index + 1);
	}

	//return the question Numbers
	function getQuestionNumber() {
		return question_numbers.shift();
	}

	//return the reflection by question
	function getReflectionByQuestion() {
		let answerString = answers.shift();
		if (answerString == undefined) {
			return '';
		}

		return answerString;
	}

	//for submitting reflection
	async function createReflection(form: FormData) {
		let questions = form.getAll('question_id');
		let answers = form.getAll('answer');

		//parse question_id to numbers
		let questions_num = questions.map(function (item) {
			return parseInt(item.toString());
		});

		let promises = [];

		for (let index = 0; index < questions.length; index++) {
			//sends #question_id reflections to backend
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

		Promise.all(promises).then(() => {
			if (browser) {
				invalidate('app:layoutUser').then(() => {
					goto(`/app/courseview/${data.course.id}`);
				});
			}
		});
	}

	function handleSubmit(e: SubmitEvent) {
		const formData = new FormData(e.target as HTMLFormElement);
		createReflection(formData);
	}
</script>

<main class="flex-shrink-0">
	<div class="relative">
		<div class="flex items-center justify-center pl-4 pr-4 pt-10">
			<div class="">
				<h3 class="headline flex text-left text-xl font-bold text-teal-12">
					{data.course.id}
					<p class="ml-3 mr-3">-</p>
					<p class="text-xl font-medium text-teal-12" style="word-break: break-word">
						{data.units.find((unit) => unit.id == data.unit_id)?.title}
					</p>
				</h3>
			</div>
			<Button
				on:click={() => history.back()}
				class=" absolute left-0 top-1 mt-2 w-52 hover:text-teal-8"
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
				<p class="ml-2 text-left">Back to units</p>
			</Button>
		</div>
	</div>
	<form class="flex justify-center pl-1 align-middle md:pl-20" on:submit={handleSubmit}>
		<p class="mx-8 my-8 mb-4 max-w-2xl">
			{#each data.course.questions as questionType}
				<div class="mt-10 flex">
					<div class="">
						{getQuestionNumber() + ')'}
					</div>
					<label
						for="question"
						class="text-ms ml-2 mb-2 block font-medium text-gray-900 dark:text-white"
						>{questionType.comment}</label
					>
				</div>

				{#if data.reflected || !data.available}
					<textarea
						id="question"
						name="answer"
						rows="4"
						class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-teal-12 focus:ring-teal-12 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-teal-12 dark:focus:ring-teal-12"
						placeholder="Write your thoughts here..."
						value={getReflectionByQuestion()}
						disabled={data.reflected || !data.available}
						style="resize: none"
					/>
				{:else}
					<textarea
						id="question"
						name="answer"
						rows="4"
						class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-teal-12 focus:ring-teal-12 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-teal-12 dark:focus:ring-teal-12"
						placeholder="Write your thoughts here..."
						style="resize: none"
					/>
				{/if}

				<input name="question_id" bind:value={questionType.id} class="hidden" />
			{/each}

			{#if data.reflected}
				<div class="my-8 mb-4 flex max-w-2xl flex-col">
					{#if data.available}
						<p class="self-center text-[18px] italic text-teal-12">
							You have already reflected on this unit
						</p>
						<Button
							on:click={() => goto(`/app/courseview/${data.course.id}`)}
							class="mt-2 self-center bg-teal-9 hover:bg-teal-8 "
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
					{:else}
						<p class="self-center text-[18px] italic text-teal-12">
							This unit is not ready for reflection
						</p>
					{/if}
				</div>
			{:else if !data.reflected && !data.available}
				<div class="my-8 mb-4 flex max-w-2xl">
					<p class="self-center pb-20 text-[18px] italic text-teal-12">
						This unit is not ready for reflection
					</p>
				</div>
			{:else}
				<div class="my-8 flex">
					<Button type="submit" class=" w-full1 self-center bg-teal-9 hover:bg-teal-8 "
						>Send reflection</Button
					>
				</div>
			{/if}
		</p>
	</form>
</main>

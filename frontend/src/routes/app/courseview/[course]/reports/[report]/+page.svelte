<script lang="ts">
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import { Button } from 'flowbite-svelte';
	export let data: PageData;
	let filename: string = 'reflections.txt';
	let content = data.unitReportContent.toString();

	//function for downloading report, downloads a .txt file
	function downloadFile(filename: string, content: string) {
		const element = document.createElement('a');
		const reportContent = data.unitReportContent.report_content;
		let fileContent = '';
		let previousAnswer = '';
		for (const { name, answers } of reportContent) {
			fileContent += `${name}\n`;
			for (const answer of answers) {
				const words = answer.split(' ');
				let currentLine = '';
				if (answer !== previousAnswer) {
					currentLine = '- ';
				}
				for (let i = 0; i < words.length; i++) {
					const word = words[i];
					if (currentLine.length + 1 + word.length > 80) {
						fileContent += `${currentLine}\n`;
						currentLine = '';
					}
					currentLine += (currentLine === '' ? '' : ' ') + word;
				}
				fileContent += `${currentLine}\n`;
				previousAnswer = answer;
			}
			fileContent += '\n';
		}
		const blob = new Blob([fileContent], { type: 'plain/text' });
		const fileUrl = URL.createObjectURL(blob);
		element.setAttribute('href', fileUrl);
		element.setAttribute('download', filename);
		element.style.display = 'none';
		document.body.appendChild(element);
		element.click();
		document.body.removeChild(element);
	}
</script>

<div class="mx-5 ml-1 flex flex-col gap-y-6 md:mx-16 md:ml-16 md:p-4">
	<div class="flex justify-start">
		<Button
			on:click={() => goto(`/app/courseview/${data.course.id}`)}
			class=" hover:text-teal-8 w-42 absolute"
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
			<p class="ml-2 text-left">Back to courseview</p>
		</Button>
	</div>
	<div
		class="header border-teal-12 mt-8 flex w-[350px] flex-col justify-center border-b-2 pb-3 md:w-[400px]"
	>
		<h3 class="headline text-teal-12 flex text-left text-[20px] font-bold md:text-xl">
			{data.course.id}
			<span class="ml-3 mr-3">-</span>
			<span class="text-teal-12 text-[20px] font-medium md:text-xl">
				Report for {data.course.id}
			</span>
		</h3>
	</div>
	<Button
		class="bg-teal-9 hover:bg-teal-11 w-36 rounded-md py-2 px-4 text-white transition duration-150 ease-in-out"
		on:click={() => downloadFile(filename, content)}
	>
		Download report
	</Button>
	{#if data.unitReportContent.report_content.length > 0}
		<div class="grid gap-4 md:grid-cols-2">
			{#each data.unitReportContent.report_content as report_content}
				<div class="mb-4">
					<div class="font-medium">{report_content.name}</div>
					<textarea
						disabled={true}
						class="focus:border-teal-12 focus:ring-teal-12 dark:focus:border-teal-12 dark:focus:ring-teal-12 mt-4 block h-40 w-full min-w-[300px] max-w-[500px] overflow-y-scroll rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 md:max-h-[500px]"
						rows={report_content.answers.length}
						>{report_content.answers.map((answer) => `- ${answer}`).join('\n\n')}
					</textarea>
				</div>
			{/each}
		</div>
	{:else}
		<div>You have not generated a report</div>
	{/if}
</div>

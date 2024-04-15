<script lang="ts">
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import { Button } from 'flowbite-svelte';
	export let data: PageData;
	let filename = 'reflections.txt';
	//let content = data.unitReportContent.toString();

	//function for downloading report, downloads a .txt file
	function downloadFile(filename: string) {
		const element = document.createElement('a');
		const reportContent = data.unitReportContent?.report_content || [];
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

	// Define a function to process answers into a formatted string
	function formatAnswers(answers: string[]) {
		return answers.map((answer) => `- ${answer}`).join('\n\n');
	}
</script>

<div class="mx-5 ml-1 flex flex-col gap-y-6 md:mx-16 md:ml-16 md:p-4">
	<div class="flex justify-start"></div>
	<div
		class="header mt-8 flex w-[350px] flex-col justify-center border-b-2 border-teal-12 pb-3 md:w-[400px]"
	>
		<h3 class="headline flex text-left text-[20px] font-bold text-teal-12 md:text-xl">
			{data.course.id}
			<span class="ml-3 mr-3">-</span>
			<span class="text-[20px] font-medium text-teal-12 md:text-xl">
				Report for {data.course.id}
			</span>
		</h3>
	</div>
	<Button
		class="w-36 rounded-md bg-teal-9 py-2 px-4 text-white transition duration-150 ease-in-out hover:bg-teal-11"
		on:click={() => downloadFile(filename)}
	>
		Download report
	</Button>
	{#if data.unitReportContent && data.unitReportContent.report_content.length > 0}
		<div class="grid gap-4 md:grid-cols-2">
			{#each data.unitReportContent.report_content as report_content}
				<div class="mb-4">
					<div class="font-medium">{report_content.name}</div>
					<textarea
						disabled={true}
						class="mt-4 block h-40 w-full min-w-[300px] max-w-[500px] overflow-y-scroll rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-teal-12 focus:ring-teal-12 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-teal-12 dark:focus:ring-teal-12 md:max-h-[500px]"
						rows={report_content.answers.length}
					>
						{formatAnswers(report_content.answers)}
					</textarea>
				</div>
			{/each}
		</div>
	{:else}
		<div>You have not generated a report</div>
	{/if}
</div>

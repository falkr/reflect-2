<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import { page } from '$app/stores';
	import { Badge, Button, ButtonGroup } from 'flowbite-svelte';
	import { DownloadSolid, FileCirclePlusSolid } from 'flowbite-svelte-icons';
	import { onMount } from 'svelte';
	import toast from 'svelte-french-toast';
	import StructuredReport from './StructuredReport.svelte';

	export let numberOfReflectionsInUnit: number;
	export let data: Data;
	const unitId = $page.params.unit;

	let reportData: any;

	let unit = data.units.find((unit) => unit.id === parseInt(unitId.slice(4)));

	onMount(async () => {
		await fetchReportData(unit);
	});

	async function fetchReportData(unit: any) {
		try {
			const response = await fetch(
				`${PUBLIC_API_URL}/report?course_id=${unit.course_id}&unit_id=${unit.id}&course_semester=${unit.course_semester}`,
				{
					credentials: 'include'
				}
			);
			if (!response.ok) {
				throw new Error('Failed to fetch report data');
			}
			reportData = await response.json();
		} catch (error) {
			console.error('Error fetching report data:', error);
		}
	}

	let isGenerating = false;

	async function generateReport() {
		isGenerating = true;
		const response = await fetch(`${PUBLIC_API_URL}/generate_report`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				unit_id: unit?.id,
				course_id: unit?.course_id,
				course_semester: unit?.course_semester
			})
		});

		if (!response.ok) {
			toast.error('Failed to generate report');
		} else {
			toast.success('Report generated successfully', {
				iconTheme: {
					primary: '#36786F',
					secondary: '#FFFFFF'
				}
			});
			await fetchReportData(unit);
		}
		isGenerating = false;
	}

	/**
	 * Function to download a report.
	 * If `data` and `data.course` are true, it opens a new window to download the report.
	 * The URL includes query parameters for `course_id`, `unit_id` and `course_semester`.
	 * If `data` or `data.course` is false, it gives a toast error
	 */
	function downloadReport() {
		if (data && data.course) {
			toast.success('Downloading report', {
				iconTheme: {
					primary: '#36786F',
					secondary: '#FFFFFF'
				}
			});
			const courseId = encodeURIComponent(data.course.id);
			const unitIdEncoded = encodeURIComponent(unitId.slice(4));
			const courseSemester = encodeURIComponent(data.course.semester);

			const downloadUrl = `${PUBLIC_API_URL}/download?course_id=${courseId}&unit_id=${unitIdEncoded}&course_semester=${courseSemester}`;
			window.open(downloadUrl);
		} else {
			toast.error('An error occurred while downloading the report');
		}
	}
</script>

<div class="mt-12 w-full flex flex-col items-center mb-16">
	<div class="flex w-4/5 items-center flex-wrap gap-4">
		<ButtonGroup>
			<Button
				on:click={generateReport}
				disabled={isGenerating || numberOfReflectionsInUnit <= 0}
				class="focus:dark:outline-none dark:outline-none dark:bg-gray-900 dark:text-white text-sm md:text-xs relative"
			>
				<FileCirclePlusSolid class="w-4 h-4 mr-2" />
				{#if isGenerating}
					Generating...
				{:else}
					Generate new report
				{/if}
			</Button>
			<Button
				class="focus:dark:outline-none dark:outline-none dark:bg-gray-900 dark:text-white text-sm md:text-xs"
				on:click={downloadReport}
				disabled={isGenerating || numberOfReflectionsInUnit <= 0 || !reportData}
			>
				<DownloadSolid class="w-4 h-4 mr-2" />
				Download report
			</Button>
		</ButtonGroup>
		{#if reportData && reportData.number_of_answers < numberOfReflectionsInUnit}
			<Badge large color="yellow" class="rounded-lg h-6 my-1 md:m-0"
				>+{numberOfReflectionsInUnit - reportData.number_of_answers} reflections since last report</Badge
			>
		{/if}
	</div>
	<div class="w-4/5 mt-8">
		{#if numberOfReflectionsInUnit <= 0}
			<h1 class="text-gray-500 dark:text-white mt-2">You have no reflections for this unit.</h1>
		{:else if isGenerating}
			<p class="text-gray-500 dark:text-white mt-2">Generating report...</p>
		{:else if (reportData && reportData.number_of_answers === 0) || !reportData}
			<h1 class="text-gray-500 dark:text-white mt-2">No report is generated for this unit yet.</h1>
		{:else if reportData && reportData.report_content}
			<StructuredReport {reportData} unitName={unit?.title} />
		{/if}
	</div>
</div>

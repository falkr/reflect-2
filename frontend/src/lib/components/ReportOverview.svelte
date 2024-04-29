<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import { page } from '$app/stores';
	import { Button, ButtonGroup } from 'flowbite-svelte';
	import { DownloadSolid, FileCirclePlusSolid } from 'flowbite-svelte-icons';
	import { onMount } from 'svelte';
	import toast from 'svelte-french-toast';
	import StructuredReport from './StructuredReport.svelte';
	import ReflectionsBadge from './ReflectionsBadge.svelte';

	export let numberOfReflectionsInUnit: number;
	export let data: Data;
	export let unit_number: number;
	const unitId = $page.params.unit;

	let reportData: ReportType;
	let unitTag = '';
	let totalReflections = 0;
	let reflectionsSinceLastReport = 0;
	let isGenerating = false;

	let unit = data.units?.find((u) => u.id === parseInt(unitId.slice(4)));

	$: if (unit) {
		reflectionsSinceLastReport = unit.reflections_since_last_report ?? 0;
		totalReflections = unit.reflections ? new Set(unit.reflections.map((r) => r.user_id)).size : 0;
		unitTag = isUnitAvailable(unit) ? 'ready' : 'notAvailable';
	}

	function isUnitAvailable(unit: Unit) {
		const date = new Date();
		const stringDate = date.toISOString().split('T')[0];
		return unit.date_available && unit.date_available.toString() <= stringDate;
	}

	onMount(() => {
		if (unit) {
			fetchReportData(unit).catch((error) => {
				console.error('Error fetching report data:', error);
				toast.error('Failed to load initial report data.');
			});
		}
	});

	async function fetchReportData(unit: Unit) {
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

	async function generateReport() {
		isGenerating = true;
		try {
			const response = await fetch(`${PUBLIC_API_URL}/generate_report`, {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					unit_id: unit?.id,
					course_id: unit?.course_id,
					course_semester: unit?.course_semester
				})
			});
			if (!response.ok) throw new Error('Failed to generate report');
			reflectionsSinceLastReport = 0;
			toast.success('Report generated successfully', {
				iconTheme: { primary: '#36786F', secondary: '#FFFFFF' }
			});
			if (unit) await fetchReportData(unit);
		} catch (error) {
			toast.error('Failed to generate report');
		} finally {
			isGenerating = false;
		}
	}

	function downloadReport() {
		if (!data || !data.course) {
			toast.error('Data is incomplete, cannot download the report.');
			return;
		}
		const downloadUrl = `${PUBLIC_API_URL}/download?course_id=${encodeURIComponent(data.course.id)}&unit_id=${encodeURIComponent(unitId.slice(4))}&course_semester=${encodeURIComponent(data.course.semester)}`;
		window.open(downloadUrl);
		toast.success('Downloading report...', {
			iconTheme: { primary: '#36786F', secondary: '#FFFFFF' }
		});
	}
</script>

<div class="mt-12 w-full flex flex-col items-center mb-16">
	<div class="flex w-4/5 items-center flex-wrap gap-4">
		<ButtonGroup>
			<Button
				id="generateReportButton"
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
				id="downloadReportButton"
				disabled={isGenerating ||
					numberOfReflectionsInUnit <= 0 ||
					reportData?.report_content?.length == 0}
			>
				<DownloadSolid class="w-4 h-4 mr-2" />
				Download report
			</Button>
		</ButtonGroup>
		<ReflectionsBadge
			reflectionsSinceLastReport={reflectionsSinceLastReport || 0}
			{totalReflections}
			{unitTag}
		/>
	</div>
	<div class="w-4/5 mt-8">
		{#if numberOfReflectionsInUnit <= 0}
			<h1 class="text-gray-500 dark:text-white mt-2">You have no reflections for this unit.</h1>
		{:else if isGenerating}
			<p class="text-gray-500 dark:text-white mt-2">Generating report...</p>
		{:else if (reportData && reportData.number_of_answers === 0) || !reportData}
			<h1 class="text-gray-500 dark:text-white mt-2">No report is generated for this unit yet.</h1>
		{:else if reportData && reportData.report_content}
			<StructuredReport {reportData} {unit_number} unitName={unit?.title} />
		{/if}
	</div>
</div>

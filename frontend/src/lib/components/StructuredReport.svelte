<script lang="ts">
	import { AccordionItem, Accordion } from 'flowbite-svelte';

	export let reportData: ReportType;
	export let unitName: string | undefined;
	export let unit_number: number;

	const reportSections = reportData ? Object.entries(reportData.report_content) : [];

	if (reportSections.length > 1) {
		reportSections.unshift(reportSections.pop() as [string, any]);
	}
</script>

<!-- The StructuredReport component displays the report for a unit in a structured way with accordions. -->
{#if reportData && reportData.report_content}
	<h1 class="text-xl font-semibold text-gray-600 dark:text-white">
		Report for unit {unit_number} - {unitName}
	</h1>
	<h2 class="text-gray-500 dark:text-white mt-2">
		Please note, this report was generated using AI and may contain errors or inaccuracies.
	</h2>

	<div class="leading-relaxed text-gray-500 dark:text-white mt-2">
		{#each reportSections as [section, content]}
			<div class="mt-6">
				<p class="text-[22px]">{section}</p>
				<Accordion flush id="categoryAccordion">
					{#if typeof content === 'object' && content !== null}
						{#each Object.entries(content) as [topic, responses]}
							{#if Array.isArray(responses) && responses.length > 0}
								<AccordionItem>
									<span slot="header">{topic}</span>
									{#each responses as response}
										<p>- {response}</p>
									{/each}
								</AccordionItem>
							{/if}
						{/each}
					{:else}
						<p>{content}</p>
					{/if}
				</Accordion>
			</div>
		{/each}
	</div>
{/if}

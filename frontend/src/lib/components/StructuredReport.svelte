<script lang="ts">
	import { AccordionItem, Accordion } from 'flowbite-svelte';

	export let reportData: ReportData;
	export let unitName: string | undefined;
</script>

{#if reportData && reportData.report_content}
	<h1 class="text-xl font-semibold text-gray-600 dark:text-white">
		Report for unit {reportData.unit_id} - {unitName}
	</h1>
	<h2 class="text-gray-500 dark:text-white mt-2">
		Please note, this report was generated using AI and may contain errors or inaccuracies.
	</h2>

	<div class="leading-relaxed text-gray-500 dark:text-white mt-2">
		{#each Object.entries(reportData.report_content) as [section, content]}
			<div class="mt-6">
				<p class="text-[22px]">{section}</p>
				<Accordion flush>
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

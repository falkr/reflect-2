<script lang="ts">
	import CourseOverview from '$lib/components/CourseOverview.svelte';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	export let data: Data;
	export let units: Unit[];
	$: units = data.units;
</script>

<Breadcrumb
	breadcrumbItems={[
		{
			label: data.course_name
		}
	]}
/>
<CourseOverview {data} {units} />

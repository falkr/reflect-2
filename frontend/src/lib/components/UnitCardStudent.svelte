<script lang="ts">
	import { Button, Card } from 'flowbite-svelte';
	import { goto, invalidate } from '$app/navigation';
	import { browser } from '$app/environment';
	import { PUBLIC_API_URL } from '$env/static/public';
	import toast from 'svelte-french-toast';

	export let unitData: Unit;
	export let status: string;
	export let data: Data;

	function reformatDate(isoDateString: Date): string {
		const [year, month, day] = isoDateString.toString().split('-');
		return `${day}.${month}.${year}`;
	}

	function gotoReflection() {
		goto(`${window.location.pathname}/${unitData.id}`, { replaceState: false });
	}

	async function declineUnit() {
		const questions = ['1', '2'];

		//Parse question_id to numbers
		let questions_num = questions.map(function (item) {
			return parseInt(item.toString());
		});

		let promises = [];

		for (let index = 0; index < questions.length; index++) {
			//Sends #question_id reflections to backend
			promises.push(
				fetch(`${PUBLIC_API_URL}/reflection`, {
					method: 'POST',
					credentials: 'include',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						body: '',
						user_id: data.user.uid,
						unit_id: unitData.id,
						question_id: questions_num[index]
					})
				})
			);
		}

		Promise.all(promises)
			.then(() => {
				if (browser) {
					invalidate('app:layoutUser').then(() => {
						goto(`/courseview/${data.course.semester}/${data.course.id}`);
					});
				}
			})
			.then(() => {
				toast.success('Unit declined', {
					iconTheme: {
						primary: '#36786F',
						secondary: '#FFFFFF'
					}
				});
			});
	}
</script>

<Card class="h-36 lg:max-w-96 md:max-w-80 max-w-96 sm:p-4 mb-4 ml-0 dark:bg-gray-800">
	<div class="relative">
		<h2 class="text-xl text-gray-900 dark:text-white font-bold">{unitData.title}</h2>
		<p class="text-gray-800 dark:text-gray-300">
			Unit {unitData.unit_number} - {reformatDate(unitData.date_available)}
		</p>
	</div>
	<div class="pt-3 space-x-6 flex">
		{#if status === 'available'}
			<Button
				on:click={gotoReflection}
				class="bg-teal-13 hover:bg-teal-10 dark:bg-blue-700 dark:hover:bg-blue-600"
				size="sm">Start reflection</Button
			>
			<Button
				on:click={declineUnit}
				color="alternative"
				class="box-border border-red-700 border-2 py-2 px-4 text-red-700 dark:text-white dark:border-red-700 dark:hover:bg-red-700 dark:hover:border-red-700"
			>
				Decline unit
			</Button>
		{:else if status === 'unavailable'}
			<Button color="alternative" size="sm">Not available yet</Button>
		{:else if status === 'declined'}
			<Button color="alternative" size="sm">Declined</Button>
		{:else}
			<Button color="alternative" size="sm">Reflection submitted</Button>
		{/if}
	</div>
</Card>

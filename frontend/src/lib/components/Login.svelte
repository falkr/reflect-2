<script>
	import { PUBLIC_API_URL } from '$env/static/public';
	import { LogInIcon } from 'svelte-feather-icons';
	export function redirect() {
		location.href = `${PUBLIC_API_URL}/login`;
	}
</script>

<head>
	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="description" content="" />
	<title>Reflection</title>
	<link
		rel="stylesheet"
		href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css"
	/>
</head>

<main class="w-100 h-100% m-auto flex justify-center">
	<div class="mt-[17%] flex flex-col items-center justify-center">
		<h3 class="mb-4">NTNU Reflection</h3>
		<div class="flex justify-center">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				version="1.1"
				xmlns:dc="http://purl.org/dc/elements/1.1/"
				xmlns:xl="http://www.w3.org/1999/xlink"
				viewBox="230 135 500 285"
				width="60"
			>
				<defs />
				<g
					id="Canvas_1"
					fill="none"
					stroke="none"
					fill-opacity="1"
					stroke-opacity="1"
					stroke-dasharray="none"
				>
					<title>Canvas 1</title>
					<g id="Canvas_1_Layer_2">
						<title>Layer 2</title>
						<g id="Line_2">
							<path
								d="M 240 341 C 266.664 350.6657 293.336 370.16665 320 370 C 346.664 369.83335 373.336 340 400 340 C 426.664 340 453.336 370 480 370 C 506.664 370 533.336 340 560 340 C 586.664 340 613.336 370 640 370 C 666.664 370 693.336 349.999 720 340"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="19"
							/>
						</g>
						<g id="Line_7">
							<path
								d="M 240 381 C 266.664 390.6657 293.336 410.16665 320 410 C 346.664 409.83335 373.336 380 400 380 C 426.664 380 453.336 410 480 410 C 506.664 410 533.336 380 560 380 C 586.664 380 613.336 410 640 410 C 666.664 410 693.336 389.999 720 380"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="19"
							/>
						</g>
						<g id="Line_14">
							<line
								x1="617.5"
								y1="286.5"
								x2="688.5"
								y2="244.5"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="18"
							/>
						</g>
						<g id="Line_17">
							<line
								x1="535.5"
								y1="218.5"
								x2="560.5"
								y2="146.5"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="18"
							/>
						</g>
						<g id="Line_18">
							<line
								x1="428"
								y1="218.5"
								x2="403"
								y2="144.5"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="18"
							/>
						</g>
						<g id="Line_19">
							<line
								x1="342.5"
								y1="286.5"
								x2="276.5"
								y2="244.5"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="18"
							/>
						</g>
						<g id="Line_20">
							<path
								d="M 360 350.5 C 366.5 307.5 407 250.5 480 250 C 553 249.5 589.5 306.5 600 350.5"
								stroke="black"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="18"
							/>
						</g>
					</g>
				</g>
			</svg>
		</div>

		<button type="button" class="p-3 border rounded-lg text-white bg-[#316CF4] mt-5 flex flex-row items-center justify-evenly hover:opacity-90" on:click={redirect}>
			<div class="mr-1.5">
				<LogInIcon size="18"/>
			</div>
			<div>Login via Feide</div>
		</button>
		<div />
	</div>
</main>


# Frontend

## Requirements:

- [Node + npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

Frontend is developed using sveltekit. The application uses client-side for fetching and requesting data.
The project uses some installed frameworks to make life easier.

### [Tailwind CSS](https://tailwindcss.com/)

The CSS library used for styling the pages and components. Tailwind is easy to pick up and learn, and comes with great documentation. Tailwind is also fully integreated with the components library used in the procject, Svelte Flowbite, meaning you can easily style the finished components how you like.

### [Flowbite Svelte](https://flowbite-svelte.com/)

Flowbite svelte is a components library that offers styled components. The components are easy to modify, and comes with alot of functionality. This saves the project from containing alot of boilerplate code and self-made components. The navbar used in the application is an example of this.

### [Felte](https://v0.felte.dev/docs)

Felte is a framework for handling forms in Svelte. Error handling in forms, aswell as handling form submission is done using Felte in the project. All the form-handling is done client side.

# Setup & running

## Environment:

`.env` is not commited to this repo because of security, so this file has to be created.

**Both frontend and backend folders includes a `.env.template` file. This file contains the variables that has to be set in the new `.env` file.**

For the **`frontend`** folder, there is no need to add any more variables than the ones already in the `.env.template` file.

## Running Frontend:

To run the frontend, you have to install the dependencies and run the dev server. This can be done by running the following commands:

```bash
cd frontend
npm install
npm run dev

# Running at 127.0.0.1:5173
```

## Testing frontend:

This project uses Vite for testing. This will also give you a coverage report. To run the tests, run the following command:

```bash
cd frontend
npm run test:coverage
```
